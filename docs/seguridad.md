# Revisión de Seguridad — PadelUrban

## 1. Hallazgos y Correcciones Aplicadas
1. **`SECRET_KEY` codificada en `config/settings.py`:** Se externalizó mediante `DJANGO_SECRET_KEY`. En producción (`DJANGO_ENV=production`) el proyecto exige la clave y `DJANGO_ALLOWED_HOSTS`. Con `DEBUG=False` en desarrollo también exige la clave.
2. **Uso innecesario de `|safe` en `registro.html`:** Se eliminó `|safe` de `{{ field.help_text }}`, manteniendo el autoescape activo por defecto en todas las plantillas y sin `mark_safe` ni consultas SQL crudas (`.raw()`, `.extra()`).
3. **Fuerza bruta en login (`/login/` y `/admin/`):** Se integró `django-axes==9.1.0` (fijado en `requirements.txt`) con almacenamiento en base de datos, bloqueo temporal tras **5 intentos fallidos** por combinación `(username, ip_address)`, enfriamiento de **15 minutos**, respuesta **HTTP 429** y plantilla en español (`reservas/templates/reservas/lockout.html`). Solo se lee `REMOTE_ADDR` (`AXES_IPWARE_META_PRECEDENCE_ORDER = ('REMOTE_ADDR',)`), ignorando cabeceras proxy arbitrarias.
4. **Separación Desarrollo (HTTP) vs Producción (HTTPS):** En desarrollo (`DJANGO_ENV=development`), `DEBUG=True`, `ALLOWED_HOSTS=['localhost', '127.0.0.1']` y sin redirección HTTPS. En producción (`DJANGO_ENV=production`), `DEBUG=False`, `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, `CSRF_COOKIE_HTTPONLY=True` y HSTS (`SECURE_HSTS_SECONDS=31536000`).

## 2. Controles Verificados
- **Contraseñas y sesiones:** `UserCreationForm` con validadores de Django, hash PBKDF2, `LogoutView` exclusivo por `POST` con invalidación de sesión (`_auth_user_id` eliminado).
- **Permisos y CSRF:** `@login_required` en todas las vistas de `reservas`, asignación de `usuario=request.user` previa a `clean()`, `reserva_cancelar` solo `POST` con bloqueo `403` ante terceros, y rechazo `403` verificado con `Client(enforce_csrf_checks=True)`.
- **Entradas maliciosas:** Autoescape de plantillas verificado con carga `<script>`, redirecciones `next` externas bloqueadas por `LoginView` y mensajes de error de login genéricos que no revelan si una cuenta existe.

## 3. Desbloqueo Administrativo (`django-axes`)
- **Por consola:**
  - Desbloquear un usuario: `.\.venv\Scripts\python.exe manage.py axes_reset_username <usuario>`
  - Desbloquear una IP: `.\.venv\Scripts\python.exe manage.py axes_reset_ip <ip>`
  - Reiniciar todos los bloqueos: `.\.venv\Scripts\python.exe manage.py axes_reset`
- **Desde `/admin/`:** Acceder como superusuario a **Axes → Access attempts** y eliminar el registro del intento bloqueado.

## 4. Configuración de Entorno (Reproducible)
Ver plantilla sin secretos en `.env.example`. Para producción, definir variables de entorno:
- `DJANGO_ENV=production`
- `DJANGO_SECRET_KEY` (cadena aleatoria de al menos 50 caracteres)
- `DJANGO_ALLOWED_HOSTS` (lista separada por comas de dominios reales)
`.gitignore` excluye `.env`, `.env.*` (excepto `.env.example`), `*.key`, `*.pem` y `db.sqlite3`.

## 5. Revisión Inicial de Seguridad (histórico)
- `manage.py check`: **0 incidencias**.
- `manage.py test reservas`: **25/25 pruebas superadas (`OK`)**, incluyendo bloqueo temporal (`429`) en `/login/` y `/admin/login/`, resistencia a cabeceras proxy falsas, bloqueo de `next` externo, errores genéricos de login, escape HTML y CSRF real.
- `manage.py check --deploy` (con `DJANGO_ENV=production`): sin advertencias de HTTPS/cookies/DEBUG/ALLOWED_HOSTS; únicamente muestra `security.W009` si la `DJANGO_SECRET_KEY` de prueba tiene menos de 50 caracteres (no silenciada).
- `pip-audit -r requirements.txt`: **No known vulnerabilities found**.
- **Limitaciones:** No se configuran dominios reales, certificados TLS ni cabeceras de proxy inverso al no existir despliegue en esta fase.

---

## 6. Verificación de Seguridad y Carga (histórico)

### 6.1 Cierre de aviso de configuración (`--fail-level WARNING`)
- Ejecutado `manage.py check --deploy --fail-level WARNING` con `DJANGO_ENV=production`, `DJANGO_ALLOWED_HOSTS` explícito y `DJANGO_SECRET_KEY` generada temporalmente con `secrets.token_urlsafe(64)` en el entorno del proceso: **0 incidencias (`EXIT 0`)**.
- **Requisitos pendientes del alojamiento (producción):** Definir `DJANGO_ENV=production`, una `DJANGO_SECRET_KEY` aleatoria de al menos 50 caracteres, `DJANGO_ALLOWED_HOSTS` con los dominios reales y servir detrás de HTTPS con terminación TLS.

### 6.2 Alcance de la protección de login (`django-axes`)
- **Pruebas verificadas (`26/26 OK`):** Bloqueo tras 5 fallos (`HTTP 429`) en `/login/` y `/admin/login/`, recuperación tras simular el enfriamiento de 15 minutos (`test_recuperacion_tras_enfriamiento_axes`), no bloqueo de otra cuenta legítima desde la misma IP y rechazo de cabeceras proxy falsas (`HTTP_X_FORWARDED_FOR`).
- **Alcance y limitación:** El bloqueo por combinación `(username, ip_address)` protege cuentas concretas desde una misma IP, pero **no** equivale a protección global contra saturación ni contra ataques distribuidos repartidos entre muchas cuentas o múltiples direcciones IP.

### 6.3 Prueba ligera de carga local (`scripts/prueba_carga_local.py`)
- **Condiciones de prueba:** Servidor temporal `runserver` exclusivo en `127.0.0.1`, base SQLite temporal (`DJANGO_DB_PATH`) eliminada al finalizar, 1 usuario sintético y 5 reservas sintéticas (sin tocar `db.sqlite3` ni cuentas reales). Lecturas autenticadas a `/reservas/` con sesión única reutilizada, verificando contenido real del listado y rechazando redirecciones fuera de `127.0.0.1`.
- **Límites aplicados:** Máx. 100 solicitudes, máx. 5 req/s, máx. 3 simultáneas, máx. 30 s, timeout de 3 s y parada anticipada tras 3 errores `5xx`/timeouts consecutivos.
- **Métricas observadas:**
  - Solicitudes realizadas: **100**
  - Duración total: **19.81 s** (~5.05 req/s)
  - Códigos HTTP: **`200`: 100** (0 errores)
  - Latencia media: **18.72 ms**
  - Percentil 95 (P95): **35.22 ms**
- **Interpretación y pendientes de despliegue:** Estos resultados corresponden únicamente a un entorno local de desarrollo (`runserver` + SQLite temporal) y **no** representan capacidad de producción ni resistencia frente a DDoS. En producción quedan pendientes: servidor WSGI/ASGI, límites de peticiones y conexiones (rate limiting), timeouts de red y protección perimetral del proveedor.

## 7. Verificación de Entrega (27/11/2026)

- `manage.py check` y `manage.py check --deploy --fail-level WARNING` sin avisos. Se usó una clave aleatoria temporal para el chequeo de producción.
- Suite completa: 26/26 pruebas superadas. `pip check` no detectó dependencias rotas.
- `pip-audit -r requirements.txt` falló al preparar su entorno auxiliar. El reintento con `--disable-pip --no-deps` falló al resolver `pypi.org`. La auditoría previa queda como resultado histórico.
- Se conservaron las mediciones previas de carga local.
