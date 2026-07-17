# Proposal: T20 — Estilos admin con Tailwind CSS

## Intent

Los templates admin (`login.html`, `dashboard.html`, `nueva_beca.html`) se renderizan como HTML crudo sin estilos — heredan solo el `bg-gray-50` del body de `base.html`. La interfaz admin se ve inacabada respecto a las vistas públicas ya estilizadas en T19. T20 aplica clases utilitarias Tailwind a los tres templates admin para lograr consistencia visual en todo el sitio.

## Scope

### In Scope
- Estilizar `templates/login.html`: card centrada con form de acceso, inputs con focus ring, botón azul, link de volver
- Estilizar `templates/dashboard.html`: header con título + botón "Nueva beca" + cerrar sesión, tabla con estados (Publicado/Borrador) como badges, estado vacío, acciones "Editar"
- Estilizar `templates/nueva_beca.html` (dual crear/editar): form completo con todos los campos, checkbox "Publicar inmediatamente", botón submit con label dinámico, errores de validación en box rojo, cancelar
- Recompilar `static/css/output.css` con `npm run build:css` para que Tailwind detecte las clases nuevas

### Out of Scope
- Modificar `templates/base.html` (ya estilizado en T19)
- Modificar templates públicos `listado.html` y `detalle.html` (ya estilizados en T19)
- Código Python (controllers, models, routes, app.py)
- AGENTS.md, plan.md, o cualquier archivo de documentación
- JavaScript del frontend
- Plugins Tailwind, config de tema, o vanilla CSS adicional

## Capabilities

> No hay directorio `openspec/` en el proyecto. No existen archivos de spec formales. Las capabilities se listan como referencia para la fase de tasks.

### New Capabilities
- `estilos-admin`: clases utilitarias Tailwind para las tres vistas del panel administrativo

### Modified Capabilities
- `admin-login` (T13 — auth/login): requiere clases Tailwind en form, card, inputs, botón
- `admin-dashboard` (T12 — dashboard admin): requiere clases Tailwind en header, tabla, badges, estado vacío
- `admin-scholarship-form` (T13/T15 — crear/editar beca): requiere clases Tailwind en form completo, errores, checkbox

## Approach

Mismo approach que T19: clases utilitarias Tailwind inline en cada template. Sin vanilla CSS adicional. Sin archivo separado — `output.css` ya cubre todo el sitio.

**Orden de aplicación:**

1. **login.html** — card centrada con `max-w-md mx-auto mt-12`, form `space-y-4`, inputs con `focus:ring-2 focus:ring-blue-500`, botón azul `w-full`
2. **dashboard.html** — header `flex items-center justify-between`, tabla `min-w-full` con `divide-y`, badges de estado con colores (verde/amarillo), estado vacío centrado
3. **nueva_beca.html** — form `max-w-2xl mx-auto`, todos los campos con clases consistentes, checkbox stylizado, errores en `bg-red-100`, layout de botones submit/cancelar
4. **Rebuild** — `npm run build:css` para que Tailwind escanee las nuevas clases y las incluya en `output.css`

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `templates/login.html` | Modified | +clases Tailwind en card, form, inputs, botón, link |
| `templates/dashboard.html` | Modified | +clases Tailwind en header, tabla, badges, estado vacío |
| `templates/nueva_beca.html` | Modified | +clases Tailwind en form completo, errores, checkbox |
| `static/css/output.css` | Modified | Rebuild para incluir nuevas clases detectadas |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| output.css no incluye clases nuevas por no rebuildear | Baja | `npm run build:css` documentado como paso obligatorio; verify con checklist |
| Clases Tailwind dinámicas (ej. `"bg-"+color`) no detectadas por purge | Baja | Todas las clases son literales completas en templates, no concatenadas |
| Regresión visual en templates públicos por rebuild | Baja | T19 ya probado; rebuild solo agrega clases, no las saca |
| Templates admin existentes tenían algo de HTML no estandar | Baja | Se respeta estructura actual, solo se agregan clases |

## Rollback Plan

Revertir `templates/login.html`, `templates/dashboard.html` y `templates/nueva_beca.html` al estado anterior (con `git checkout`). Si el output.css queda corrupto, regenerar con `npm run build:css` desde la rama anterior o restaurar el archivo previo.

## Dependencies

- T19 completada (Tailwind configurado, output.css generado, base.html con link)
- T12, T13, T15 completas (templates admin existen con su estructura HTML)
- Node.js y npm disponibles para rebuild

## Success Criteria

- [ ] `npm run build:css` sin errores
- [ ] `/admin/login` muestra card centrada con form estilizado, inputs con focus ring, botón azul
- [ ] `/admin` muestra header con título + "Nueva beca" + "Cerrar sesión", tabla con badges de estado
- [ ] `/admin/becas/nueva` muestra form estilizado con todos los campos
- [ ] `/admin/becas/<id>/editar` muestra form con datos precargados
- [ ] Errores de validación se muestran en box rojo arriba del form
- [ ] Botón "Admin/Ingresar" sigue arriba a la derecha (heredado de base.html, sin cambios)
- [ ] Sin becas → mensaje informativo centrado en lugar de raw text
- [ ] No hay regresión visual en templates públicos (T19)
