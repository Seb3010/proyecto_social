# T23 — Estado publicación — Solo becas publicadas en vista pública

## Intención

Un visitante puede hoy buscar una beca borrador y verla en resultados, o acceder al detalle público de una beca no publicada si conoce su ID. Esto rompe la separación entre vista pública y admin. El cambio asegura que la vista pública muestre **solo becas publicadas** sin afectar el dashboard admin.

## Alcance

### Incluye
- Extender `models.scholarship.search()` con parámetro `published_only` para filtrar solo becas publicadas
- Pasar `published_only=True` desde `controllers.becas.buscar()`
- Bloquear el detalle público de becas borrador devolviendo 404 en `controllers.becas.detalle()`
- Verificar que dashboard admin siga mostrando todas las becas

### No incluye
- Cambiar el dashboard admin ni sus rutas (debe seguir viendo todo)
- Modificar login, templates, ni lógica de edición/creación
- Cambiar `get_all()` ni `get_by_id()` a nivel modelo
- Migraciones de base de datos

## Capacidades

### Nuevas capacidades
Ninguna. Todo es modificación de capacidades existentes.

### Capacidades modificadas
- `scholarship-model`: `search()` gana el parámetro `published_only`; comportamiento actual se mantiene por defecto (`published_only=False`)
- `becas-controller`: `buscar()` filtra por publicadas; `detalle()` rechaza borradores con 404

## Enfoque técnico

### 1) Filtrar búsqueda pública (`models/scholarship.py`)
Agregar parámetro `published_only` a `search()`. Si es `True`, se antepone `is_published = 1 AND` al WHERE.

### 2) Bloquear detalle de borradores (`controllers/becas.py`)
En `detalle()`, después de obtener la beca, verificar `is_published != 1` además de `None`. Unificar en un solo `if` con `or`.

### 3) Búsqueda pública filtrada (`controllers/becas.py`)
En `buscar()`, pasar `published_only=True` al llamar `search()`.

## Archivos afectados

| Archivo | Impacto | Descripción |
|---------|---------|-------------|
| `models/scholarship.py` | Modificado | `search()` acepta `published_only=False` y filtra cuando es `True` |
| `controllers/becas.py` | Modificado | `buscar()` pasa `published_only=True`; `detalle()` verifica `is_published` |
| `plans/plan_T23.md` | Nuevo | Esta propuesta |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Admin no ve borradores en búsqueda del dashboard | Baja | El dashboard no usa `search()`, usa `get_all()`; este cambio solo toca rutas públicas |
| Romper búsqueda admin si se reusa `search()` | Baja | `published_only=False` por defecto; ningún cambio en llamadas existentes |
| 404 en detalle de beca recién despublicada | Media | Comportamiento esperado; el admin usa rutas propias para ver borradores |

## Plan de rollback

Revertir cambios en `models/scholarship.py` y `controllers/becas.py`. No hay migraciones, cambios de esquema, ni nuevos archivos que limpiar.

## Dependencias

- T05 (modelo `scholarship.py` con `search()`) — completada
- T07 (controlador `becas.py` con rutas públicas) — completada

## Criterios de éxito

- [ ] `GET /` muestra solo becas con `is_published=1`
- [ ] `GET /buscar?q=...` muestra solo becas publicadas
- [ ] `GET /becas/<id>` devuelve 404 si la beca tiene `is_published=0`
- [ ] `GET /becas/<id>` funciona normalmente si la beca está publicada
- [ ] Dashboard admin (`/admin`) sigue mostrando todas las becas sin cambios

## Próximo paso

Pasar a `sdd-apply` o implementar directamente los cambios en `models/scholarship.py` y `controllers/becas.py`, verificar los criterios de éxito y marcar T23 como completada en `task_list.csv`.
