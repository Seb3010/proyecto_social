# Proposal: T07 — Crear listado público (ruta + template para becas publicadas)

## Intent

Conectar el modelo `scholarship.py` (T05) con la web. Sin esta tarea, el entrypoint Flask solo muestra un placeholder. El usuario visita `/` y ve el listado de becas publicadas con búsqueda por texto.

## Scope

### In Scope
- `controllers/__init__.py` — package marker
- `controllers/becas.py` — Blueprint `becas` con `GET /` y `GET /buscar`
- `templates/listado.html` — template con cards + buscador + mensaje vacío
- `templates/base.html` — layout base mínimo con bloque `content`
- `app.py` — registrar Blueprint, eliminar placeholder `index()`

### Out of Scope
- CSS/estilos (T19)
- JS frontend (T21)
- Vista detalle de beca (T08)
- Login/sesión admin (T09+)
- Panel admin (T12+)

## Capabilities

### New Capabilities
- `public-scholarship-listing`: listado público de becas publicadas con búsqueda

### Modified Capabilities
None — primera capability pública del proyecto.

## Approach

```
controllers/becas.py          → Blueprint 'becas' url_prefix=''
  GET /                        → listado(): get_all(published_only=True) → listado.html
  GET /buscar?q=               → buscar(): search(db, q) o get_all(published_only=True) si q vacío

templates/base.html            → HTML5 doctype, <head>, <title>, {% block content %}
templates/listado.html         → extiende base, form GET /buscar, cards con for/if/else

app.py                         → from controllers.becas import becas_bp
                                 app.register_blueprint(becas_bp)
                                 remover @app.route('/') index()
```

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/__init__.py` | New | Package marker (vacío o docstring) |
| `controllers/becas.py` | New | Blueprint con 2 rutas públicas |
| `templates/base.html` | New | Layout base HTML5 |
| `templates/listado.html` | New | Template listado + buscador + cards |
| `app.py` | Modified | Register blueprint, remove placeholder route |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SQL injection en búsqueda | Low | `%` wrapping + placeholders ya en `search()` |
| Blueprint no registrado → 404 | Low | `register_blueprint` antes de correr app |
| Template inexistente → 500 | Low | Archivos creados en mismo cambio |

## Rollback Plan

Revertir cambios en `app.py` (quitar registro del blueprint, restaurar placeholder). Eliminar `controllers/` y `templates/listado.html` + `base.html`. Ninguna data se pierde.

## Dependencies

- T05 completada (`scholarship.py` con `get_all(published_only=True)` y `search()`)
- `models/db.py` con `get_db()` funcionando

## Success Criteria

- [ ] `GET /` renderiza listado con solo becas donde `is_published=1`
- [ ] `GET /buscar?q=medicina` devuelve becas cuyo título/institución/descripción contiene "medicina"
- [ ] `GET /buscar?q=` (vacío) muestra todas las publicadas
- [ ] Sin becas publicadas → mensaje "No se encontraron becas"
- [ ] Placeholder `/` original es reemplazado, no hay ruta duplicada
