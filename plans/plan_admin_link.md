# Proposal: Admin Link Button in Public Views

## Intent

Las vistas públicas (listado, detalle) no exponen acceso al admin. El único admin debe tipear `/admin/login` en la URL. Esto se detectó durante pruebas post-T19. El cambio agrega un botón visible en la esquina superior derecha de todas las páginas públicas que linkea a login (no autenticado) o al dashboard (autenticado).

## Scope

### In Scope

- Agregar un `<a>` en `templates/base.html` con link condicional según sesión
- Usar `session.get('admin_id')` directo en Jinja — Opción A (DRY, no toca endpoints)
- Posicionar el botón en la esquina superior derecha (absoluto dentro de body relativo)
- Estilo Tailwind coherente con T19 existente
- Compilar `output.css` con `npm run build:css`

### Out of Scope

- Modificar templates de admin (dashboard, login, nueva_beca, editar_beca)
- Modificar controladores, modelos, o rutas Flask
- Agregar lógica JS
- Cambiar el sistema de autenticación existente

## Capabilities

### New Capabilities

- `admin-link-public`: botón de acceso admin desde las vistas públicas

### Modified Capabilities

- `estilos-publicos` (T19): requiere recompilar CSS para incluir nuevas clases

## Approach

Único cambio: en `templates/base.html`, agregar un `<a>` como primer hijo del `<body>`, con posición absoluta en la esquina superior derecha:

```html
<body class="bg-gray-50 text-gray-900 min-h-screen relative">
    <a href="{{ url_for('auth.dashboard') if session.get('admin_id') else url_for('auth.login') }}"
       class="absolute top-4 right-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm">
        {% if session.get('admin_id') %}Admin{% else %}Ingresar{% endif %}
    </a>
    ...
```

Usar `bg-blue-600` en lugar de `bg-indigo-600` porque **ya está compilado en output.css** y es el mismo color primario del resto del sitio (botones de búsqueda, volver). Esto evita agregar clases nuevas innecesarias al CSS.

Clases nuevas que requiere este cambio (`relative`, `absolute`, `top-4`, `right-4`) → compilar con `npm run build:css`.

**Por qué Opción A (session.get en Jinja)**: Flask expone `session` como global de template automáticamente. No requiere modificar ningún endpoint público. Es estrictamente más DRY que pasar `admin` desde cada ruta.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `templates/base.html` | Modified | +`<a>` botón admin en esquina sup. der. |
| `static/css/output.css` | Modified | Recompilar con nuevas clases (`relative`, `absolute`, `top-4`, `right-4`) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|-------------|
| Olvidar recompilar CSS → botón sin posición/estilo | Baja | Incluir `npm run build:css` en los pasos; verificar visualmente |
| `session` no disponible en Jinja | Muy baja | Flask la inyecta por defecto; verificar con template sin endpoint modificado |
| El botón tapa contenido en responsive | Baja | `top-4 right-4` deja margen; en mobile el main tiene `px-4 py-8` visible |

## Rollback Plan

Revetir el cambio en `templates/base.html` y recompilar `output.css`. El botón desaparece sin afectar nada más. No hay cambios en BD, rutas, ni controladores.

## Dependencies

- `npm run build:css` ejecutable (Tailwind CLI configurado en T19)
- auth Blueprint existente con rutas `auth.login` y `auth.dashboard`

## Success Criteria

- [ ] Botón aparece en listado público (/) y detalle público (/beca/<id>)
- [ ] Sin sesión activa: botón dice "Ingresar" → click → `/admin/login`
- [ ] Con sesión activa (admin_id): botón dice "Admin" → click → `/admin`
- [ ] Botón visible en esquina superior derecha
- [ ] Estilo Tailwind consistente con el resto del sitio
- [ ] `npm run build:css` ejecuta sin errores
- [ ] No hay regresión en templates admin
- [ ] Ningún endpoint público fue modificado
