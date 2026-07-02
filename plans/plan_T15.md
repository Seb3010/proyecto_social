# Proposal: T15 — Formulario editar beca (vista GET precargada)

## Intent

El dashboard (T12) ya tiene links a `auth.editar_beca` por cada beca, pero la ruta no existe — da 404. Sin esta tarea, el admin no puede editar becas existentes. T15 crea la vista GET que muestra el formulario precargado con los datos actuales de la beca. El POST que persiste los cambios es T16.

## Scope

### In Scope
- Ruta `GET /admin/becas/<int:beca_id>/editar` en Blueprint `auth`
- Protegida con `@login_required`
- `abort(404)` si la beca no existe
- Precarga del formulario con datos de `scholarship.get_by_id()`
- Template `nueva_beca.html` modificado para ser dual (crear/editar)
- Botón de submit dice "Actualizar" en modo edición
- Import de `abort` en `controllers/auth.py`

### Out of Scope
- POST que procesa el formulario (T16)
- Validaciones de campos (T17)
- Mensajes flash de éxito/error (T18)
- Estilos CSS (T20)
- Crear un template nuevo (se reutiliza `nueva_beca.html`)

## Capabilities

### New Capabilities
- `scholarship-edit-view`: ruta GET protegida que muestra formulario precargado para editar una beca existente

### Modified Capabilities
- `scholarship-form-template` (T13): `nueva_beca.html` se vuelve dual — acepta `beca` y `editando` en el contexto para alternar entre crear y editar

## Approach

Dos cambios, uno por archivo:

1. **`controllers/auth.py`**: agregar `abort` al import de flask. Agregar ruta `editar_beca(beca_id)`:
   - Decoradores: `@auth_bp.route('/admin/becas/<int:beca_id>/editar')` + `@login_required`
   - Obtiene `db = get_db()`, busca `beca = get_by_id(db, beca_id)`
   - Si `beca is None`: `abort(404)`
   - Render `nueva_beca.html` con `beca=beca` y `editando=True`

2. **`templates/nueva_beca.html`**: modificaciones condicionales:
   - Título: `{% if editando %}Editar Beca{% else %}Nueva Beca{% endif %}`
   - Action del form: `{% if editando %}{{ url_for('auth.editar_beca', beca_id=beca.id) }}{% else %}{{ url_for('auth.nueva_beca') }}{% endif %}`
   - Cada `value=""` → `value="{{ beca.campo or '' }}"` (solo si editando)
   - Checkbox `is_published`: marcar si `beca.is_published == 1`
   - Botón submit: `{% if editando %}Actualizar{% else %}Crear beca{% endif %}`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/auth.py` | Modified | Nueva ruta `editar_beca()` GET, import `abort` |
| `templates/nueva_beca.html` | Modified | Template dual crear/editar con Jinja condicional |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| La beca no existe o ID inválido | Low | `abort(404)` antes de renderizar |
| Campos del modelo cambian (T16+) | Low | Template itera sobre campos conocidos; si se agregan campos, se actualizan inputs manualmente |
| La ruta GET es accesible sin login | None | `@login_required` la protege |

## Rollback Plan

- Revertir cambios en `controllers/auth.py` (git checkout del archivo)
- Revertir cambios en `templates/nueva_beca.html` (git checkout del archivo)
- Sin migraciones de BD ni datos que afectar — es solo vista

## Dependencies

- T05 completa (`get_by_id()` en `models/scholarship.py`)
- T11 completa (`@login_required` disponible)
- T13 completa (`nueva_beca.html` existe como base para template dual)

## Success Criteria

- [ ] `GET /admin/becas/1/editar` responde 200 con el formulario precargado con datos de la beca ID=1
- [ ] `GET /admin/becas/99999/editar` responde 404 (beca inexistente)
- [ ] `GET /admin/becas/1/editar` sin sesión redirige al login (`@login_required`)
- [ ] El título de la página dice "Editar Beca" (no "Nueva Beca")
- [ ] Cada input/textarea muestra el valor actual de la beca
- [ ] El checkbox `is_published` aparece marcado si la beca está publicada
- [ ] El botón de submit dice "Actualizar"
- [ ] El action del form apunta a `auth.editar_beca` con el ID de la beca
- [ ] La ruta `GET /admin/becas/nueva` sigue funcionando sin cambios (modo crear)
