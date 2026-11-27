# Checklist de Entrega — PadelUrban (E2 UF2405)

Leyenda: ✅ Prueba automatizada superada · ✔️ Verificado manualmente · ⚠️ Pendiente de verificación manual

## Criterio 1: Modelos y POO (2.5 puntos)

| Requisito | Implementación | Evidencia |
|---|---|---|
| Modelo `Pista` con `nombre`, `techada`, `activa` | `reservas/models.py` — `class Pista` | ✅ `test_str_modelos` |
| Modelo `Reserva` con `usuario`, `pista`, `fecha`, `hora_inicio`, `hora_fin` | `reservas/models.py` — `class Reserva` | ✅ `test_duracion_minutos` |
| `ForeignKey` con `on_delete=CASCADE` en ambas FK | `reservas/models.py` líneas `usuario`, `pista` | Inspección de ambos campos en `Reserva` |
| `__str__` en `Pista` y `Reserva` | Ambas clases en `models.py` | ✅ `test_str_modelos` |
| `duracion_minutos()` en `Reserva` | `def duracion_minutos(self) -> int` | ✅ `test_duracion_minutos` (90 min) |
| `clean()` con `hora_fin > hora_inicio` | `Reserva.clean()` | ✅ `test_horarios_invalidos_fallan_full_clean` |
| `clean()` con anti-solapamiento | `Reserva.clean()` filtro ORM | ✅ `test_solapamientos_fallan_full_clean` |
| Reservas consecutivas permitidas | `hora_inicio__lt`, `hora_fin__gt` (desigualdad estricta) | ✅ `test_reservas_consecutivas_permitidas` |
| Edición sin conflicto consigo misma | `.exclude(pk=self.pk)` | ✅ `test_edicion_sin_conflicto_consigo_misma` |
| Orden cronológico por `fecha`, `hora_inicio` | `Meta.ordering` | ✅ `test_listado_cronologico_y_diferenciacion_propias` |
| `Pista` y `Reserva` registradas en `/admin/` | `reservas/admin.py` | ✔️ Verificado en navegador |

## Criterio 2: Control de Accesos (2.5 puntos)

| Requisito | Implementación | Evidencia |
|---|---|---|
| Registro de vecinos con `UserCreationForm` | `reservas/views.py` — `def registro` | ✅ `test_registro_valido_y_password_hasheada` |
| Validación de contraseñas de Django | `AUTH_PASSWORD_VALIDATORS` en `settings.py` | ✅ `test_registro_contrasenas_invalidas` |
| Contraseña almacenada como hash PBKDF2 | `create_user()` de Django | ✅ `test_registro_valido_y_password_hasheada` |
| Usuario duplicado rechazado | `UserCreationForm` | ✅ `test_registro_usuario_duplicado` |
| Login con `LoginView` en `/login/` | `reservas/urls.py` | ✅ `test_login_correcto_e_incorrecto` |
| Logout mediante POST en `/logout/` | `LogoutView` de Django (POST) | ✅ `test_logout_post` |
| `@login_required` en `/reservas/`, `/reservas/nueva/`, `/reservas/<id>/cancelar/` | `reservas/views.py` | ✅ `test_get_cancelar_sin_borrado_y_acceso_anonimo_bloqueado` |
| Redirección a `/login/` para anónimos | `LOGIN_URL = '/login/'` | ✅ `test_bloqueo_anonimo_reservas_y_raiz` |
| Bloqueo temporal tras 5 fallos (django-axes, 429) | `config/settings.py`, `AXES_FAILURE_LIMIT=5` | ✅ `test_bloqueo_temporal_axes_login_admin_y_proxy` |
| Recuperación tras enfriamiento de 15 min | `AXES_COOLOFF_TIME=timedelta(minutes=15)` | ✅ `test_recuperacion_tras_enfriamiento_axes` |

## Criterio 3: Lógica de Reservas (2.0 puntos)

| Requisito | Implementación | Evidencia |
|---|---|---|
| Asignación automática de `request.user` | `Reserva(usuario=request.user)` antes de `form.is_valid()` | ✅ `test_asignacion_automatica_y_resistencia_suplantacion` |
| Imposible reservar en nombre de tercero por POST | El campo `usuario` no está en el formulario | ✅ `test_asignacion_automatica_y_resistencia_suplantacion` |
| Solo pistas activas en el formulario | `Pista.objects.filter(activa=True)` en `ReservaForm` | ✅ `test_consecutivas_validas_y_rechazo_pista_inactiva` |
| Cancelación exclusiva de reservas propias | `if reserva.usuario != request.user: return HttpResponseForbidden(...)` | ✅ `test_cancelacion_propia_y_bloqueo_ajena` |
| GET en `/cancelar/` no borra datos (`405`) | `@require_POST` | ✅ `test_get_cancelar_sin_borrado_y_acceso_anonimo_bloqueado` |
| Errores de horario/solapamiento sin guardar | `form.is_valid()` llama a `full_clean()` → `clean()` | ✅ `test_horarios_invalidos_y_solapamiento_no_guardan` |
| Dos pistas iniciales disponibles en `/admin/` | `reservas/fixtures/pistas_iniciales.json` | ✔️ Verificado con `loaddata` |

## Criterio 4: Plantillas e Interfaz MVT (1.5 puntos)

| Requisito | Implementación | Evidencia |
|---|---|---|
| Herencia de plantillas con `base.html` | `{% extends 'base.html' %}` en todas | ✔️ Verificado en navegador |
| Bootstrap 5 (CDN) | `base.html` — `bootstrap@5.3.3` | ✔️ Verificado en navegador |
| Mensajes flash | `{% if messages %}` en `base.html` | ✔️ Verificado en navegador (registro, reserva, cancelación) |
| `{% csrf_token %}` en todos los formularios POST | `registro.html`, `login.html`, `base.html` (logout), `reserva_form.html`, `reservas_list.html` | ✅ `test_post_sin_csrf_rechazado` |
| Listado cronológico con diferenciación de reservas propias | `reservas_list.html` — `pu-reserva-card--propia`, badge «Tu reserva» | ✔️ Verificado en navegador |
| Estado vacío con llamada a reservar | `reservas_list.html` — bloque `{% else %}` | ✔️ Verificado en navegador |
| Botón de cancelación solo en reservas propias | `{% if reserva.usuario == user %}` en plantilla | ✔️ Verificado en navegador |
| Confirmación de cancelación | `onsubmit="return confirm(...)"` en plantilla | ✔️ Verificado en navegador |
| Interfaz responsive sin desbordamiento | CSS de tarjetas en rejilla + Bootstrap | ✔️ Verificado en navegador a 390px y 1440px |

## Criterio 5: Vibe Coding y Defensa (1.5 puntos)

| Requisito | Estado |
|---|---|
| Prompts de cada fase documentados | ✔️ [`docs/prompts.md`](prompts.md) |
| Guion de defensa oral (3 min) | ✔️ [`docs/defensa_3_minutos.md`](defensa_3_minutos.md) |
| Comprensión y justificación del código | ⚠️ Pendiente — defensa individual presencial |

## Verificación del Checklist del Enunciado

| Ítem | Estado | Evidencia |
|---|---|---|
| Acceso anónimo bloqueado: `/reservas/` → `/login/` | ✅ | `test_bloqueo_anonimo_reservas_y_raiz` |
| Registro funcional (crear vecino e iniciar sesión) | ✅ | `test_registro_valido_y_password_hasheada` + ✔️ navegador |
| Asignación automática a `request.user` | ✅ | `test_asignacion_automatica_y_resistencia_suplantacion` |
| Validación de solapamiento con error visible | ✅ | `test_solapamientos_fallan_full_clean` + `test_horarios_invalidos_y_solapamiento_no_guardan` |
| Validación horaria (fin no anterior a inicio) | ✅ | `test_horarios_invalidos_fallan_full_clean` |
| Privacidad en borrado (no cancelar reservas ajenas) | ✅ | `test_cancelacion_propia_y_bloqueo_ajena` |
| Migraciones en SQLite y al menos 2 pistas en `/admin/` | ✔️ | `loaddata pistas_iniciales` + superusuario |
