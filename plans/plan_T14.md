# Proposal: T14 — Guardar nueva beca: verificar persistencia en SQLite

## Intent

La ruta `POST /admin/becas/nueva` (T13) ya ejecuta `scholarship.create(db, data)` y redirige al dashboard. Sin embargo, no hay verificación formal de que los datos realmente persistan correctamente en SQLite. T14 cierra ese gap: ejecuta una prueba controlada que inserta, lee, verifica y limpia una beca de prueba, confirmando que el modelo CRUD funciona más allá del flujo HTTP.

## Scope

### In Scope
- Script inline de verificación que conecta a `instance/becas.sqlite`
- Inserta una beca de prueba con los 8 campos vía `scholarship.create()`
- Lee la beca insertada con `scholarship.get_by_id()`
- Verifica que los 8 campos coinciden exactamente
- Verifica que `is_published` se guarda como INTEGER (1/0)
- Verifica que `created_at` y `updated_at` se autogeneran con `CURRENT_TIMESTAMP`
- Verifica que `lastrowid` devuelve un entero positivo
- DELETE directo de la fila de prueba (cleanup)
- Resultado documentado en `plan_T14.md` y en Engram

### Out of Scope
- Modificar código de la app (la persistencia ya existe desde T13)
- Pruebas unitarias con unittest/pytest
- Validaciones de campos vacíos o formato (T17)
- Verificación de los triggers SQL de timestamps (se verifica por presencia, no por trigger)
- Verificación de la ruta HTTP completa (solo capa modelo + BD)

## Capabilities

### New Capabilities
- `scholarship-verification`: script de verificación end-to-end que confirma que `create()` + `get_by_id()` funcionan correctamente contra SQLite real

### Modified Capabilities
- `scholarship-data-access` (T05): se verifica formalmente que `create()` y `get_by_id()` cumplen su contrato; no hay cambios de código

## Approach

Ejecutar un script Python inline vía `.venv/bin/python` que:

1. Importa `create` y `get_by_id` de `models.scholarship`
2. Conecta a `instance/becas.sqlite` vía `models.db.get_db()`
3. Construye un dict con los 8 campos (incluye `is_published=1`)
4. Llama a `create(db, data)` y captura `lastrowid`
5. Llama a `get_by_id(db, lastrowid)` y compara campo por campo
6. Verifica que `created_at` y `updated_at` no sean `None`
7. Elimina la fila de prueba con `DELETE directo` vía `db.execute()`
8. Imprime resultados: PASS/FAIL por cada verificación

El script se ejecuta una sola vez. No se deja código permanente — es una verificación única.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `plans/plan_T14.md` | Modified | Se agrega esta sección con resultados tras ejecutar verificación |
| `instance/becas.sqlite` | Temporal | Una fila insertada y eliminada durante la verificación |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| La BD de instancia no existe o está vacía | Low | T04 ya la crea con schema. Si no existe, el script aborta con error claro. |
| El script deja la fila de prueba si falla el DELETE | Low | El cleanup es un DELETE directo; si falla, la fila queda huérfana con ID alto. Aceptable para MVP. |
| `get_db()` falla por path relativo | Low | El script se ejecuta desde la raíz del proyecto. Verificar `cwd` antes de ejecutar. |

## Rollback Plan

No hay rollback de código porque no se modifica código. Si la verificación falla, se documenta el error y se revisa el handler POST de T13 o el modelo de T05. La fila de prueba se limpia manualmente con `DELETE FROM scholarships WHERE title = 'Beca de prueba T14'`.

## Dependencies

- T04 completa (tabla `scholarships` existe en SQLite)
- T05 completa (`models/scholarship.py` con `create()` y `get_by_id()`)
- T13 completa (ruta POST existe — la verificación confirma que su lógica de persistencia funciona)
- `.venv/bin/python` accesible desde la raíz del proyecto
- `models/db.py` con `get_db()` funcionando

## Success Criteria

- [ ] `create(db, data)` inserta la fila y devuelve `lastrowid` como entero > 0
- [ ] `get_by_id(db, id)` recupera la fila con los 8 campos exactos
- [ ] `is_published` se persiste como INTEGER 1 (no string)
- [ ] `created_at` y `updated_at` tienen valores no nulos (autogenerados)
- [ ] DELETE directo limpia la fila de prueba sin errores
- [ ] Resultados documentados en este plan y en Engram
