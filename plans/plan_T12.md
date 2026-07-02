# Proposal: T12 — Dashboard admin (vista inicial del panel)

## Intent

El admin necesita una landing page post-login donde pueda ver el estado del sistema de un vistazo: qué becas existen, cuáles están publicadas y cuáles en borrador, y desde dónde lanzar las acciones de crear o editar. Sin esta vista, después del login el usuario cae a un redirect sin destino (T09 redirige a `auth.dashboard`, que aún no existe).

## Scope

### In Scope
- Ruta `GET /admin` en Blueprint `auth` protegida con `@login_required`
- Template `templates/dashboard.html` con listado completo de becas
- Tabla con columnas: Título (link a vista pública), Estado (Publicado/Borrador), Acciones (Editar)
- Header con nombre del admin logueado y botón de cerrar sesión
- Botón "+ Nueva beca" (link a ruta futura T13)
- Mensaje "No hay becas todavía" si la lista está vacía
- Mostrar TODAS las becas (get_all sin filtro), no solo las publicadas
- Template HTML sin CSS (T20 se encarga)

### Out of Scope
- Formulario nueva beca (T13)
- Formulario editar beca (T15)
- Mensajes flash de éxito/error (T18)
- Estilos CSS (T20)
- Funcionalidad de borrar becas
- Paginación o filtros

## Capabilities

### New Capabilities
- `admin-dashboard`: ruta `GET /admin` protegida que lista todas las becas con estado y acciones, y muestra identidad del admin logueado

### Modified Capabilities
- `admin-auth-guard`: la ruta `auth.logout` ya usa `@login_required`; `dashboard()` también lo usará

## Approach

Agregar ruta `dashboard()` en `controllers/auth.py` entre login y logout. Usa `get_all(db)` de `models/scholarship.py` (sin filtro) y `get_by_id(db)` de `models/admin.py` (ya importado en T09). Template nuevo que extiende `base.html` y renderiza tabla simple con Jinja2.

El redirect desde login (T09) ya apunta a `url_for('auth.dashboard')` — esta tarea completa ese enlace.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `controllers/auth.py` | Modified | Agregar import `from models.scholarship import get_all`, nueva ruta `dashboard()` con `@login_required` |
| `templates/dashboard.html` | New | Template que extiende `base.html`, header admin, tabla de becas, botones de acción |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|-------------|
| Ruta nueva en auth_bp usa `/admin` y podría colisionar con futuras rutas admin | Low | El blueprint 'auth' ya tiene las rutas admin (`/admin/login`, `/admin/logout`). Convención documentada: rutas admin van en auth_bp hasta que se justifique separar. |
| `url_for('becas.detalle')` redirige a vista pública — admin puede ver becas no publicadas | Low | Intencional: el admin necesita previsualizar. El controlador `becas.detalle` ya renderiza sin filtrar por publicación (solo la vista pública lista filtra). Verificar que `becas.detalle` no filtre por `is_published`. |

## Rollback Plan

Eliminar ruta `dashboard()` y archivo `dashboard.html`. El login redirigirá a `auth.dashboard` y dará 404 — habrá que reemplazar el redirect de T09 temporalmente por `url_for('becas.listado')` hasta restaurar.

## Dependencies

- T11 completa (`@login_required` disponible)
- `get_all(db)` sin filtro existe desde T05
- `get_by_id(db)` para admin existe desde T06
- `base.html` existe desde T07
- `url_for('becas.detalle', beca_id=...)` existe desde T08

## Success Criteria

- [ ] `GET /admin` sin sesión redirige a login (por `@login_required`)
- [ ] `GET /admin` con sesión activa muestra nombre del admin y tabla de becas
- [ ] Tabla muestra todas las becas (publicadas y borradores)
- [ ] Cada beca tiene link a vista pública (`becas.detalle`) y link a editar (`auth.editar_beca`)
- [ ] Aparece botón "+ Nueva beca" que linkea a `auth.nueva_beca` (aunque dé 404 hasta T13)
- [ ] Aparece botón "Cerrar sesión" que hace POST a `auth.logout`
- [ ] Si no hay becas, se muestra "No hay becas todavía"
- [ ] Sin CSS, el HTML es funcional y semántico
