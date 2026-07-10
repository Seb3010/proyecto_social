# Proposal: T16 — Actualizar beca - Procesar formulario de edición y persistir en SQLite

## Intent

El dashboard (T12) tiene links "Editar" que llevan a `auth.editar_beca`. T15 creó la vista GET con el formulario precargado, pero la ruta solo acepta GET — hacer submit al form da 405 Method Not Allowed. Sin T16, la edición de becas está a mitad de camino: el admin ve el formulario pero no puede persistir cambios.

## Scope

### In Scope
- Agregar `update` al import de `models.scholarship` en `controllers/auth.py`
- Ruta `editar_beca` cambia a `methods=['GET', 'POST']`
- Rama POST: mapea los 8 campos del form (`title`, `institution`, `description`, `requirements`, `deadline`, `location`, `link`, `is_published`), llama a `update(db, beca_id, data)`, redirige a `auth.dashboard`
- Rama GET se mantiene idéntica a T15

### Out of Scope
- Templates (el dual de T15 ya apunta a `auth.editar_beca`)
- Modelos (`update()` ya existe desde T05)
- Validaciones de campos (T17)
- Mensajes flash de éxito/error (T18)
- Otros controladores o archivos

## Capabilities

### New Capabilities
None

### Modified Capabilities
- `scholarship-edit-view`: pasa de ser solo GET a aceptar GET+POST. El POST persiste los cambios editados vía `scholarship.update()`

## Approach

Un solo cambio en `controllers/auth.py` (~10 líneas):

1. Agregar `update` al import de `models.scholarship`
2. Cambiar el decorador `@auth_bp.route(...)` para incluir `methods=['GET', 'POST']`
3. Dentro de `editar_beca()`: antes del `return render_template(...)`, agregar:
   - `if request.method == 'POST':`
   - Construir `data` dict con los 8 campos del form
   - `update(db, beca_id, data)`
   - `return redirect(url_for('auth.dashboard'))`

La rama GET (beca precargada + abort(404)) queda intacta.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/auth.py` | Modified | +import `update`, +methods POST, +rama POST con mapeo de campos y persistencia |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Beca no existe en POST | Low | `abort(404)` se ejecuta antes de llegar al POST (misma guarda GET) |
| Campos del form no coinciden con modelo | Low | `request.form.get()` con default `''` evita KeyError; `update()` usa los mismos 8 campos que `create()` |
| Sin feedback al admin tras guardar | Medium | Postergado a T18 (mensajes flash) — el redirect a dashboard es funcional pero silencioso |

## Rollback Plan

- Revertir `controllers/auth.py` al estado de T15: `git checkout controllers/auth.py`
- Sin migraciones de BD ni cambios en templates que afectar

## Dependencies

- T05 completa (`update()` en `models/scholarship.py`)
- T15 completa (ruta GET + template dual `nueva_beca.html`)

## Success Criteria

- [ ] `POST /admin/becas/1/editar` con datos válidos redirige a `GET /admin/dashboard`
- [ ] Los campos editados persisten en SQLite (verificar con SELECT directo)
- [ ] `GET /admin/becas/1/editar` sigue funcionando igual que en T15
- [ ] `POST /admin/becas/99999/editar` responde 404 (beca inexistente)
- [ ] Sin sesión activa, POST redirige al login (`@login_required`)
- [ ] El checkbox `is_published` se marca/desmarca correctamente (0 → 1, 1 → 0)
