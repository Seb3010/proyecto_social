# Plan Inicial MVP

## Objetivo
- Construir una app web monolitica para mostrar becas disponibles.
- Usar arquitectura MVC.
- Mantener el frontend con `HTML`, `CSS` (con Tailwind CSS compilado localmente) y `vanilla JS` lo mas basico posible.
- Mantener el backend con `Python`, `Flask` y `sqlite3` directo, sin ORM.

## Alcance del MVP
- Vista publica con listado de becas.
- Vista publica con detalle de cada beca.
- Login solo para admin.
- Panel admin separado de la vista publica.
- Admin puede crear y editar becas publicadas.

## Restricciones tecnicas
- Una excepcion a la regla "no frameworks de frontend": Tailwind CSS v3+ se permite porque el equipo lo aprendio y decidio sumarlo. Compila localmente via npm/npx (script `npm run build:css`). Tailwind CLI se ejecuta local, no se usa el CDN. Requiere `node_modules/` y un script de build.
- Sin otros frameworks de frontend (Bootstrap, Vue, React, etc.) ni librerias externas de JS.
- No usar ORM.
- Acceso a base de datos con `sqlite3` de la libreria estandar.
- Escribir SQL de forma explicita.
- Evitar capas innecesarias o abstracciones que oculten la logica.

## Modelo inicial de datos

### Tabla `scholarships`
- `id`
- `title`
- `institution`
- `description`
- `requirements`
- `deadline`
- `location`
- `link`
- `is_published`
- `created_at`
- `updated_at`

### Tabla `admin_users`
- `id`
- `username`
- `password_hash`

## Estructura MVC sugerida
- `app.py` o `run.py` como entrypoint.
- `controllers/` para rutas y flujo HTTP.
- `models/` para acceso a datos con `sqlite3`.
- `templates/` para vistas HTML renderizadas por Flask.
- `static/css/` para estilos.
- `static/js/` para comportamiento minimo del frontend.
- `instance/` o `database/` para el archivo SQLite.

## Flujos principales

### Publico
- `GET /` listado de becas publicadas.
- `GET /becas/<id>` detalle de beca.

### Admin
- `GET/POST /admin/login`
- `GET /admin`
- `GET/POST /admin/becas/nueva`
- `GET/POST /admin/becas/<id>/editar`
- `POST /admin/logout`

## Orden de implementacion
1. Crear la estructura base del proyecto Flask.
2. Configurar la conexion SQLite con `sqlite3`.
3. Crear el esquema inicial de tablas.
4. Implementar listado publico de becas.
5. Implementar detalle publico de beca.
6. Implementar login y logout de admin.
7. Proteger rutas admin con sesion.
8. Implementar alta y edicion de becas desde admin.
9. Agregar validaciones y mensajes basicos.
10. Ajustar la interfaz visual minima para publico y admin.

## Reglas de implementacion
- Mantener separadas la UI publica y la UI admin.
- No mezclar controles de edicion con la vista publica.
- Mantener la logica SQL fuera de los templates.
- Mantener los controladores chicos y claros.
- Preferir soluciones simples antes que patrones extra.

## Riesgos a evitar
- Guardar contrasenas en texto plano.
- Mezclar permisos admin con la navegacion publica.
- Repartir SQL por cualquier archivo sin orden.
- Sobredisenar el proyecto antes de tener el CRUD basico funcionando.

## Siguiente paso recomendado
- Definir la estructura exacta de carpetas y archivos iniciales del MVC antes de empezar a implementar.
