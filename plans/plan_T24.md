# Propuesta: T24 — Probar flujo público — Listado y detalle de becas

## Intención

T23 implementó la restricción de publicación en las rutas públicas, pero no hay una verificación reproducible de que el flujo público respete esa restricción. Sin esta tarea, cualquier regresión futura (un refactor, un cambio inadvertido en `scholarship.py`) puede filtrar borradores al público sin que nadie lo detecte hasta que un usuario lo reporte.

T24 no agrega funcionalidad nueva. Es una verificación automatizada del contrato: el público solo ve becas publicadas.

## Alcance

### Incluye
- Script de verificación (`tests/test_public_flow.py`) que ejecuta los 8 casos contra la app via Flask test client
- Datos de prueba controlados (una beca publicada, una borrador)
- Verificación de códigos HTTP y presencia/ausencia de títulos en HTML
- Validación adicional vía modelo de que el dashboard admin sigue viendo ambas becas
- Cleanup de los datos de prueba al finalizar

### No incluye
- Modificar `controllers/becas.py`, `models/scholarship.py` ni ningún archivo de ruta/modelo
- Agregar estilos, JS, templates ni funcionalidades
- Probar login, creación o edición admin (T25)
- Agregar pytest ni otros frameworks de testing

## Capacidades

### Nuevas capacidades
- `public-flow-verification`: script de verificación del flujo público de becas

### Capacidades modificadas
Ninguna. T24 es verificación, no modifica capacidades existentes.

## Estrategia de verificación

### Alternativa evaluada: pytest + Flask test client
Requiere instalar pytest, agregarlo a `requirements.txt`, crear `conftest.py` con fixtures. Sobredimensionado para una batería de 8 casos.

### Alternativa elegida: script plano con Flask test client
Usar `app.test_client()` directamente. El entrypoint (`app.py`) importa `app` como variable global, así que el test puede importarlo sin tocar la estructura del proyecto. Un solo archivo, cero dependencias nuevas.

### Archivo destino
`tests/test_public_flow.py` — no requiere `__init__.py` porque no es un paquete, se ejecuta con `python tests/test_public_flow.py`.

### Manejo de base de datos
Usar una base temporal en memoria (`:memory:`) o un archivo SQLite en `/tmp/` creado y destruido por el script. La app soporta `DATABASE` configurable, así que sobreescribimos `app.config['DATABASE']` antes de iniciar las pruebas para no tocar la base real (`instance/becas.sqlite`).

### Datos de prueba
El script crea dos becas vía `models.scholarship.create()` directamente:
1. **Beca A** — `is_published=1`, título unique como `"Beca Publicada T24"`
2. **Beca B** — `is_published=0`, título unique como `"Beca Borrador T24"`

Esto evita depender del estado actual de la base y hace el test determinístico.

### Verificación de contenido HTML
Se revisa que el título de la beca publicada **aparezca** en el body de la respuesta y que el título de la beca borrador **no aparezca**. Esto es suficiente porque los templates (`listado.html`, `detalle.html`) interpolar `{{ beca.title }}` directamente. No se usan selectores CSS, XPath ni scraping.

### Dashboard admin
Se verifica a nivel de modelo (`get_all(db)` sin filtro devuelve 2 registros) para confirmar que la restricción de publicación no filtró datos del admin. No se prueba HTTP del dashboard porque requiere sesión y convertiría T24 en una prueba admin.

## Casos de verificación

| # | Caso | Método | Ruta | Expected | Qué se verifica |
|---|------|--------|------|----------|-----------------|
| 1 | Setup | — | — | OK | Se crean beca publicada + borrador en base temporal |
| 2 | Listado público | `GET` | `/` | 200 | Beca publicada visible, borrador ausente |
| 3 | Búsqueda coincide publicada | `GET` | `/buscar?q=Beca Publicada` | 200 | Beca publicada visible en resultados |
| 4 | Búsqueda no muestra borrador | `GET` | `/buscar?q=Beca Borrador` | 200 | Borrador ausente de resultados (ni siquiera si coincide textualmente) |
| 5 | Detalle de publicada | `GET` | `/becas/<id-publicada>` | 200 | Título de la beca visible |
| 6 | Detalle de borrador | `GET` | `/becas/<id-borrador>` | 404 | Página de error |
| 7 | Detalle de ID inexistente | `GET` | `/becas/99999` | 404 | Página de error |
| 8 | Admin sigue viendo ambas | — | `get_all(db)` | 2 registros | Modelo no filtró; ambas existen |
| 9 | Cleanup | — | — | OK | Base temporal eliminada |

## Archivos afectados

| Archivo | Impacto | Descripción |
|---------|---------|-------------|
| `tests/test_public_flow.py` | Nuevo | Script de verificación con Flask test client |

No se modifica ningún archivo existente.

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| El script se vuelve frágil si cambian los templates | Baja | Solo verifica presencia/ausencia de texto, no estructura HTML |
| La base temporal en `:memory:` no replica el mismo PRAGMA que la real | Baja | El script aplica `PRAGMA foreign_keys = ON` y el mismo esquema |
| El test depende de que `app.py` sea importable sin efectos secundarios | Media | `app.py` ya es importable; `app.run(debug=True)` solo se ejecuta si `__name__ == '__main__'` |

## Plan de rollback

Eliminar `tests/test_public_flow.py`. No hay cambios en rutas, modelos, base de datos ni configuraciones.

## Dependencias

- T07 (controlador `becas.py` con rutas públicas) — completada
- T08 (template `detalle.html`) — completada
- T23 (restricción de publicación) — completada (verificar que el código refleje los cambios)

## Criterios de éxito

- [ ] `tests/test_public_flow.py` existe y se ejecuta con `python tests/test_public_flow.py`
- [ ] Los 8 casos pasan sin errores
- [ ] El script no modifica la base de datos real (`instance/becas.sqlite`)
- [ ] No se agregaron dependencias nuevas a `requirements.txt`
- [ ] No se modificó ningún archivo fuera de `tests/`

## Siguiente paso

Pasar a implementación (`sdd-apply`): crear `tests/test_public_flow.py`, ejecutarlo, verificar los 8 casos, y marcar T24 como completada en `task_list.csv`.
