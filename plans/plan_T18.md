# Proposal: T18 — Mensajes flash — Éxito y error en login y formularios

## Intent

Hoy login, nueva beca, editar beca y logout redirigen sin ningún feedback al admin. Si el login falla, el mensaje de error se ve *solo en el form* (renderizado directo). Si una beca se crea o edita bien, el admin llega al dashboard sin saber si la operación funcionó. Sin T18 el sistema opera mudo — no confirma éxito ni centraliza errores.

## Scope

### In Scope
- `flash('Bienvenido al panel', 'success')` en login POST exitoso
- `flash('Usuario o contraseña incorrectos', 'error')` en login POST fallido (reemplaza `error=error`)
- `flash('Beca creada correctamente', 'success')` en nueva_beca POST exitoso
- `flash('Beca actualizada correctamente', 'success')` en editar_beca POST exitoso
- `flash('Sesión cerrada', 'success')` en logout POST
- Bloque `get_flashed_messages()` en `templates/base.html` con soporte `with_categories=true`
- Migrar login de `error=error` a flash + eliminar `{% if error %}` de `login.html`

### Out of Scope
- Estilos CSS para flashes (T20)
- Refactor de validaciones T17 (siguen con `errores=errores`, es mecanismo distinto)
- Flashes en la vista pública (listado/detalle) — solo admin
- Flash de "sesión expirada" o similar

## Capabilities

### New Capabilities
- `flash-messages`: sistema de mensajes flash vía `flash()` de Flask con categorías `success`/`error`, renderizado en `base.html` y visible en todas las páginas admin

### Modified Capabilities
- `admin-login` (T09): login POST pasa de `error=error` (render directo) a `flash()` + redirect; logout POST agrega flash de confirmación
- `admin-create-scholarship` (T13): nueva_beca POST exitoso agrega flash antes del redirect
- `scholarship-edit-view` (T15/T16): editar_beca POST exitoso agrega flash antes del redirect

## Approach

### Opción recomendada: migrar a flash + eliminar `error=error`

**Argumento**: hoy coexisten dos mecanismos — `error=error` en login (render directo) y `errores=errores` en becas (validación T17). Flash es el mecanismo nativo de Flask para mensajes que *sobreviven un redirect*. Centralizar en flash elimina duplicación, asegura que los mensajes se vean en la página destino (dashboard), y unifica el punto de renderizado en `base.html`.

**Alternativa descartada — mantener `error=error`**: requeriría duplicar la lógica de renderizado (un bloque en login.html + otro en base.html), no cubriría los mensajes de éxito post-redirect, y dejaría dos mecanismos activos para el mismo propósito. Inconsistente, más código, más superficie de testing.

### Mecanismo

```python
from flask import flash

# login POST éxito:
flash('Bienvenido al panel', 'success')

# login POST error:
flash('Usuario o contraseña incorrectos', 'error')
# ya NO se pasa error=error al template

# nueva_beca POST éxito:
flash('Beca creada correctamente', 'success')

# editar_beca POST éxito:
flash('Beca actualizada correctamente', 'success')

# logout POST:
flash('Sesión cerrada', 'success')
```

### Renderizado en base.html

```html
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        <div class="flashes">
            {% for category, message in messages %}
                <div class="flash flash-{{ category }}">{{ message }}</div>
            {% endfor %}
        </div>
    {% endif %}
{% endwith %}
```

El bloque va DENTRO de `<body>`, antes de `{% block content %}`, para que los flashes aparezcan arriba de toda página que extienda base.html.

### Decisión: login POST con flash en lugar de `error=error`

- login POST fallido: `flash('...', 'error')` + `return redirect(url_for('auth.login'))` (para que el flash viaje en la sesión y se renderice al hacer GET de login)
- login POST exitoso: `flash('...', 'success')` + `return redirect(url_for('auth.dashboard'))` (ya existente)
- login GET: ya no recibe `error`; solo muestra el flash si hay uno en la sesión
- login.html: eliminar el bloque `{% if error %}`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/auth.py` | Modified | +`import flash`, +5 llamadas a `flash()`, -parámetro `error=error` en login |
| `templates/base.html` | Modified | +bloque `get_flashed_messages()` dentro de `<body>` |
| `templates/login.html` | Modified | -bloque `{% if error %}`, login GET ya no recibe `error` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Login POST fallido usa flash + redirect — el mensaje viaja por sesión | Low | `flash()` es el mecanismo estándar de Flask para este patrón. La sesión ya existe (T09). No hay riesgo de perder el mensaje. |
| login GET sin `error` — si alguien pasa `?error=...` manual, se ignora | Low | Aceptado. No hay flujo que lo use. El flash cubre todos los casos. |
| Flashes se acumulan si hay múltiples redirects | Low | Flask limpia flashes al consumirlos con `get_flashed_messages()`. Un solo render los drena. |

## Rollback Plan

Revertir cambios en `controllers/auth.py`, `templates/base.html` y `templates/login.html`. Sin migraciones de BD ni cambios de esquema. Volver a pasar `error=error` en login GET.

## Dependencies

- T09 completa (login/logout funcionando)
- T14 completa (nueva_beca POST funcionando)
- T16 completa (editar_beca POST funcionando)
- T17 completa (opcional — no hay conflictos, validación usa `errores=errores` que es independiente)

## Success Criteria

- [ ] Login con credenciales correctas redirige a dashboard con flash "Bienvenido al panel"
- [ ] Login con credenciales incorrectas redirige a login con flash "Usuario o contraseña incorrectos"
- [ ] Login GET después de error NO muestra el mensaje como `error=error` (solo como flash si aplica)
- [ ] Crear beca exitoso redirige a dashboard con flash "Beca creada correctamente"
- [ ] Editar beca exitoso redirige a dashboard con flash "Beca actualizada correctamente"
- [ ] Logout exitoso redirige a login con flash "Sesión cerrada"
- [ ] El flash se renderiza en todas las páginas admin (login, dashboard, nueva/editar beca)
- [ ] Flash con categoría `success` tiene clase `flash-success`, flash con categoría `error` tiene clase `flash-error`
- [ ] Las validaciones T17 siguen funcionando sin interferencia (errores de formulario no se mezclan con flashes)
- [ ] Navegar a cualquier página sin flash activo no muestra contenedor vacío de flashes
