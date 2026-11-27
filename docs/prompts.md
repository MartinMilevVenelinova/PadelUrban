# Registro de Prompts — PadelUrban

## Fase 1

### Prompt
```text
Lee modeloe2_uf2405.docx como enunciado de referencia. Guarda un resumen fiel de requisitos y criterios de evaluación en docs/requisitos.md para consultarlo en las siguientes fases. No reproduzcas el documento en el chat. Ahora ejecuta únicamente la fase 1 descrita a continuación.

FASE 1 — PadelUrban, examen E2 UF2405.

Prepara en la carpeta actual una aplicación Django con SQLite3 y arquitectura MVT para reservar pistas de pádel. Implementa únicamente el entorno inicial.

Tareas:
1. Comprueba Python y su compatibilidad con una versión estable de Django. Si falta un requisito, detente e indica cómo resolverlo.
2. Crea .venv e instala Django dentro del entorno.
3. Crea el proyecto config en la raíz y la app reservas. Registra la app en INSTALLED_APPS.
4. Mantén SQLite3. Configura LANGUAGE_CODE="es" y TIME_ZONE="Europe/Madrid".
5. Genera requirements.txt con versiones exactas y .gitignore para excluir .venv, cachés, secretos y db.sqlite3, conservando las migraciones.
6. Ejecuta las migraciones iniciales y manage.py check. Comprueba que el servidor responde y muestra la página inicial de Django.
7. Guarda este prompt en docs/prompts.md como «Fase 1», seguido de un resumen breve de resultados y correcciones.

No implementes aún modelos, autenticación, formularios ni plantillas.
```

### Resultados y correcciones
- **Requisitos:** Extraído el resumen de `modeloe2_uf2405.docx` en `docs/requisitos.md`.
- **Entorno:** Verificado Python `3.11.9`, creado `.venv` e instalado `Django==5.2.19` (junto con `asgiref==3.13.0`, `sqlparse==0.6.1`, `tzdata==2026.6`).
- **Proyecto y configuración:** Creado proyecto `config` en la raíz y app `reservas` registrada en `INSTALLED_APPS`, manteniendo SQLite3 y configurando `LANGUAGE_CODE = 'es'` y `TIME_ZONE = 'Europe/Madrid'`.
- **Dependencias y control de versiones:** Generados `requirements.txt` con versiones exactas y `.gitignore` excluyendo `.venv/`, cachés, secretos y `db.sqlite3`, conservando migraciones.
- **Verificación:** Aplicadas las migraciones iniciales (`db.sqlite3`), `manage.py check` sin errores y servidor de desarrollo respondiendo HTTP 200 en `http://127.0.0.1:8000/`.
- **Correcciones durante la ejecución:** En PowerShell 5.1 se sustituyó `&&` por `;` con comprobación `$?`, y tanto la instalación vía `pip` como la prueba de escucha del servidor en puerto local se ejecutaron fuera del sandbox por restricciones de red y sockets.

---

## Diseño ER

### Prompt
```text
PadelUrban — Diseño ER previo a la fase 2.

Consulta docs/requisitos.md y crea docs/modelo_er.md con un diagrama Mermaid ER en notación de patas de gallo:

- Usuario: modelo de autenticación existente de Django. Representa id, username y password (hash gestionado por Django).
- Pista: id, nombre, techada, activa.
- Reserva: id, usuario_id, pista_id, fecha, hora_inicio, hora_fin.

Marca PK, FK y tipos de datos. Cada reserva pertenece obligatoriamente a un usuario y una pista. Cada usuario y cada pista pueden tener cero o muchas reservas. Las dos FK tendrán on_delete=CASCADE.

Explica brevemente las relaciones y estas reglas: fin posterior al inicio y ausencia de solapamientos para una misma pista y fecha. Las reservas consecutivas deben permitirse.

Guarda este prompt en docs/prompts.md bajo «Diseño ER». No programes todavía los modelos.
```

### Resultados
- Creado `docs/modelo_er.md` con el diagrama Mermaid `erDiagram` en notación de patas de gallo (`Usuario`, `Pista`, `Reserva` con PK, FK, tipos de datos y cardinalidad `||--o{`).
- Documentadas las relaciones con `on_delete=CASCADE` y las reglas de validación (`hora_fin > hora_inicio` y anti-solapamiento con desigualdad estricta para permitir reservas consecutivas), sin implementar aún los modelos en `models.py`.

---

## Fase 2

### Prompt
```text
FASE 2 — Modelos y POO de PadelUrban.

Consulta docs/requisitos.md y docs/modelo_er.md. Implementa en reservas/models.py:

Pista:
- nombre: CharField.
- techada y activa: BooleanField.

Reserva:
- usuario: ForeignKey a settings.AUTH_USER_MODEL.
- pista: ForeignKey a Pista.
- Ambas FK con on_delete=models.CASCADE.
- fecha: DateField.
- hora_inicio y hora_fin: TimeField.
- Orden cronológico por fecha y hora_inicio.

Incluye __str__ en ambos modelos y duracion_minutos() en Reserva, calculando minutos enteros.

En Reserva.clean(), llama a super().clean() y valida:
- hora_fin estrictamente posterior a hora_inicio.
- Sin solapamientos para la misma pista y fecha: inicio_existente < fin_nuevo y fin_existente > inicio_nuevo.
- Excluye la propia reserva al editar.
- Maneja campos incompletos sin provocar excepciones inesperadas.
- Muestra errores comprensibles mediante ValidationError.

Registra ambos modelos en /admin. Crea y carga una fixture reutilizable con dos pistas.

Genera y aplica migraciones. Ejecuta manage.py check y pruebas automatizadas de duración, horarios inválidos, solapamientos, reservas consecutivas, distintas pistas/fechas y edición sin conflicto consigo misma. Las pruebas deben ejecutar full_clean().

Actualiza el ER si hubiera diferencias y registra este prompt y resultados en docs/prompts.md como «Fase 2».

No avances a autenticación ni vistas.
```

### Resultados
- Implementados `Pista` y `Reserva` en `reservas/models.py` con `__str__`, `duracion_minutos()`, orden cronológico (`['fecha', 'hora_inicio']`) y validaciones en `clean()` mediante `ValidationError`.
- Registrados ambos modelos en `reservas/admin.py` y creada/cargada la fixture `reservas/fixtures/pistas_iniciales.json` con 2 pistas (`Pista 1 - Central` y `Pista 2 - Exterior`).
- Generada y aplicada `reservas/migrations/0001_initial.py`; `manage.py check` sin incidencias y 8 pruebas unitarias en `reservas/tests.py` (ejecutando `full_clean()`) superadas (`OK`).
- Sin diferencias respecto a `docs/modelo_er.md`.

---

## Fase 3

### Prompt
```text
FASE 3 — Autenticación de PadelUrban.

Consulta docs/requisitos.md y reutiliza el proyecto existente.

Implementa:
- /registro/: alta de vecinos con UserCreationForm de Django, validación de contraseñas y errores visibles.
- /login/: LoginView de Django.
- /logout/: LogoutView mediante POST.
- /reservas/: vista provisional con @login_required, sin implementar todavía el listado ni el CRUD.
- /: redirección a /reservas/.

Configura LOGIN_URL="/login/", LOGIN_REDIRECT_URL="/reservas/" y LOGOUT_REDIRECT_URL="/login/".

Crea las plantillas mínimas necesarias con base.html, mensajes flash y csrf_token en todos los formularios POST. Incluye navegación según la sesión y un formulario POST para cerrar sesión. El diseño completo queda para la fase 5.

Tras el registro correcto, muestra un mensaje y redirige al login. Utiliza exclusivamente la gestión de contraseñas de Django.

Añade pruebas de registro válido, usuario duplicado, contraseñas inválidas, login correcto/incorrecto, logout POST y bloqueo anónimo de /reservas/ con redirección al login. Comprueba que la contraseña se almacena como hash.

Ejecuta manage.py check y la suite de pruebas. Guarda este prompt y resultados en docs/prompts.md como «Fase 3».

No implementes aún creación ni cancelación de reservas.
```

### Resultados
- Configurados `LOGIN_URL = '/login/'`, `LOGIN_REDIRECT_URL = '/reservas/'` y `LOGOUT_REDIRECT_URL = '/login/'` en `config/settings.py`.
- Implementadas las rutas `/`, `/registro/`, `/login/`, `/logout/` (POST) y `/reservas/` (`@login_required`) en `reservas/urls.py`, `config/urls.py` y `reservas/views.py` con `UserCreationForm`, `LoginView`, `LogoutView` y mensajes flash.
- Creadas las plantillas mínimas `reservas/templates/base.html`, `reservas/templates/reservas/registro.html`, `login.html` y `reservas_list.html` con `{% csrf_token %}` y navegación condicional según sesión.
- Añadidas 6 pruebas de autenticación en `reservas/tests.py` (registro válido con hash, usuario duplicado, contraseñas inválidas, login correcto/incorrecto, logout POST y bloqueo anónimo); `manage.py check` (0 incidencias) y 14/14 pruebas superadas (`OK`).

---

## Fase 4

### Prompt
```text
FASE 4 — Formularios y vistas protegidas de PadelUrban.

Consulta docs/requisitos.md y reutiliza los modelos y la autenticación existentes.

Implementa:
1. /reservas/: listado cronológico de reservas, diferenciando las propias e incluyendo pista, fecha, horas y duración.
2. /reservas/nueva/: ModelForm con únicamente pista, fecha, hora_inicio y hora_fin. Ofrece solo pistas activas y rechaza identificadores de pistas inactivas enviados manualmente.
3. Asigna usuario=request.user desde el servidor antes de validar el formulario. Ignora cualquier usuario enviado por el cliente. Aprovecha clean() del modelo para mostrar los errores de horario y solapamiento, sin duplicar esa lógica.
4. /reservas/<id>/cancelar/: acepta exclusivamente POST y elimina únicamente reservas del usuario conectado. Devuelve 403 o 404 si la reserva pertenece a otro usuario.

Protege todas las vistas con @login_required. Añade csrf_token a los formularios, mensajes de éxito/error y plantillas mínimas. Muestra el botón de cancelación solo en reservas propias; comprueba también la propiedad en el servidor.

Añade pruebas de:
- Asignación automática y resistencia a suplantación mediante POST.
- Horarios inválidos y solapamientos sin guardar registros.
- Reservas consecutivas válidas y rechazo de pistas inactivas.
- Cancelación propia y bloqueo de cancelación ajena.
- GET sin borrado, acceso anónimo bloqueado y POST sin CSRF rechazado usando un cliente con comprobación CSRF activa.

Ejecuta manage.py check y la suite completa. Registra este prompt y resultados en docs/prompts.md como «Fase 4».

No avances al diseño visual final.
```

### Resultados
- Creado `ReservaForm` en `reservas/forms.py` (`pista`, `fecha`, `hora_inicio`, `hora_fin`) filtrando pistas activas (`activa=True`).
- Implementadas en `reservas/views.py` y `reservas/urls.py` las vistas protegidas `@login_required`: `reservas_inicio` (`/reservas/`), `reserva_crear` (`/reservas/nueva/` con `Reserva(usuario=request.user)` previo a validar y aprovechamiento de `Reserva.clean()`) y `reserva_cancelar` (`/reservas/<id>/cancelar/` con `@require_POST` y 403 si no es propietario).
- Actualizadas `reservas_list.html` y `reserva_form.html` con `{% csrf_token %}`, duración, diferenciación de reservas propias y botón de cancelación solo para el propietario.
- Añadidas 7 pruebas en `reservas/tests.py` (asignación automática/anti-suplantación, horarios/solapamientos, consecutivas/pista inactiva, cancelación propia/ajena, GET sin borrado/anónimo y CSRF activo); `manage.py check` (0 incidencias) y 21/21 pruebas superadas (`OK`).

---

## Fase 5

### Prompt
```text
FASE 5 — Interfaz de PadelUrban.

Consulta docs/requisitos.md. Mejora las plantillas existentes con Bootstrap 5 mediante CDN y herencia de base.html.

Diseño:
- Interfaz limpia en español, fondo claro, verde oscuro y buen contraste.
- Cabecera «PadelUrban», navegación según sesión y logout mediante POST.
- Login y registro en tarjetas centradas.
- Listado responsive con pista, fecha, inicio, fin y duración en minutos.
- Reservas propias identificadas mediante texto «Tu reserva» y color.
- Botón «Nueva reserva», estado vacío y cancelación solo en reservas propias, con confirmación.
- Formularios con etiquetas visibles, controles adecuados de fecha/hora y errores por campo y generales.
- Mensajes flash con estilos Bootstrap.

Conserva @login_required, asignación automática del usuario, validaciones y CSRF. Limita los cambios a presentación y atributos visuales de formularios. Evita dependencias adicionales.

Ejecuta manage.py check y la suite existente. Si dispones de navegador, comprueba escritorio y móvil; indica expresamente si no pudiste verificar la apariencia.

Guarda este prompt y resultados en docs/prompts.md como «Fase 5». No empaquetes ni despliegues todavía.
```

### Resultados
- Actualizadas `base.html`, `login.html`, `registro.html`, `reservas_list.html` y `reserva_form.html` con Bootstrap 5.3.3 vía CDN, paleta verde oscuro (`#14532d`) sobre fondo claro, tarjetas centradas, alertas flash Bootstrap, listado responsive con etiqueta «Tu reserva» (`table-success`), estado vacío y confirmación en cancelación.
- Añadidas clases Bootstrap (`form-select`, `form-control`) en `reservas/forms.py` conservando `@login_required`, asignación automática de `usuario`, validaciones y CSRF.
- Verificada la interfaz en navegador en escritorio (`1280x800`) y móvil (`390x844`) sin desbordamiento horizontal; ajustado el contraste de enlaces en navbar y selector de pista tras la revisión visual.
- Ejecutados `manage.py check` (0 incidencias) y las 21 pruebas de `reservas/tests.py` (`OK`).

---

## Mejora visual

### Prompt
```text
MEJORA VISUAL — PadelUrban.

Rediseña la interfaz existente con estética de club de pádel contemporáneo: deportiva, acogedora y elegante. Este brief ya contiene las decisiones de diseño: no investigues referencias adicionales.

ALCANCE
Reutiliza Django, Bootstrap 5 y las funcionalidades existentes. Cambia presentación, CSS y recursos gráficos locales. Conserva rutas, seguridad, formularios, validaciones y pruebas.

PALETA
Define variables CSS:
- Fondo marfil: #FCFAF7.
- Superficies blancas: #FFFFFF.
- Lavanda pastel: #EEE8FB.
- Melocotón pastel: #FAE1D2.
- Azul pastel: #DEEAF8.
- Texto principal: #29263D.
- Texto secundario: #625D73.
- Botón principal violeta: #66508C, texto blanco.
- Hover principal: #503D72.
- Bordes: #E5DFEA.

Los pasteles son fondos y acentos; usa texto oscuro legible. Sustituye el verde dominante.

IDENTIDAD
- Logotipo «PadelUrban» acompañado de una pequeña pala original en SVG.
- Tipografía Plus Jakarta Sans, con fallback system-ui.
- Títulos con peso 700, texto base de 16px, espacio generoso y jerarquía clara.
- Tarjetas con radios de 20px, bordes finos y sombras discretas.
- Botones de al menos 44px de alto y foco de teclado visible.

REFERENCIAS AL PÁDEL
Crea SVG originales y ligeros: pista cenital con red y líneas de saque, palas perforadas y pelota. Úsalos como ilustración principal y pequeños detalles decorativos. Los elementos decorativos llevarán aria-hidden y no interceptarán clics. Guarda los recursos en static; evita fotografías externas y nuevas librerías.

PANTALLAS
1. Cabecera clara con marca, navegación y usuario. Menú móvil accesible.
2. Reservas: bloque introductorio compacto, texto «Tu próximo partido empieza aquí», botón «Reservar pista» e ilustración de pista sobre fondo lavanda. El listado debe quedar visible pronto, sin una portada enorme.
3. Presenta las reservas como tarjetas ordenadas cronológicamente: fecha destacada, pista, horario y duración. Dos columnas en escritorio y una en móvil. Reserva propia con etiqueta «Tu reserva», acento lavanda y cancelación visible.
4. Estado vacío con ilustración pequeña y llamada a reservar.
5. Login y registro: composición dividida en escritorio, ilustración deportiva a un lado y formulario al otro; una columna en móvil.
6. Nueva reserva: formulario claro dentro de tarjeta, campos amplios, ayuda y errores legibles.
7. Mensajes flash suaves y cancelación con confirmación. Conserva POST y CSRF.

ACABADO
Aplica estilos coherentes a todas las pantallas, incluidos errores, enlaces, botones secundarios y controles. Transiciones discretas de 150–200ms respetando prefers-reduced-motion. No añadas funciones, estadísticas ficticias, carruseles ni animaciones continuas.

VERIFICACIÓN
Comprueba en navegador a 390px y 1440px: sin desbordamientos, solapamientos ni contenido cortado; navegación, formularios y cancelación utilizables. Si el navegador no está disponible, indícalo.

Ejecuta manage.py check y la suite existente una vez al finalizar. Documenta prompt y resultados en docs/prompts.md como «Mejora visual».
```

### Resultados
- Creada la hoja de estilos `reservas/static/reservas/css/padelurban.css` con variables CSS de la paleta marfil/lavanda/melocotón/azul/violeta, tipografía `Plus Jakarta Sans`, tarjetas con radio de `20px`, botones `>= 44px`, foco `:focus-visible` y soporte para `prefers-reduced-motion`.
- Creados los SVG originales locales en `reservas/static/reservas/img/`: `pala-logo.svg`, `pista-cenital.svg`, `padel-auth.svg` y `pelota-empty.svg` (con `aria-hidden="true"` y sin interceptar clics).
- Rediseñadas `base.html`, `login.html`, `registro.html`, `reservas_list.html` y `reserva_form.html` con cabecera limpia, login/registro divididos en escritorio, bloque compacto «Tu próximo partido empieza aquí», tarjetas de reserva (2 columnas en escritorio, 1 en móvil) con acento lavanda y «Tu reserva», estado vacío y alertas suaves.
- Verificados `manage.py check` (0 incidencias), `manage.py test reservas` (21/21 `OK`) y comprobación visual en navegador a `1440px` y `390px` sin desbordamientos, solapamientos ni contenido cortado, incluyendo navegación, formularios y cancelación con confirmación.

---

## Revisión de seguridad

### Prompt
```text
REVISIÓN DE SEGURIDAD — PadelUrban.

Revisa el código existente, corrige problemas demostrados y conserva el diseño y los requisitos del examen. Evita reescribir componentes que ya funcionan.

1. CONTRASEÑAS Y SESIONES
Comprueba UserCreationForm, validadores de contraseñas, almacenamiento mediante hash y autenticación de Django. Ninguna contraseña debe aparecer en código, fixtures, documentación ni logs. Verifica logout POST e invalidación de sesión.

2. PERMISOS Y FORMULARIOS
Comprueba @login_required en todas las vistas de reservas, asignación de request.user e imposibilidad de cancelar reservas ajenas manipulando URL o POST. Mantén CSRF activo en registro, login, logout, creación y cancelación. Ningún GET debe modificar datos.

3. ENTRADAS MALICIOSAS
Comprueba autoescape de plantillas, ausencia de uso inseguro de safe/mark_safe, consultas mediante ORM y redirecciones next restringidas a destinos permitidos. Los errores de login no deben revelar si una cuenta existe.

4. INTENTOS DE LOGIN
Integra una versión estable de django-axes compatible con el entorno. Configura bloqueo temporal tras 5 fallos por combinación usuario/IP, con enfriamiento de 15 minutos, tanto en /login/ como en /admin/. Usa almacenamiento en base de datos, respuesta 429 y mensaje en español coherente con el diseño.
Aplica migraciones, fija la versión instalada y documenta el desbloqueo administrativo. No confíes en cabeceras de proxy arbitrarias.

5. CONFIGURACIÓN
Externaliza SECRET_KEY y excluye secretos y db.sqlite3 de Git y del futuro ZIP. Deja instrucciones reproducibles y ejemplos sin valores reales.
Separa desarrollo local HTTP y producción HTTPS: DEBUG desactivado en producción, ALLOWED_HOSTS explícitos, cookies seguras y protecciones estándar de Django. Producción debe fallar si falta la clave secreta. No fuerces HTTPS en localhost ni inventes dominios o configuración de proxy.

6. VERIFICACIÓN
Reutiliza las pruebas existentes y añade únicamente las que falten para demostrar estas protecciones, incluyendo bloqueo temporal, CSRF real, permisos, redirección externa y escape de contenido.
No desactives protecciones para conseguir que pasen las pruebas.
Ejecuta check, suite completa y check --deploy con configuración de producción. Documenta advertencias pendientes; no las silencies.
Audita dependencias con pip-audit. Si no puedes completar alguna comprobación, indica el motivo.

Guarda hallazgos, correcciones, pruebas y limitaciones en docs/seguridad.md. Registra este prompt y resultados en docs/prompts.md como «Revisión de seguridad».
```

### Resultados
- Externalizada `SECRET_KEY` (`DJANGO_SECRET_KEY`), separada configuración de desarrollo HTTP y producción HTTPS en `config/settings.py`, creado `.env.example` y eliminado `|safe` de `registro.html`.
- Integrado `django-axes==9.1.0` (fijado en `requirements.txt`, migraciones aplicadas) con bloqueo tras 5 fallos por `(username, ip_address)`, enfriamiento de 15 minutos, respuesta HTTP 429 (`lockout.html`) y uso exclusivo de `REMOTE_ADDR`.
- Añadidas 4 pruebas de seguridad en `reservas/tests.py` (25/25 `OK`); `manage.py check` (0 incidencias), `manage.py check --deploy` (solo `security.W009` si la clave de prueba tiene < 50 caracteres) y `pip-audit -r requirements.txt` sin vulnerabilidades.
- Documentados hallazgos, desbloqueo administrativo y limitaciones en `docs/seguridad.md`.

---

## Verificación final de seguridad y carga

### Prompt
```text
VERIFICACIÓN FINAL DE SEGURIDAD Y CARGA — PadelUrban.

Reutiliza docs/seguridad.md y las comprobaciones existentes. Conserva diseño, funcionalidades y protecciones.

1. CERRAR AVISO DE CONFIGURACIÓN
Ejecuta manage.py check --deploy --fail-level WARNING usando la configuración de producción y una DJANGO_SECRET_KEY temporal generada con secrets.token_urlsafe(64).
Pasa los valores necesarios únicamente al entorno del proceso. No muestres ni guardes secretos. No silencies advertencias. Corrige problemas del proyecto e informa de requisitos pendientes del alojamiento.

2. COMPROBAR PROTECCIÓN DE LOGIN
Revisa las pruebas existentes de django-axes para /login/ y /admin/login/.
Comprueba bloqueo tras 5 fallos, respuesta 429, recuperación tras el enfriamiento y que otra cuenta legítima no quede bloqueada por compartir IP.
Añade solo las pruebas que falten. Simula el paso del tiempo, sin esperar 15 minutos.
Documenta el alcance del bloqueo por combinación usuario/IP: no equivale a protección global contra saturación ni contra intentos repartidos entre muchas cuentas o direcciones.

3. PRUEBA LIGERA DE CARGA LOCAL
Crea una comprobación reproducible usando un servidor temporal exclusivo en 127.0.0.1, base SQLite temporal y datos sintéticos. No uses ni modifiques db.sqlite3 ni cuentas existentes.

Prueba lecturas autenticadas del listado con una sesión válida, sin repetir el login en cada petición. Confirma que las respuestas contienen realmente el listado y no una redirección al login.

Límites obligatorios:
- Máximo 100 solicitudes en total.
- Máximo global de 5 solicitudes por segundo.
- Máximo de 3 solicitudes simultáneas.
- Duración máxima de 30 segundos.
- Timeout de 3 segundos por solicitud.
- Detención anticipada tras 3 errores 5xx o timeouts consecutivos.

Restringe el destino a 127.0.0.1 y rechaza redirecciones fuera de ese destino. No aumentes automáticamente los límites.

Registra solicitudes realizadas, códigos HTTP, errores, latencia media y percentil 95. Identifica los datos y condiciones de la prueba. No presentes este resultado como capacidad de producción ni resistencia demostrada a DDoS.

Detén únicamente el servidor temporal que hayas creado y elimina sus datos temporales al finalizar, incluso si hay errores.

4. RESULTADOS
Corrige fallos reproducibles sin debilitar controles. Ejecuta la suite completa solo si modificas código o pruebas.

Guarda el procedimiento, métricas, correcciones y limitaciones en docs/seguridad.md. Distingue resultados locales de medidas pendientes del despliegue: límites de peticiones y conexiones, timeouts y protección del proveedor. No inventes una configuración de alojamiento.

Registra este prompt y resultados en docs/prompts.md. No publiques ni empaquetes todavía.
```

### Resultados
- `manage.py check --deploy --fail-level WARNING` en producción con `DJANGO_SECRET_KEY` generada mediante `secrets.token_urlsafe(64)` superado sin avisos (`EXIT 0`).
- Añadida `test_recuperacion_tras_enfriamiento_axes` en `reservas/tests.py` (simulando el paso de 16 min); suite completa superada (`26/26 OK`).
- Creado `scripts/prueba_carga_local.py` (servidor y SQLite temporales vía `DJANGO_DB_PATH` en `config/settings.py`): 100 lecturas autenticadas en 19.81 s (`HTTP 200`: 100, 0 errores, media 18.72 ms, P95 35.22 ms), con limpieza automática al finalizar.
- Documentados métricas, alcance de `django-axes` y requisitos pendientes del alojamiento en `docs/seguridad.md`.

---

## Preparación de entrega

### Prompt
```text
PREPARACIÓN DE ENTREGA — Documentación de PadelUrban.

Revisa el código y la documentación existentes. No cambies funcionalidades ni diseño.

1. Crea README.md con objetivo, tecnologías, instalación reproducible en Windows/PowerShell, configuración de variables, migraciones, fixture, createsuperuser, arranque local, pruebas y enlaces a documentación.

2. Comprueba que docs/modelo_er.md coincide con los modelos reales. Exporta a .svg y .pdf con herramienta local. Si no puedes exportar, informa del impedimento.

3. Revisa docs/prompts.md: conserva los prompts en orden sin reconstruir conversaciones.

4. Crea docs/checklist_entrega.md relacionando requisitos del examen con implementación y evidencia.

5. Crea docs/defensa_3_minutos.md con guion para MVT, modelos, clean(), duracion_minutos(), request.user, permisos y CSRF.

Registra este prompt en docs/prompts.md. No repitas pruebas por cambios documentales. No generes ZIP ni publiques en GitHub.
```

### Resultados
- Creado [`README.md`](../README.md) con tecnologías y versiones reales, instalación paso a paso en PowerShell, configuración de variables de entorno sin carga automática de `.env`, migraciones, fixture, createsuperuser y tabla de 26 pruebas.
- Actualizado [`docs/modelo_er.md`](modelo_er.md): clarificada la tabla real `auth_user`, añadidas notas de exportación (`mmdc`) y verificado que atributos, tipos, PK/FK y cardinalidades coinciden con `reservas/models.py`. Exportación a SVG/PDF pendiente de Node.js + Mermaid CLI en el entorno.
- Creados [`docs/checklist_entrega.md`](checklist_entrega.md) (todos los ítems del examen con evidencia automatizada o manual) y [`docs/defensa_3_minutos.md`](defensa_3_minutos.md) con guion de 3 minutos (MVT, modelos, `clean()`, `duracion_minutos()`, `request.user`, permisos y CSRF).

---

## Cierre de entrega (27/11/2026)

### Solicitud

Continuar el proyecto existente, contrastar documentación y código, verificar la suite y la configuración, preparar un ZIP reproducible sin datos locales y revisar el contenido destinado a GitHub.

### Resultados

- Actualizados el README, los requisitos, el checklist, las referencias del modelo ER y el registro de seguridad. El modelo se entrega en MD, SVG y PDF. Se conservó el código de la aplicación.
- `manage.py check` y `manage.py check --deploy --fail-level WARNING` finalizaron sin avisos. La suite completa pasó 26 de 26 pruebas. `pip check` no detectó dependencias rotas. `pip-audit` se ejecutó, pero no pudo completar la consulta a PyPI por un error de resolución DNS tras reintentar sin entorno auxiliar.
- Se extrajo el ZIP de verificación en una carpeta temporal. Django confirmó que no faltan migraciones, aplicó las existentes y el fixture reconstruyó la pista Central activa y techada y la pista Exterior activa y descubierta. La base temporal quedó sin cuentas ni reservas. El README documenta `createsuperuser` con credenciales elegidas por quien instala la aplicación.
- Revisados los archivos de entrega y reforzadas las exclusiones en `.gitignore`. Se comprobó la integridad de la base local mediante SHA-256 y se conservaron las mediciones históricas de carga.
- Inicializado Git en la rama `main`. El entorno bloqueó la escritura del índice de Git. Quedan pendientes el commit inicial, un remoto de GitHub y su visibilidad.
- El entorno bloqueó la escritura del ZIP en la carpeta superior. El paquete quedó en la carpeta del proyecto con una única raíz `PadelUrban/`.
