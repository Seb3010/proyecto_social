# Proposal: T11 — Proteger rutas admin con decorador de sesión

## Intent

Sin esta tarea, cualquiera que conozca una URL admin (ej. `/admin/dashboard`) puede acceder sin autenticarse. Necesitamos un mecanismo de guarda que se aplique a todas las rutas admin futuras (T12+). El decorador `login_required` es esa guarda: liviana, reutilizable, y que no toca las rutas públicas.

## Scope

### In Scope
- `controllers/decorators.py` — archivo nuevo con decorador `login_required`
- Importar decorador desde `auth.py` para la ruta `logout` (POST)
- Logout redirige a login incluso sin sesión activa (safe-by-default)

### Out of Scope
- Dashboard admin (T12)
- CRUD admin (T13-T16)
- Mensajes flash (T18)
- CSS (T20)
- Decorador `admin_required` con verificación de rol

## Capabilities

### New Capabilities
- `admin-auth-guard`: decorador `login_required` que verifica `session['admin_id']` antes de ejecutar cualquier ruta protegida

### Modified Capabilities
None — capability nueva, independiente de `admin-login`.

## Approach

Opción B — archivo separado `controllers/decorators.py`:

```python
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
```

Razones para archivo separado:
- `auth.py` queda limpio: solo rutas (login, logout)
- `decorators.py` puede crecer con más decoradores sin acoplar
- Se importa desde cualquier controller sin riesgo de ciclos

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/decorators.py` | New | Decorador `login_required` con verificación de sesión |
| `controllers/auth.py` | Modified | Importar y aplicar `@login_required` a `logout()` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Olvidar aplicar decorador en rutas admin nuevas | Medium | Convención de equipo: toda ruta admin nueva arranca con `@login_required` |
| Redirect loop si login no tiene `@login_required` | Low | El decorador NO se aplica a `login()` — explícito en el diseño |
| Sesión expirada pierde datos de formulario | Low | Fuera de scope hasta T18 (flash messages) |

## Rollback Plan

Eliminar `controllers/decorators.py`. Revertir import en `auth.py`. Las rutas admin aún no existen, no hay nada que desproteger.

## Dependencies

- T09 completa (`session['admin_id']` se setea en login)
- `SECRET_KEY` configurada en `app.py`
- Flask `session` importable

## Success Criteria

- [ ] `controllers/decorators.py` existe con `login_required` importable
- [ ] Decorador redirige a `auth.login` si no hay `admin_id` en sesión
- [ ] Decorador NO interfiere con rutas públicas (becas)
- [ ] Logout funciona sin sesión activa (safe)
- [ ] Importar decorador en cualquier controller nuevo no produce ciclos
