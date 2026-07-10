# Proposal: T17 — Validaciones básicas — Campos requeridos y formatos mínimos

## Intent

Hoy `POST /admin/becas/nueva` y `POST /admin/becas/<id>/editar` persisten sin validar — datos vacíos se guardan como cadenas vacías, deadlines con formato inválido entran igual, el admin nunca recibe feedback de error. Sin T17, el sistema acepta basura y no se lo dice a nadie.

## Scope

### In Scope
- Función helper de validación para `title` (obligatorio), `institution` (obligatorio), `deadline` (formato YYYY-MM-DD si se ingresa), `link` (URL http/https si se ingresa)
- Llamada a validación en ambos POST (nueva y editar) antes de persistir
- Render del template con errores y datos precargados cuando hay fallos de validación (sin flash, sin redirect)
- Bloque de renderizado de errores en `templates/nueva_beca.html`
- Import de `re` en `controllers/auth.py`

### Out of Scope
- Mensajes flash de éxito/error (T18)
- Estilos CSS para errores (T20)
- Validación client-side extra (el `required` HTML ya está)
- Normalización de datos (trim, lowercasing, etc.)
- Validación en `deadline` de que la fecha sea real (ej. 2026-02-30 pasaría)
- Validación en `link` de que la URL sea alcanzable (solo prefix check)

## Capabilities

### New Capabilities
- `scholarship-validation`: función `_validar_beca(data)` que chequea campos requeridos y formatos mínimos, y mecanismo para mostrar errores en el template sin perder datos ingresados

### Modified Capabilities
- `admin-create-scholarship` (T13): el POST deja de persistir ciegamente; valida antes y vuelve al form con errores si falla
- `scholarship-edit-view` (T15/T16): el POST deja de persistir ciegamente; valida antes y vuelve al form con errores si falla
- `scholarship-edit-view`: el template `nueva_beca.html` ahora recibe `errores` y `beca` también en el path de creación (antes solo editar recibía `beca`)

## Approach

### Opción recomendada: helper privado en `controllers/auth.py`

Agregar `_validar_beca(data)` como función privada (prefijo `_`) en `auth.py`, justo antes de las rutas. Recibe un dict con los campos del form y devuelve una lista de strings (vacía si todo ok).

**Por qué esta opción y no un separado:**
- Son ~15 líneas, una sola responsabilidad, llamada desde solo dos rutas en el mismo archivo
- Un archivo `controllers/validators.py` añadiría un import y un archivo para una función que no se reusa fuera de auth.py
- El prefijo `_` ya comunica "no me importes desde afuera"

### Mecanismo de errores

Cuando hay errores, ambos POST hacen `return render_template('nueva_beca.html', errores=errores, beca=data)` — no hay redirect ni flash. El template existente se modifica para que:
- `nueva_beca.html` recorra `errores` y los muestre como lista no ordenada arriba del form
- Use `beca.title`, `beca.institution`, etc. para precargar lo que el admin ya escribió (hoy solo usa `beca` en modo edición)

El cambio en el template es mínimo: el contexto `beca` es un dict (no un `sqlite3.Row`) cuando viene de validación fallida, y un Row cuando viene de editar GET. Ambos soportan acceso por clave.

### Pseudocódigo del cambio en auth.py

```python
import re

def _validar_beca(data):
    errores = []
    if not data.get('title', '').strip():
        errores.append('El título es obligatorio.')
    if not data.get('institution', '').strip():
        errores.append('La institución es obligatoria.')
    deadline = data.get('deadline', '').strip()
    if deadline and not re.match(r'^\d{4}-\d{2}-\d{2}$', deadline):
        errores.append('La fecha límite debe tener formato YYYY-MM-DD.')
    link = data.get('link', '').strip()
    if link and not re.match(r'^https?://', link):
        errores.append('El link debe ser una URL válida (https://...).')
    return errores

# En nueva_beca() POST:
errores = _validar_beca(data)
if errores:
    return render_template('nueva_beca.html', errores=errores, beca=data)
create(db, data)
return redirect(url_for('auth.dashboard'))

# En editar_beca() POST:
errores = _validar_beca(data)
if errores:
    return render_template('nueva_beca.html', errores=errores, beca=data, editando=True)
update(db, beca_id, data)
return redirect(url_for('auth.dashboard'))
```

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/auth.py` | Modified | +`import re`, +función `_validar_beca()`, llamada en ambos POSTs con render condicional |
| `templates/nueva_beca.html` | Modified | +bloque de renderizado de errores, +valor precargado en inputs para creación |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Template accede a `beca.title` pero el dict viene sin algunos campos | Low | Todas las claves se setean con `request.form.get(k, '')` — nunca falta una clave |
| `beca` es un dict en validación vs `sqlite3.Row` en editar GET | Low | Ambos soportan `beca['title']` y `beca.title`. El template usa `.title` (atributo) que funciona en Row pero no en dict. **Hay que cambiar el template a** `beca.title` **o** `beca['title']` **para que funcione en ambos casos. Se usará filtro por defecto:** `{{ beca.get('title', '') if beca is mapping else beca.title }}` — o mejor, unificar normalizando a dict en la rama GET de editar. |
| `is_published` checkbox no se precarga tras error | Low | Aceptado: el checkbox solo manda `1` si está marcado. En error, el admin debe volver a marcarlo. No es blocker. |

## Rollback Plan

Revertir los cambios en `controllers/auth.py` y `templates/nueva_beca.html`. Sin migraciones de BD ni cambios de esquema que afectar.

## Dependencies

- T13 completa (`nueva_beca()` POST existe)
- T15/T16 completa (`editar_beca()` GET+POST existe)
- El template `nueva_beca.html` existe y es dual (creación/edición)

## Success Criteria

- [ ] `POST /admin/becas/nueva` con `title` vacío devuelve el form con error "El título es obligatorio." y los datos intactos
- [ ] `POST /admin/becas/nueva` con `institution` vacío devuelve el form con error correspondiente
- [ ] `POST /admin/becas/nueva` con `deadline=invalido` devuelve error de formato YYYY-MM-DD
- [ ] `POST /admin/becas/nueva` con `deadline=2026-12-31` pasa validación
- [ ] `POST /admin/becas/nueva` con `link=ftp://algo` devuelve error de URL válida
- [ ] `POST /admin/becas/nueva` con `link=https://ejemplo.com` pasa validación
- [ ] `POST /admin/becas/1/editar` con datos inválidos devuelve errores + campos precargados
- [ ] `POST /admin/becas/1/editar` con datos válidos persiste sin cambios de comportamiento (sigue redirigiendo a dashboard)
- [ ] Si solo `title` está vacío, solo se muestra ese error (no todos a la vez, pero sí todos los que apliquen)
- [ ] Campos opcionales (`description`, `requirements`, `location`) vacíos pasan validación sin errores
- [ ] `deadline` vacío pasa validación (es opcional)
- [ ] `link` vacío pasa validación (es opcional)
- [ ] `title` con solo espacios es tratado como vacío (error)
- [ ] `institution` con solo espacios es tratado como vacío (error)
- [ ] GET de ambos formularios no muestra errores (no hay `errores` en el contexto)
