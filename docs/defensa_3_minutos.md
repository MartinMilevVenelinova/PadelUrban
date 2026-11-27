# Guion de Defensa — PadelUrban (3 minutos)

## Estructura sugerida

### 0. Presentación (15 s)
> «PadelUrban es una aplicación web Django para reservar pistas de pádel. Sigue la arquitectura MVT: los modelos gestionan los datos, las vistas la lógica y las plantillas la presentación.»

---

### 1. Arquitectura MVT (30 s)
- **Modelos** (`reservas/models.py`): `Pista` y `Reserva` son clases Python que heredan de `django.db.models.Model`. Django traduce cada clase a una tabla SQLite y gestiona las consultas mediante el ORM, sin SQL manual.
- **Vistas** (`reservas/views.py`): funciones que reciben la petición HTTP, consultan los modelos y devuelven una respuesta con la plantilla renderizada.
- **Plantillas** (`reservas/templates/`): archivos HTML con etiquetas Django (`{% %}`, `{{ }}`). Todas heredan de `base.html` para mantener cabecera, mensajes y estilos comunes.

---

### 2. Modelos y relaciones (40 s)
- `Pista` tiene `nombre` (texto único), `techada` (booleano) y `activa` (booleano).
- `Reserva` tiene `fecha`, `hora_inicio`, `hora_fin` y dos claves foráneas con `on_delete=CASCADE`:
  - `usuario` → tabla `auth_user` de Django (el vecino que reserva).
  - `pista` → tabla `reservas_pista`.
- Cardinalidad: un usuario puede tener muchas reservas, una pista puede tener muchas reservas, pero cada reserva pertenece exactamente a un usuario y una pista.

---

### 3. Métodos de instancia: `__str__` y `duracion_minutos()` (20 s)
- `__str__` devuelve una cadena legible; Django la usa en el panel `/admin/` y en los desplegables del formulario.
- `duracion_minutos()` combina `hora_inicio` y `hora_fin` con `datetime.combine()` y calcula la diferencia en segundos, dividiéndola entre 60. Ejemplo: 10:00–11:30 → 90 min.

---

### 4. Validación `clean()` (25 s)
- Se ejecuta automáticamente al llamar a `full_clean()` o cuando el formulario llama a `is_valid()`.
- Valida dos reglas:
  1. `hora_fin > hora_inicio` — lanza `ValidationError` si no se cumple.
  2. Anti-solapamiento: consulta si ya existe alguna reserva en la misma pista y fecha cuyo tramo se solape (`hora_inicio__lt=fin_nuevo` **y** `hora_fin__gt=inicio_nuevo`). Las desigualdades estrictas permiten reservas consecutivas. Si es una edición, excluye la propia reserva con `.exclude(pk=self.pk)`.

---

### 5. `request.user` y permisos (25 s)
- En la vista `reserva_crear`, antes de validar el formulario, se crea la instancia con `Reserva(usuario=request.user)`. El campo `usuario` no aparece en el formulario, por lo que el cliente **no puede** enviarlo ni suplantarlo.
- La cancelación comprueba en el servidor que `reserva.usuario == request.user`. Si no coincide, devuelve `HTTP 403`. El botón «Cancelar» solo se muestra en la plantilla para las reservas propias (doble barrera: visual y de servidor).
- Todas las vistas de reservas están decoradas con `@login_required`: si el usuario no tiene sesión, Django redirige automáticamente a `/login/`.

---

### 6. CSRF (15 s)
- Todos los formularios POST incluyen `{% csrf_token %}`. Django genera un token único por sesión; si una petición POST no lo incluye o incluye uno incorrecto, Django devuelve `HTTP 403` automáticamente. Esto protege contra ataques de tipo Cross-Site Request Forgery.

---

### 7. Cierre (10 s)
> «En resumen: arquitectura MVT limpia, modelos con validación en `clean()`, asignación automática del usuario y protección CSRF en todos los formularios. ¿Alguna pregunta?»
