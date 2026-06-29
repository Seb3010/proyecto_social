# Proposal: T08 — Crear detalle público (ruta + template para detalle de beca)

## Intent

Sin esta tarea, el listado público (T07) muestra cada beca como un card con título, institución y ubicación, pero no hay forma de ver la información completa. El usuario que encuentra una beca interesante en el listado no puede acceder a la descripción, requisitos, fecha límite ni enlace de postulación.

## Scope

### In Scope
- `controllers/becas.py` — agregar ruta `GET /becas/<int:beca_id>` en el Blueprint `becas`
- `templates/detalle.html` — template nuevo que extiende `base.html`
- `templates/listado.html` — reemplazar URL quemada `/becas/{{ beca.id }}` por `url_for('becas.detalle', beca_id=beca.id)`

### Out of Scope
- CSS/estilos (T19)
- JS frontend (T21)
- Admin
- Manejo de slugs o URLs amigables
- Vistas relacionadas (becas similares, etc.)

## Capabilities

### New Capabilities
- `public-scholarship-detail`: vista detalle de una beca individual con todos sus campos

### Modified Capabilities
- `public-scholarship-listing`: el template del listado ahora usa `url_for` en vez de una URL hardcodeada para navegar al detalle

## Approach

```
controllers/becas.py          → agregar GET /becas/<beca_id>
  get_by_id(db, id) → None? abort(404) : render_template('detalle.html', beca=beca)

templates/detalle.html         → extiende base.html, muestra todos los campos
                                {% if beca.description %} / {% if beca.requirements %}
                                link condicional si beca.link existe
                                link "← Volver al listado" con url_for('becas.listado')

templates/listado.html         → reemplazar href="/becas/{{ beca.id }}"
                                por href="{{ url_for('becas.detalle', beca_id=beca.id) }}"
```

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/becas.py` | Modified | Nueva ruta `GET /becas/<beca_id>`, import `abort` |
| `templates/detalle.html` | New | Template detalle de beca individual |
| `templates/listado.html` | Modified | URL quemada → `url_for` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|-------------|
| Beca no encontrada → 500 sin abort | Low | `if beca is None: abort(404)` explícito |
| Blueprint sin importar abort | Low | Agregar `abort` al import de Flask |
| Campos None en template → error | Low | Jinja2 maneja `{{ None }}` silenciosamente, pero se usan `{% if %}` para `description`, `requirements` y `link` |

## Rollback Plan

Revertir cambios en `controllers/becas.py` (remover ruta y su import de `abort`). Eliminar `templates/detalle.html`. Revertir `templates/listado.html` a URL quemada. Ninguna data se pierde.

## Dependencies

- T07 completada: Blueprint `becas` registrado, `listado.html` y `base.html` existentes
- `models/scholarship.py` con `get_by_id()` funcionando (T05)

## Success Criteria

- [ ] `GET /becas/1` muestra detalle completo de la beca con id=1
- [ ] `GET /becas/9999` retorna HTTP 404
- [ ] `description` y `requirements` como None no rompen la página (no se renderizan si son None)
- [ ] Si `link` no es None, se muestra enlace "Más información" con `target="_blank"`
- [ ] Si `link` es None, no se muestra el enlace
- [ ] El enlace "← Volver al listado" navega correctamente a `GET /`
- [ ] Los títulos en el listado ahora apuntan a `GET /becas/<id>` via `url_for`
