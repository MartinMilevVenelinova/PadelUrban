# Requisitos y Criterios de Evaluación — PadelUrban (E2 UF2405)

## Contexto y Objetivo
- **Prueba:** Evaluación continua E2 — UF2405: Modelo de programación web y bases de datos (MF0227_3 / IFCD0112).
- **Caso práctico:** Sistema Web de Reserva de Pistas de Pádel (**PadelUrban**) para la comunidad "Residencial Las Palas".
- **Stack:** Django (Python) + SQLite3, aplicando POO, arquitectura MVT y control estricto de accesos.

## Requisitos Funcionales (RF)
- **RF-01 — Control de Accesos y Seguridad:** Registro web de vecinos (usuario y contraseña), inicio y cierre de sesión. Ningún usuario anónimo puede acceder al listado de reservas ni solicitar pistas (redirección automática al login).
- **RF-02 — Catálogo de Pistas:** Modelo `Pista` (`nombre`, `techada`: sí/no, `activa`: sí/no), gestionable inicialmente desde `/admin`.
- **RF-03 — Listado de Disponibilidad:** La página principal para usuarios autenticados muestra las reservas ordenadas cronológicamente, diferenciando visualmente las del usuario conectado.
- **RF-04 — Solicitud de Reserva con Asignación Automática:** El formulario solicita únicamente `Pista`, `Fecha`, `Hora de inicio` y `Hora de fin`. La reserva se vincula automáticamente a `request.user`, impidiendo reservar en nombre de terceros.
- **RF-05 — Reglas de Negocio en POO (`clean()`):** En `Reserva.clean()` se valida:
  1. Hora de fin posterior a la hora de inicio.
  2. No solapamiento: la pista no puede estar ocupada en el mismo día y tramo horario.
- **RF-06 — Cancelación Segura:** Un vecino solo puede eliminar/cancelar sus propias reservas; intentar cancelar la de otro propietario debe bloquearse.

## Requisitos Técnicos y de Arquitectura (RT)
- **RT-01 (POO en Django):** Modelos `Pista` y `Reserva` en `models.py` con atributos tipados, `__str__`, `clean()` y método de instancia `duracion_minutos()`.
- **RT-02 (BBDD Relacional):** SQLite3 con `ForeignKey` e integridad referencial `on_delete=models.CASCADE`.
- **RT-03 (Seguridad y Vistas):** Vistas protegidas con `@login_required`, formularios `ModelForm` y protección CSRF (`{% csrf_token %}`).
- **RT-04 (Plantillas y UI):** Arquitectura MVT con `base.html`, Bootstrap 5 (CDN) y mensajes flash.

## Fases de Trabajo
1. **Fase 1:** Preparación del Entorno y Proyecto Django
2. **Fase 2:** Modelado de Datos y POO (`models.py`)
3. **Fase 3:** Control de Accesos y Autenticación
4. **Fase 4:** Formularios y Vistas CRUD Protegidas
5. **Fase 5:** Plantillas HTML con Bootstrap 5

## Criterios de Evaluación (10 Puntos)
| Criterio | Puntuación | Aspectos Evaluados |
| --- | --- | --- |
| Modelos y POO | 2.5 | Clases bien estructuradas, herencia, `ForeignKey`, `__str__`, cálculo de duración y validación anti-solapamiento en `clean()`. |
| Control de Accesos | 2.5 | Registro seguro de vecinos, login/logout operativos, `@login_required` y redirección de usuarios no autenticados. |
| Lógica de Reservas | 2.0 | Asignación automática de `request.user`, tratamiento de errores y bloqueo de borrado a usuarios no propietarios. |
| Plantillas e Interfaz (MVT) | 1.5 | Herencia de plantillas (`base.html`), maquetación limpia en Bootstrap 5, mensajes flash y token CSRF. |
| Vibe Coding y Defensa | 1.5 | Explicación del código generado y justificación técnica en defensa individual (3 min). |

## Lista de Verificación Previa a la Entrega
- [ ] Acceso anónimo bloqueado: `/reservas/` redirige a `/login/` sin sesión.
- [ ] Registro funcional: crear nuevo vecino (ej. `vecino1`) e iniciar sesión.
- [ ] Asignación automática: al crear reserva se asocia a `request.user` sin seleccionarlo en el formulario.
- [ ] Validación de solapamiento: impide reservar la misma pista a la misma hora y muestra error.
- [ ] Validación horaria: impide hora de fin anterior a hora de inicio.
- [ ] Privacidad en borrado: no permite cancelar reservas de otro usuario.
- [ ] BBDD y Superusuario: migraciones aplicadas en SQLite3 y al menos 2 pistas disponibles en `/admin`.
