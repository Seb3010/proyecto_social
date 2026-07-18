# Task List — BecaSocial MVP

> `[x]` = completada · `[ ]` = pendiente

---

## Base de Datos

- [x] **T01** — Crear estructura MVC base — Carpetas `controllers/`, `models/`, `templates/`, `static/`, `instance/`
- [x] **T02** — Crear entrypoint Flask — `app.py` con configuración inicial _(depende: T01, prioridad: alta)_
- [x] **T03** — Configurar sqlite3 — Conexión básica con `sqlite3` estándar _(depende: T02, prioridad: alta)_
- [x] **T04** — Crear esquema inicial — Tablas `scholarships` y `admin_users` _(depende: T03, prioridad: alta)_

## Modelos

- [x] **T05** — Modelo de becas — CRUD + search para `scholarships` _(depende: T04, prioridad: alta)_
- [x] **T06** — Modelo de admin — `get_by_username`, `get_by_id`, `create` _(depende: T04, prioridad: alta)_

## Vista Pública

- [x] **T07** — Crear listado público — Ruta y template para becas publicadas _(depende: T05, prioridad: alta)_
- [x] **T08** — Crear detalle público — Ruta y template para detalle de beca _(depende: T05, prioridad: alta)_

## Autenticación

- [x] **T09** — Login admin — Formulario y validación de acceso _(depende: T06, prioridad: alta)_
- [x] **T10** — Logout admin — Cerrar sesión de forma segura _(depende: T09, prioridad: media)_
- [x] **T11** — Proteger rutas admin — Control de sesión para rutas privadas _(depende: T09, prioridad: alta)_

## Panel Admin

- [x] **T12** — Dashboard admin — Vista inicial del panel _(depende: T11, prioridad: media)_
- [x] **T13** — Formulario nueva beca — Vista y ruta para alta _(depende: T11, prioridad: alta)_
- [x] **T14** — Guardar nueva beca — Procesar formulario y persistir en SQLite _(depende: T13, prioridad: alta)_
- [x] **T15** — Formulario editar beca — Vista y ruta para editar _(depende: T11, prioridad: alta)_
- [x] **T16** — Actualizar beca — Procesar formulario y actualizar en SQLite _(depende: T15, prioridad: alta)_

## Validación y UX

- [x] **T17** — Validaciones básicas — Campos requeridos y formatos mínimos _(depende: T14|T16, prioridad: media)_
- [x] **T18** — Mensajes flash — Éxito y error en login y formularios _(depende: T09|T14|T16, prioridad: media)_

## Estilos

- [x] **T19** — Estilos públicos — CSS para listado y detalle _(depende: T07|T08, prioridad: baja)_
- [x] **T20** — Estilos admin — CSS para login, dashboard y formularios _(depende: T12|T13|T15, prioridad: baja)_
- [x] **T21** — JS mínimo — Vanilla JS solo si hace falta _(depende: T19|T20, prioridad: baja)_

## Seguridad

- [x] **T22** — Hash contraseñas — Almacenar password con hash seguro _(depende: T09, prioridad: alta)_
- [x] **T23** — Estado publicación — Solo becas publicadas en vista pública _(depende: T05|T07, prioridad: alta)_

## Verificación

- [x] **T24** — Probar flujo público — Listado y detalle de becas _(depende: T07|T08|T23, prioridad: media)_
- [x] **T25** — Probar flujo admin — Login, alta y edición _(depende: T09|T14|T16|T22, prioridad: media)_
