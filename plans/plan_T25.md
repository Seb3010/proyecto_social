# Propuesta: T25 — Probar flujo admin — Login, alta y edición

## Intención

T09–T22 implementaron login, alta y edición de becas con sesión, hash de contraseñas y validaciones, pero no hay una verificación reproducible de que el flujo admin completo funcione correctamente. Sin esta tarea, cualquier regresión futura (refactor de rutas, cambio en modelos, modificación de decoradores) puede romper login, filtrar rutas protegidas, o perder datos sin detección hasta que alguien lo reporte en producción.

T25 no agrega funcionalidad nueva. Es una verificación automatizada del flujo admin completo: autenticación, protección de rutas, creación y edición de becas.

## Alcance

### Incluye
- Script de verificación `tests/test_admin_flow.py` que ejecuta los 13 casos contra la app via Flask test client
- Base SQLite temporal con el esquema real (`schema.sql`)
- Admin temporal creado con `generate_password_hash()` + `models.admin.create()`
- Beca de prueba creada via `POST /admin/becas/nueva`
- Verificación de: redirects sin sesión, login exitoso/fallido, dashboard, alta, edición, validaciones, logout
- Cleanup de base temporal al finalizar

### No incluye
- Modificar `controllers/auth.py`, `controllers/becas.py`, `models/*.py`, `app.py` ni templates
- Agregar pytest, `unittest` ni dependencias nuevas
- Probar el servidor en vivo con curl o selenium
- Probar rutas públicas (T24 ya las cubre)
- Probar borrado de becas (fuera del alcance del flujo actual)
- Modificar `instance/becas.sqlite` ni contraseñas reales

## Capacidades

### Nuevas capacidades
- `admin-flow-verification`: script de verificación del flujo completo de administración

### Capacidades modificadas
Ninguna. T25 es verificación, no modifica capacidades existentes.

## Estrategia

### Alternativa evaluada: pytest + fixtures
Requiere instalar pytest, crear `conftest.py`, fixtures para app/client/db. Sobredimensionado para una batería de 13 casos.

### Alternativa elegida: script plano con Flask test client
Mismo patrón que T24 (`tests/test_public_flow.py`): `app.test_client()`, cero dependencias nuevas, archivo independiente.

### Archivo destino
`tests/test_admin_flow.py` — separado del test público para mantener casos claros y ejecución independiente.

### Base de datos temporal
Usar `tempfile.mkstemp()` como T24: archivo `.db` en `/tmp/`, `app.config['DATABASE']` apunta a él, se aplica `schema.sql`, nunca toca `instance/becas.sqlite`.

### Creación del admin de prueba
NO se usa `flask create-admin` (CLI que opera sobre la base real). En su lugar:
```python
from werkzeug.security import generate_password_hash
from models.admin import create as create_admin
admin_id = create_admin(db, 'testadmin', generate_password_hash('testpass123'))
```
Esto evita efectos secundarios, no necesita `click.Context`, y es determinístico.

### Cliente de prueba y sesión
`app.test_client()` maneja cookies de sesión automáticamente entre requests. Para verificar contenido de flash messages se usa el stack de Flask: `session['_flashes']`.

### Verificación de redirects
Con `follow_redirects=False` se captura el status 302 y la Location. Con `follow_redirects=True` (default no) se sigue el redirect y se verifica el HTML destino.

## Casos de verificación

| # | Caso | Método | Ruta | Expected | Qué se verifica |
|---|------|--------|------|----------|-----------------|
| 1 | Setup | — | — | OK | DB temporal creada, esquema aplicado |
| 2 | Crear admin temporal | — | `create_admin()` | OK | Admin insertado con password_hash, no texto plano |
| 3 | Hash no es texto plano | — | `SELECT password_hash` | String ≠ pass | `check_password_hash()` lo valida, `password_hash` no es `testpass123` |
| 4 | Sin sesión → redirect login | `GET` | `/admin` | 302 → `/admin/login` | `@login_required` redirige |
| 5 | Login con creds incorrectas | `POST` | `/admin/login` | 200, flash error | No autentica, muestra error |
| 6 | Login con creds correctas | `POST` | `/admin/login` | 302 → `/admin` | Sesión creada, `admin_id` en session |
| 7 | Dashboard autenticado | `GET` | `/admin` | 200 | Panel responde OK |
| 8 | Alta con datos válidos | `POST` | `/admin/becas/nueva` | 302 → `/admin`, flash éxito | Beca creada en DB |
| 9 | GET edición precarga datos | `GET` | `/admin/becas/<id>/editar` | 200 | Formulario con título precargado |
| 10 | Edición persiste cambios | `POST` | `/admin/becas/<id>/editar` | 302 → `/admin`, flash éxito | Título/descripción cambiados en DB |
| 11 | POST con datos inválidos | `POST` | `/admin/becas/nueva` | 200, errores | Sin título → no persiste, muestra error |
| 12 | Logout limpia sesión | `POST` | `/admin/logout` | 302 → `/admin/login` | Sesión limpiada, no hay `admin_id` |
| 13 | Cleanup | — | — | OK | Archivo temporal eliminado |

## Archivos afectados

| Archivo | Impacto | Descripción |
|---------|---------|-------------|
| `tests/test_admin_flow.py` | Nuevo | Script de verificación del flujo admin con Flask test client |

No se modifica ningún archivo existente.

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| El test depende de que `app.py` sea importable sin efectos secundarios | Media | `app.py` ya es importable; `app.run()` solo se ejecuta si `__name__ == '__main__'` (verificado en T24) |
| Flash messages cambian de texto | Baja | Verificar por substring estable (ej. "correctamente") en lugar de texto exacto completo |
| La sesión se comporta distinto con `TESTING=True` | Baja | `app.config['TESTING'] = True` es práctica estándar de Flask; deshabilita errores catch por defecto |
| DB temporal no replica PRAGMAs de la real | Baja | `get_db()` ya configura `foreign_keys = ON` automáticamente |

## Plan de rollback

Eliminar `tests/test_admin_flow.py`. No hay cambios en rutas, modelos, base de datos ni configuraciones.

## Dependencias

- T09 (login admin + blueprint `auth`) — **completada**
- T14 (alta de beca: `POST /admin/becas/nueva`) — **completada**
- T16 (edición de beca: `POST /admin/becas/<id>/editar`) — **completada**
- T22 (hash de contraseñas con Werkzeug) — **completada**
- T24 (patrón de test con Flask client y base temporal) — **completada**

## Criterios de éxito

- [ ] `tests/test_admin_flow.py` existe y se ejecuta con `python tests/test_admin_flow.py`
- [ ] Los 13 casos pasan sin errores
- [ ] El script no modifica la base de datos real (`instance/becas.sqlite`)
- [ ] No se agregaron dependencias nuevas a `requirements.txt`
- [ ] No se modificó ningún archivo fuera de `tests/`

## Siguiente paso

Pasar a implementación (`sdd-apply`): crear `tests/test_admin_flow.py`, ejecutarlo, verificar los 13 casos, y marcar T25 como completada en `task_list.csv`.
