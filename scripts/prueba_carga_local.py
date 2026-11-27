"""Prueba ligera de carga local sobre servidor y SQLite temporales en 127.0.0.1."""

import concurrent.futures
import http.cookiejar
import math
import os
import re
import secrets
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PYTHON_EXE = sys.executable

MAX_REQUESTS = 100
MAX_RPS = 5.0
MAX_CONCURRENCY = 3
MAX_DURATION_SEC = 30.0
REQUEST_TIMEOUT_SEC = 3.0
MAX_CONSECUTIVE_ERRORS = 3


class LocalOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Rechaza cualquier redirección fuera de 127.0.0.1."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlparse(urllib.parse.urljoin(req.full_url, newurl))
        if parsed.hostname not in (None, '127.0.0.1'):
            raise ValueError(f'Redirección rechazada fuera de 127.0.0.1: {parsed.hostname}')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def main() -> int:
    port = get_free_port()
    base_url = f'http://127.0.0.1:{port}'

    with tempfile.TemporaryDirectory(prefix='padelurban_carga_') as tmp_dir:
        db_path = Path(tmp_dir) / 'carga_temp.sqlite3'
        env = os.environ.copy()
        env['DJANGO_ENV'] = 'development'
        env['DJANGO_DB_PATH'] = str(db_path)
        env['DJANGO_SECRET_KEY'] = secrets.token_urlsafe(64)

        subprocess.run(
            [PYTHON_EXE, 'manage.py', 'migrate', '--noinput'],
            cwd=BASE_DIR,
            env=env,
            check=True,
            stdout=subprocess.DEVNULL,
        )

        # Datos sintéticos temporales
        synth_pass = secrets.token_urlsafe(16)
        seed_code = (
            "from datetime import date, time\n"
            "from django.contrib.auth import get_user_model\n"
            "from reservas.models import Pista, Reserva\n"
            "U = get_user_model()\n"
            f"u = U.objects.create_user(username='carga_vecino', password={synth_pass!r})\n"
            "p1 = Pista.objects.create(nombre='Pista Carga 1', techada=True, activa=True)\n"
            "p2 = Pista.objects.create(nombre='Pista Carga 2', techada=False, activa=True)\n"
            "for i in range(5):\n"
            "    Reserva.objects.create(usuario=u, pista=p1 if i % 2 == 0 else p2, "
            "fecha=date(2026, 12, 20), hora_inicio=time(9 + i, 0), hora_fin=time(10 + i, 0))\n"
        )
        subprocess.run(
            [PYTHON_EXE, 'manage.py', 'shell', '-c', seed_code],
            cwd=BASE_DIR,
            env=env,
            check=True,
            stdout=subprocess.DEVNULL,
        )

        server = subprocess.Popen(
            [PYTHON_EXE, 'manage.py', 'runserver', '--noreload', f'127.0.0.1:{port}'],
            cwd=BASE_DIR,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            # Esperar arranque del servidor temporal
            ready = False
            for _ in range(30):
                if server.poll() is not None:
                    raise RuntimeError('El servidor temporal terminó inesperadamente.')
                try:
                    with urllib.request.urlopen(f'{base_url}/login/', timeout=1.0) as r:
                        if r.status == 200:
                            ready = True
                            break
                except Exception:
                    time.sleep(0.25)
            if not ready:
                raise RuntimeError('Tiempo agotado esperando al servidor temporal.')

            # Sesión autenticada única (sin repetir login en cada petición)
            cj = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(cj),
                LocalOnlyRedirectHandler(),
            )
            with opener.open(f'{base_url}/login/', timeout=REQUEST_TIMEOUT_SEC) as r:
                login_html = r.read().decode('utf-8', 'ignore')
            m = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', login_html)
            if not m:
                raise RuntimeError('No se pudo obtener el token CSRF de /login/.')

            payload = urllib.parse.urlencode({
                'csrfmiddlewaretoken': m.group(1),
                'username': 'carga_vecino',
                'password': synth_pass,
            }).encode('utf-8')
            req_login = urllib.request.Request(
                f'{base_url}/login/',
                data=payload,
                headers={'Referer': f'{base_url}/login/'},
            )
            with opener.open(req_login, timeout=REQUEST_TIMEOUT_SEC) as r:
                body_after = r.read().decode('utf-8', 'ignore')
                if r.status != 200 or 'Reservas programadas' not in body_after:
                    raise RuntimeError('El login de la sesión de prueba no llegó al listado.')

            cookie_header = '; '.join(f'{c.name}={c.value}' for c in cj)

            # Ejecución controlada de lecturas autenticadas
            latencies_ms: list[float] = []
            status_counts: dict[str, int] = {}
            errors = 0
            consecutive_errors = 0
            stop_event = threading.Event()
            rate_lock = threading.Lock()
            next_slot = time.monotonic()

            def one_request() -> tuple[str, float, bool]:
                nonlocal next_slot
                with rate_lock:
                    if stop_event.is_set():
                        return ('SKIP', 0.0, False)
                    now = time.monotonic()
                    if now < next_slot:
                        time.sleep(next_slot - now)
                    next_slot = max(now, next_slot) + (1.0 / MAX_RPS)

                if stop_event.is_set():
                    return ('SKIP', 0.0, False)

                req = urllib.request.Request(
                    f'{base_url}/reservas/',
                    headers={'Cookie': cookie_header},
                )
                req_opener = urllib.request.build_opener(LocalOnlyRedirectHandler())
                t0 = time.perf_counter()
                try:
                    with req_opener.open(req, timeout=REQUEST_TIMEOUT_SEC) as resp:
                        html = resp.read().decode('utf-8', 'ignore')
                        elapsed = (time.perf_counter() - t0) * 1000.0
                        if resp.status == 200 and 'Reservas programadas' in html and 'Pista Carga' in html:
                            return ('200', elapsed, False)
                        return (f'{resp.status}_INVALID', elapsed, resp.status >= 500)
                except urllib.error.HTTPError as e:
                    elapsed = (time.perf_counter() - t0) * 1000.0
                    return (str(e.code), elapsed, e.code >= 500)
                except Exception:
                    elapsed = (time.perf_counter() - t0) * 1000.0
                    return ('TIMEOUT_OR_ERR', elapsed, True)

            t_start = time.monotonic()
            sent = 0
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENCY) as pool:
                futures = []
                for _ in range(MAX_REQUESTS):
                    if time.monotonic() - t_start >= MAX_DURATION_SEC or stop_event.is_set():
                        break
                    futures.append(pool.submit(one_request))

                for fut in concurrent.futures.as_completed(futures):
                    if time.monotonic() - t_start >= MAX_DURATION_SEC:
                        stop_event.set()
                    code, lat, is_fail = fut.result()
                    if code == 'SKIP':
                        continue
                    sent += 1
                    status_counts[code] = status_counts.get(code, 0) + 1
                    latencies_ms.append(lat)
                    if is_fail:
                        errors += 1
                        consecutive_errors += 1
                        if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                            stop_event.set()
                    else:
                        consecutive_errors = 0

            total_time = time.monotonic() - t_start
            latencies_ms.sort()
            avg_ms = sum(latencies_ms) / len(latencies_ms) if latencies_ms else 0.0
            p95_idx = max(0, math.ceil(0.95 * len(latencies_ms)) - 1) if latencies_ms else 0
            p95_ms = latencies_ms[p95_idx] if latencies_ms else 0.0

            print(f'SOLICITUDES: {sent}')
            print(f'DURACION_SEG: {total_time:.2f}')
            print(f'RPS_REAL: {sent / total_time:.2f}')
            print(f'CODIGOS_HTTP: {status_counts}')
            print(f'ERRORES: {errors}')
            print(f'LATENCIA_MEDIA_MS: {avg_ms:.2f}')
            print(f'LATENCIA_P95_MS: {p95_ms:.2f}')
            return 0 if errors == 0 and sent > 0 else 1
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()


if __name__ == '__main__':
    raise SystemExit(main())
