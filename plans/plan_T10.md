# Proposal: T10 — Implementar logout admin

## Intent

Cerrar sesión de admin de forma segura. Sin logout, el admin no puede salir del sistema — quedaría autenticado hasta que expire la sesión del navegador. Un solo endpoint POST resuelve el vacío entre login (T09) y la protección de rutas (T11).

## Scope

### In Scope
- `controllers/auth.py` — agregar ruta `POST /admin/logout` en Blueprint `auth`
- Llamar `session.clear()` para eliminar todos los datos de sesión
- Redirigir a `url_for('auth.login')` después del logout

### Out of Scope
- Proteger rutas admin con `@login_required` (T11)
- Dashboard admin (T12)
- Confirmación visual de logout (mensajes flash — T18)
- Logout GET (intencional: solo POST para evitar cierre accidental por precarga/link)

## Capabilities

### New Capabilities
None — el logout es extensión de la capability `admin-login`.

### Modified Capabilities
- `admin-login`: se añade la ruta `POST /admin/logout` con limpieza de sesión y redirect. El nombre de la capability se actualiza semánticamente a "autenticación admin" (login + logout).

## Approach

```
controllers/auth.py (modificar)
  POST /admin/logout          → session.clear()
                                redirect(url_for('auth.login'))
```

El logout es POST obligatorio. No hay template nuevo: el usuario vuelve al formulario de login limpio. La ruta existe aunque todavía no haya `@login_required` protegiendo las rutas admin — eso llega en T11.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/auth.py` | Modified | Agregar ruta `logout()` al Blueprint `auth` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|-------------|
| Logout GET accidental por escaneo de rutas | Low | Sólo POST aceptado; GET devuelve 405 automáticamente |
| `session.clear()` elimina datos útiles | Low | No hay otros datos de sesión en MVP; `session.pop('admin_id')` es alternativa válida pero `clear()` es más robusto |
| Logout sin login previo | Low | `session.clear()` es seguro aunque no haya sesión activa |

## Rollback Plan

Revertir el diff en `controllers/auth.py`: eliminar método `logout()` y su registro de ruta. No hay datos que perder ni migraciones que deshacer.

## Dependencies

- T09 completada (Blueprint `auth` existe y funciona)
- `app.py` con `SECRET_KEY` configurada (T02)

## Success Criteria

- [ ] `POST /admin/logout` limpia `session` y redirige a `/admin/login`
- [ ] `GET /admin/logout` devuelve `405 Method Not Allowed`
- [ ] Después del logout, intentar acceder a cualquier ruta admin (T11+) redirige a login (se verifica con T11)
- [ ] El código fuente usa `session.clear()` (no `session.pop` a menos que se justifique)
