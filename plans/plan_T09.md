# Proposal: T09 — Implementar login admin (formulario + validación)

## Intent

Conectar el modelo `admin.py` (T06) con la web. Sin esta tarea, no hay forma de que el admin acceda al sistema. El formulario de login es la puerta de entrada al panel de administración. Una vez autenticado, el admin puede acceder a rutas protegidas (T11+).

## Scope

### In Scope
- `controllers/auth.py` — Blueprint `auth` con `GET` y `POST /admin/login`
- `templates/login.html` — formulario que extiende `base.html`
- `app.py` — registrar Blueprint `auth`
- Usar `werkzeug.security.check_password_hash` para validar credenciales contra `admin_users.password_hash`
- Sesión con `session` de Flask (`admin_id`)
- Redirect a `auth.dashboard` (placeholder intencional — dará 404 hasta T12)
- Manejo de error: "Usuario o contraseña incorrectos" si falla validación

### Out of Scope
- Logout (T10)
- Proteger rutas admin con decorador/session check (T11)
- Dashboard admin (T12)
- Creación de admin con `generate_password_hash` (T22)
- CSS/estilos (T20)
- Multi-admin, roles, permisos

## Capabilities

### New Capabilities
- `admin-login`: formulario y validación de acceso para administrador del sistema

### Modified Capabilities
None — capability nueva, independiente de `public-scholarship-listing` y `public-scholarship-detail`.

## Approach

```
controllers/auth.py         → Blueprint 'auth' url_prefix=''
  GET /admin/login           → render_template('login.html', error=None)
  POST /admin/login          → obtener username/password del form
                               get_by_username(db, username)
                               check_password_hash o None → error o session['admin_id']
                               redirect(url_for('auth.dashboard'))

templates/login.html         → extiende base.html
                               <h1>Acceso Administrador</h1>
                               form POST /admin/login
                               input username + input password + button "Ingresar"
                               {% if error %} mostrar mensaje
                               link "← Volver al inicio" → url_for('becas.listado')

app.py                       → from controllers.auth import auth_bp
                               app.register_blueprint(auth_bp)
```

Flujo GET/POST estándar: GET muestra el formulario limpio, POST valida contra DB. Si credenciales son incorrectas, se re-renderiza el template con el mensaje de error. Si son correctas, se guarda `admin_id` en la sesión y se redirige al dashboard (placeholder).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/auth.py` | New | Blueprint con ruta GET+POST /admin/login |
| `templates/login.html` | New | Formulario de login que extiende base.html |
| `app.py` | Modified | Importar y registrar Blueprint `auth` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SQL injection en username/password | Low | Placeholders `?` en `get_by_username()` |
| Redirect a dashboard inexistente (404) | Medium | Intencional hasta T12; no hay pérdida de datos ni seguridad |
| `SECRET_KEY` débil expone sesión | Low | Ya configurada en `app.py`, etiquetada para cambiar en producción |
| Admin sin seed → login siempre falla | Medium | T22 (seed/CLI) está planificada después; hasta entonces no hay admin que pueda loguearse |

## Rollback Plan

Revertir cambios en `app.py` (quitar registro del blueprint). Eliminar `controllers/auth.py` y `templates/login.html`. Ninguna data se pierde, la sesión no persiste porque no hay admin seed todavía.

## Dependencies

- T06 completada (`models/admin.py` con `get_by_username()` funcionando)
- `models/db.py` con `get_db()` funcionando
- `app.py` con `SECRET_KEY` configurada (T02)
- `templates/base.html` existente (T07)

## Success Criteria

- [ ] `GET /admin/login` renderiza formulario con inputs username (text) y password (password), botón "Ingresar", y link "← Volver al inicio"
- [ ] `POST /admin/login` con credenciales inválidas muestra mensaje "Usuario o contraseña incorrectos"
- [ ] `POST /admin/login` con credenciales válidas guarda `admin_id` en `session` y redirige a `/admin/dashboard`
- [ ] El error se muestra en la misma página del formulario (no redirect separado)
- [ ] Sin credenciales en `session`, el formulario se muestra limpio (sin error)
