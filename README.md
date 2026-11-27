# PadelUrban

Sistema web de reserva de pistas de pádel para la comunidad «Residencial Las Palas». Proyecto de examen E2 — UF2405 (MF0227\_3 / IFCD0112).

## Tecnologías

| Componente | Versión |
|---|---|
| Python | 3.11.9 |
| Django | 5.2.19 |
| django-axes | 9.1.0 |
| asgiref | 3.13.0 |
| sqlparse | 0.6.1 |
| tzdata | 2026.6 |
| Base de datos | SQLite 3 (integrada en Python) |
| CSS | Bootstrap 5.3.3 (CDN) |
| Tipografía | Plus Jakarta Sans (Google Fonts CDN) |

## Instalación desde cero (Windows / PowerShell)

### 1. Requisitos previos

- Python 3.11+ instalado y en el `PATH`
- Acceso a internet para descargar dependencias

### 2. Clonar o descomprimir el proyecto

```powershell
Set-Location -LiteralPath 'D:\Documentos\Trabajo Curso\PadelUrban'  # ajusta la ruta
```

### 3. Crear el entorno virtual e instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Configurar variables de entorno

El proyecto **no carga `.env` automáticamente**. Define las variables en la sesión de PowerShell antes de arrancar:

```powershell
# Desarrollo local (valores mínimos necesarios)
$env:DJANGO_ENV = "development"
# DJANGO_SECRET_KEY es opcional en desarrollo; se usa una clave de desarrollo insegura por defecto
# $env:DJANGO_SECRET_KEY = "clave-aleatoria-aqui"
```

Para producción consulta [.env.example](.env.example) y define obligatoriamente:
- `DJANGO_ENV=production`
- `DJANGO_SECRET_KEY` (cadena aleatoria de al menos 50 caracteres)
- `DJANGO_ALLOWED_HOSTS` (dominios reales separados por comas)

### 5. Aplicar migraciones

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

### 6. Cargar fixture de pistas iniciales

```powershell
.\.venv\Scripts\python.exe manage.py loaddata pistas_iniciales
```

Carga dos pistas: «Pista 1 - Central» (techada) y «Pista 2 - Exterior».

### 7. Crear superusuario para el panel de administración

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

No hay credenciales predeterminadas. Introduce usuario y contraseña cuando se te solicite.

### 8. Arrancar el servidor de desarrollo

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Accede a **http://127.0.0.1:8000/** (redirige a `/reservas/` → `/login/` si no hay sesión) y al panel de administración en **http://127.0.0.1:8000/admin/**.

## Pruebas automatizadas

```powershell
.\.venv\Scripts\python.exe manage.py test reservas
```

La suite contiene **26 pruebas** distribuidas en cuatro clases:

| Clase | Pruebas | Qué cubre |
|---|---|---|
| `PistaYReservaModelTests` | 8 | `duracion_minutos()`, `__str__`, horarios inválidos, solapamientos, consecutivas, distintas pistas/fechas, edición sin conflicto, campos incompletos |
| `AutenticacionTests` | 6 | Registro válido (hash), duplicado, contraseñas inválidas, login correcto/incorrecto, logout POST, bloqueo anónimo |
| `ReservasCRUDTests` | 7 | Listado cronológico, asignación automática de `request.user`, resistencia a suplantación, horarios/solapamientos, pista inactiva, cancelación propia/ajena, GET sin borrado, CSRF real |
| `SeguridadTests` | 5 | Bloqueo temporal django-axes (429), recuperación tras enfriamiento simulado, proxy spoof, redirección `next` externa, errores genéricos de login, escape HTML |

## Funcionalidades principales

- **Registro y autenticación de vecinos:** `UserCreationForm`, login/logout seguros, contraseñas hasheadas con PBKDF2.
- **Protección de acceso:** `@login_required` en todas las vistas de reservas; redirección automática a `/login/` para usuarios anónimos.
- **Catálogo de pistas:** Modelo `Pista` gestionable desde `/admin/`; el formulario solo muestra pistas activas.
- **Reservas:** Asignación automática de `request.user`, validación en `Reserva.clean()` (fin > inicio, anti-solapamiento, consecutivas permitidas, edición sin autoconflicto).
- **Cancelación segura:** Solo el propietario puede cancelar su reserva; terceros reciben `HTTP 403`.
- **Protección contra fuerza bruta:** `django-axes` bloquea temporalmente tras 5 fallos por `(username, ip_address)` durante 15 minutos, con respuesta `HTTP 429` y página en español.
- **CSRF activo:** Todos los formularios POST incluyen `{% csrf_token %}`.

## Documentación

| Documento | Descripción |
|---|---|
| [docs/prompts.md](docs/prompts.md) | Prompts de cada fase y resultados |
| [Mermaid](docs/modelo_er.md) · [SVG](docs/modelo_er.svg) · [PDF](docs/modelo_er.pdf) | Diagrama ER en notación de patas de gallo |
| [docs/requisitos.md](docs/requisitos.md) | Requisitos y criterios de evaluación del examen |
| [docs/seguridad.md](docs/seguridad.md) | Revisión de seguridad, bloqueo de login y prueba de carga local |
| [docs/checklist_entrega.md](docs/checklist_entrega.md) | Checklist de entrega con evidencias por requisito |
| [docs/defensa_3_minutos.md](docs/defensa_3_minutos.md) | Guion de defensa oral (3 minutos) |
