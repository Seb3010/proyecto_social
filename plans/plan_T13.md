# Proposal: T13 — Formulario nueva beca (ruta + template + persistencia)

## Intent

El dashboard (T12) tiene un botón "+ Nueva beca" que linkea a `auth.nueva_beca` y da 404 porque la ruta no existe. Sin esta tarea el admin no puede crear becas desde el panel. Necesitamos el formulario de alta, su ruta GET/POST, y que el POST persista la beca en SQLite.

Aunque T14 aparece como tarea separada, en la práctica el handler POST de esta ruta ya ejecuta `scholarship.create()` — la separación es nominal para mantener el plan ordenado, pero la implementación es una sola.

## Scope

### In Scope
- Ruta `GET/POST /admin/becas/nueva` en Blueprint `auth` protegida con `@login_required`
- Template `templates/nueva_beca.html` con formulario para los 8 campos del modelo
- Handler POST que recolecta `request.form`, construye dict, llama a `scholarship.create(db, data)` y hace commit
- Redirect a `auth.dashboard` después de crear
- Import `create` desde `models.scholarship` en `auth.py`
- HTML sin CSS (T20), sin flash messages (T18), sin validaciones (T17)

### Out of Scope
- Validaciones de campos vacíos (T17)
- Mensajes flash de éxito/error (T18)
- Estilos CSS (T20)
- Editar beca (T15/T16)
- Guardar como borrador vs publicar — el checkbox `is_published` ya decide

## Capabilities

### New Capabilities
- `admin-create-scholarship`: ruta `GET/POST /admin/becas/nueva` que muestra formulario y persiste nueva beca vía `scholarship.create()`

### Modified Capabilities
- `admin-dashboard`: el link `url_for('auth.nueva_beca')` ya no da 404; ahora lleva al formulario de alta
- `admin-auth-guard`: `nueva_beca()` se suma a las rutas que usan `@login_required`

## Approach

Agregar ruta `nueva_beca()` en `controllers/auth.py` entre `dashboard()` y `logout()`. GET renderiza `nueva_beca.html`. POST arma dict desde `request.form`, llama a `create(db, data)` de `models/scholarship.py`, y redirige a `auth.dashboard`.

El template `nueva_beca.html` extiende `base.html` con un formulario POST que incluye los 8 campos del modelo. `deadline` se implementa como `<input type="text">` (MVP). Checkbox `is_published` envía `1` si está marcado, `0` si no.

No se necesita `commit()` explícito — `scholarship.create()` ejecuta el INSERT dentro de la transacción actual y `get_db()` devuelve conexión con autocommit desactivado, pero Flask cierra la conexión tras la request haciendo commit implícito. Verificar que el INSERT persista.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/auth.py` | Modified | Agregar `from models.scholarship import create`, nueva ruta `nueva_beca()` con GET/POST |
| `templates/nueva_beca.html` | New | Form POST con campos del modelo, extiende `base.html` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `deadline` como text permite formatos inconsistentes | Low | Aceptado para MVP. T17 agregará validación de formato y campos requeridos. |
| No hay confirmación visual post-creación (flash) | Med | El redirect a dashboard muestra la nueva beca en la tabla. T18 agregará flash. |
| Sin validación, el form acepta datos vacíos | Med | Intencional por ahora. T17 lo cubre. Los inputs usan `value=""` preparados para ese momento. |

## Rollback Plan

Eliminar ruta `nueva_beca()` de `auth.py`, revertir import, borrar `templates/nueva_beca.html`. El dashboard (T12) tendrá un link roto a `auth.nueva_beca` hasta restaurar — aceptable.

## Dependencies

- T11 completa (`@login_required` disponible)
- T12 completa (dashboard con link a `auth.nueva_beca`)
- `scholarship.create(db, data)` existe desde T05
- `base.html` existe desde T07
- Blueprint `auth` registrado en `app.py`

## Success Criteria

- [ ] `GET /admin/becas/nueva` sin sesión redirige a login
- [ ] `GET /admin/becas/nueva` con sesión muestra formulario con los 8 campos
- [ ] Formulario tiene botón "Crear beca" (submit) y link "Cancelar" → dashboard
- [ ] POST envía datos correctamente y redirige a dashboard
- [ ] Beca creada aparece en el listado del dashboard
- [ ] Beca creada es visible en la BD con `sqlite3` directo
- [ ] El link "+ Nueva beca" en dashboard ya no da 404
