# Proposal: T19 — Estilos públicos con Tailwind CSS

## Intent

Las vistas públicas (listado y detalle de becas) de T07 y T08 se renderizan sin estilos — tipografía del navegador, layout raw. La app se ve inacabada. El equipo decidió adoptar Tailwind CSS v3+ compilado localmente para acelerar el prototipado sin romper la regla de no usar frameworks JS. T19 configura Tailwind por primera vez en el proyecto y aplica estilos a las templates públicas.

## Scope

### In Scope
- Inicializar `package.json` con `npm init`
- Instalar `tailwindcss@^3` como devDependency
- Crear `tailwind.config.js` escaneando `./templates/**/*.html`
- Crear `static/css/input.css` con las directivas `@tailwind`
- Agregar scripts `build:css` y `watch:css` a `package.json`
- Generar `static/css/output.css` con `npm run build:css`
- Modificar `templates/base.html`: link a `output.css`, clases Tailwind en `<body>`, flash messages
- Reescribir `templates/listado.html` con clases Tailwind (header, cards grid, búsqueda, estado vacío)
- Reescribir `templates/detalle.html` con clases Tailwind (layout, campos, link externo)
- Agregar `node_modules/` a `.gitignore`

### Out of Scope
- Estilos del dashboard/admin (T20)
- JavaScript del frontend (T21)
- Tailwind por CDN (solo compilado local)
- Cambiar estructura Flask, rutas, modelos o BD
- Plugins Tailwind ni configuraciones de tema avanzadas

## Capabilities

### New Capabilities
- `tailwind-setup`: configuración inicial de Tailwind CLI + build pipeline para el proyecto
- `estilos-publicos`: estilos basados en utilidades Tailwind para las vistas públicas

### Modified Capabilities
- `public-scholarship-listing` (T07): requiere link a output.css + clases en templates
- `public-scholarship-detail` (T08): requiere link a output.css + clases en templates

## Approach

**Fase 1 — Setup Tailwind (primera vez en el proyecto)**

```
npm init -y                                  → package.json
npm install -D tailwindcss@^3                → node_modules/ + lockfile
npx tailwindcss init                         → tailwind.config.js
```

Configurar `tailwind.config.js` apuntando a `./templates/**/*.html`.
Crear `static/css/input.css` con:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Scripts en `package.json`:

```json
"scripts": {
  "build:css": "tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify",
  "watch:css": "tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch"
}
```

Ejecutar `npm run build:css` para generar `static/css/output.css`.

**Fase 2 — Aplicar clases a templates**

- `base.html`: link a `output.css`, `bg-gray-50 text-gray-900`, main centrado, flash messages con colores según categoría
- `listado.html`: grid de cards con `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3`, formulario de búsqueda inline, badge "Borrador", estado vacío con icono/texto centrado
- `detalle.html`: layout apilado con secciones, tipografía clara, link externo con icono

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `package.json` | New | npm init + tailwindcss devDep + build scripts |
| `tailwind.config.js` | New | Content paths a templates |
| `static/css/input.css` | New | Directivas @tailwind base/components/utilities |
| `static/css/output.css` | New | Generado por `npm run build:css` |
| `templates/base.html` | Modified | +link output.css, clases Tailwind en body y flash |
| `templates/listado.html` | Modified | Reescribir clases con Tailwind |
| `templates/detalle.html` | Modified | Reescribir clases con Tailwind |
| `.gitignore` | Modified | +`node_modules/` |
| `package-lock.json` | New | Lockfile de npm |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `output.css` queda out of sync si se editan templates sin rebuild | Media | Documentar `npm run build:css` como paso obligatorio; `watch:css` para dev |
| `node_modules/` olvidado en `.gitignore` | Baja | Ya incluido en esta propuesta |
| output.css inicial ~30-50KB impacta tiempo de carga | Baja | Minificado con `--minify`, una sola solicitud HTTP, cacheable |
| Tailwind purge no detecta clases dinámicas construidas con strings | Baja | Usar clases completas en templates, no concatenación dinámica |

## Rollback Plan

Eliminar `package.json`, `tailwind.config.js`, `static/css/input.css`, `static/css/output.css`, `package-lock.json`, `node_modules/`. Revertir cambios en templates. Las templates vuelven a funcionar sin estilos como antes.

## Dependencies

- T07 y T08 completas (templates `listado.html` y `detalle.html` existen)
- Node.js y npm instalados en el entorno de desarrollo

## Success Criteria

- [ ] `npm run build:css` ejecuta sin errores
- [ ] `static/css/output.css` existe y es CSS minificado
- [ ] El listado se ve con grid de cards, espaciado y tipografía Tailwind
- [ ] El detalle tiene layout limpio con secciones diferenciadas
- [ ] La búsqueda está estilizada (input + botón inline)
- [ ] Los flashes tienen color según categoría (verde success, rojo error, azul info)
- [ ] El badge "Borrador" se distingue visualmente
- [ ] Sin resultados → mensaje informativo en lugar de raw text
- [ ] No hay regresión visual en templates admin (T20)
- [ ] `node_modules/` está en `.gitignore` y no se comitea
