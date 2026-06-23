# Proposal: T05 — Implementar modelo de becas (scholarships)

## Intent

Agregar la capa de acceso a datos para `scholarships` con funciones SQL explícitas. Es el puente entre la base ya creada (T04) y los controladores públicos/admin que vendrán (T07+). Sin esto, no hay forma de listar, buscar, crear o editar becas desde la app.

## Scope

### In Scope
- Archivo `models/scholarship.py` con funciones sueltas (sin clase wrapper)
- `get_by_id(id)` → devuelve `sqlite3.Row` o `None`
- `get_all(published_only=False)` → listado completo o solo publicadas
- `create(data)` → INSERT y devuelve el nuevo id
- `update(id, data)` → UPDATE con actualización automática de `updated_at`
- `delete(id)` → DELETE físico, sin soft delete
- `search(query)` → LIKE sobre title, institution, description

### Out of Scope
- Llamadas desde controladores o templates (T07+)
- Validaciones de negocio en el modelo (se harán en controladores)
- Migraciones o versionado de esquema
- Soft delete o lógica de archivado

## Capabilities

### New Capabilities
- `scholarship-data-access`: operaciones CRUD + búsqueda para la tabla `scholarships`

### Modified Capabilities
None — primera capability del proyecto.

## Approach

```
models/scholarship.py
├── get_by_id(id)         → SELECT * WHERE id = ?
├── get_all(published_only=False) → SELECT * [WHERE is_published = 1]
├── create(data)          → INSERT con dict de campos
├── update(id, data)      → UPDATE SET col=val, updated_at=CURRENT_TIMESTAMP
├── delete(id)            → DELETE WHERE id = ?
└── search(query)         → SELECT * WHERE title/institution/description LIKE ?
```

Todas las funciones reciben `db` como primer parámetro (inyección desde el controlador vía `get_db()`). SQL siempre explícito, sin ORM. `update()` sincroniza `updated_at` con SQL directo en el mismo statement.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `models/scholarship.py` | New | Archivo completo con 6 funciones de acceso a datos |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| SQL injection en search() | Low | Placeholders `?` en LIKE — concatenar `%` antes de pasar, no en el SQL |
| updated_at se desincronice | Low | `CURRENT_TIMESTAMP` inline en el UPDATE, no desde Python |

## Rollback Plan

Eliminar `models/scholarship.py`. Ninguna otra parte del sistema depende de él todavía. La base de datos no se modifica (solo se agrega código de acceso).

## Dependencies

- T04 completada (tabla `scholarships` existe en SQLite)
- `models/db.py` con `get_db()` funcionando

## Success Criteria

- [ ] `get_all()` devuelve todas las filas de scholarships
- [ ] `get_all(published_only=True)` filtra solo `is_published=1`
- [ ] `get_by_id(id)` devuelve la fila correcta; get_by_id(inexistente) devuelve None
- [ ] `create(data)` inserta y devuelve el id generado
- [ ] `update(id, data)` modifica campos y actualiza `updated_at`
- [ ] `delete(id)` elimina físicamente la fila
- [ ] `search("texto")` encuentra matches en title, institution o description
