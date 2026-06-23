# Proposal: T06 — Implementar modelo de admin (admin_users)

## Intent

Agregar la capa de acceso a datos para `admin_users` con funciones SQL explícitas. Es el puente entre la tabla ya creada (T04) y la lógica de autenticación que vendrá (T09-T11). Sin esto, no hay forma de verificar credenciales ni identificar al admin desde los controladores.

## Scope

### In Scope
- Archivo `models/admin.py` con funciones sueltas (sin clase wrapper)
- `get_by_username(db, username)` → `sqlite3.Row` o `None`
- `get_by_id(db, admin_id)` → `sqlite3.Row` o `None`
- `create(db, username, password_hash)` → INSERT y devuelve `lastrowid`
- Mismo estilo, documentación y convención que `models/scholarship.py`

### Out of Scope
- Lógica de hasheo de contraseñas (T22 con `werkzeug.security`)
- Lógica de login/sesión (T09-T11)
- Validaciones de negocio (T17)
- Multi-admin, roles, ownership de becas

## Capabilities

### New Capabilities
- `admin-user-data-access`: operaciones básicas de acceso a datos para la tabla `admin_users`

### Modified Capabilities
None — capability nueva, independiente de `scholarship-data-access`.

## Approach

```
models/admin.py
├── get_by_username(db, username) → SELECT * WHERE username = ?
├── get_by_id(db, admin_id)       → SELECT * WHERE id = ?
└── create(db, username, password_hash) → INSERT con lastrowid
```

Las tres funciones reciben `db` como primer parámetro (inyección desde el controlador vía `get_db()`). SQL explícito con placeholders `?`. Sin ORM. Sin clases. Sin hasheo. Idéntica convención a `scholarship.py`: docstring con Args/Returns, type hints en texto, `sqlite3.Row` como tipo de retorno.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `models/admin.py` | New | Archivo nuevo con 3 funciones de acceso a datos |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SQL injection en username | Low | Placeholders `?` en todas las queries |
| get_by_username(username) con caracteres especiales | Low | Parámetro como string plano, SQLite lo escapa con `?` |

## Rollback Plan

Eliminar `models/admin.py`. Ninguna otra parte del sistema depende de él todavía. La base de datos no se modifica (solo se agrega código de acceso).

## Dependencies

- T04 completada (tabla `admin_users` existe en SQLite)
- `models/db.py` con `get_db()` funcionando
- Convención de estilo establecida en `models/scholarship.py` (T05)

## Success Criteria

- [ ] `get_by_username(db, "admin")` devuelve la fila correcta
- [ ] `get_by_username(db, "inexistente")` devuelve `None`
- [ ] `get_by_id(db, 1)` devuelve la fila correcta
- [ ] `get_by_id(db, 999)` devuelve `None`
- [ ] `create(db, "admin", "hash")` inserta y devuelve el `lastrowid`
- [ ] El archivo `models/admin.py` sigue el mismo estilo (docstrings, tipo de retorno, nombres de parámetros) que `models/scholarship.py`
