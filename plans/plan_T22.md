# T22 — Hash de contraseñas — Almacenar password con hash seguro

## Intención

Todas las contraseñas de admin se almacenan hoy como `password_hash` en la tabla `admin_users`, pero no existe ningún flujo para crear un admin con una contraseña hasheada. La única forma de tener un admin funcional es insertar un hash manualmente en SQLite, lo cual es inviable para el deploy y desarrollo.

El login (T09) ya usa `check_password_hash()`. El problema está aguas arriba: no hay manera de *generar* ese hash. Sin esta tarea, el sistema de autenticación no se puede usar.

## Alcance

### Incluye
- Comando CLI `flask create-admin <username> <password>` que genera el hash con `werkzeug.security.generate_password_hash()` y persiste el admin
- Verificación de duplicados: el comando falla con mensaje claro si el username ya existe
- Confirmación visual al crear el admin exitosamente

### No incluye
- UI de registro de admin (el proyecto tiene un solo admin global, la creación es operativa)
- Cambiar la tabla `admin_users` ni su esquema (`password_hash` ya existe)
- Modificar el login existente (ya usa `check_password_hash()`, funciona correctamente)
- Seed automático al iniciar la app
- Hash de otras entidades (solo aplica a admin)
- Migraciones de base de datos

## Capacidades

### Nuevas capacidades
- `create-admin-cli`: Comando Flask CLI para crear administradores con contraseña hasheada

### Capacidades modificadas
Ninguna. El login y los modelos existentes no cambian.

## Enfoque técnico

Agregar un comando de Flask CLI en `app.py` usando `@app.cli.command('create-admin')`. El comando recibe username y password como argumentos posicionales, verifica que el usuario no exista vía `models.admin.get_by_username()`, genera el hash con `generate_password_hash()`, persiste con `models.admin.create()`, e imprime confirmación.

No se requiere cambios en `models/admin.py` — `get_by_username()` y `create()` ya existen y reciben `password_hash`. Tampoco se toca `controllers/auth.py`.

```python
# Pseudocódigo del comando
@app.cli.command('create-admin')
@click.argument('username')
@click.argument('password')
def create_admin(username, password):
    db = get_db()
    if get_by_username(db, username) is not None:
        click.echo('Error: el usuario ya existe')
        raise SystemExit(1)
    password_hash = generate_password_hash(password)
    create(db, username, password_hash)
    click.echo(f'Admin {username} creado correctamente')
```

## Archivos afectados

| Archivo | Impacto | Descripción |
|---------|---------|-------------|
| `app.py` | Modificado | Registrar comando `create-admin` con imports de `click`, `werkzeug`, `models.db` y `models.admin` |
| `plans/plan_T22.md` | Nuevo | Esta propuesta |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Error si `instance/becas.sqlite` no existe | Baja | `get_db()` crea la BD con el esquema si no existe (T03) |
| Usuario escribe contraseña en el historial del shell | Media | Documentar que es un comando de setup inicial, no de uso diario |
| Duplicado de username sin verificacion previa | Baja | El comando checkea `get_by_username()` antes de insertar |

## Plan de rollback

Eliminar el bloque del comando en `app.py` y revertir al estado anterior. No hay migraciones ni cambios de esquema.

## Dependencias

- `werkzeug.security.generate_password_hash` (ya disponible vía Flask/Werkzeug)
- `click` (ya disponible vía Flask)
- `models.db.get_db()` (existente)
- `models.admin.get_by_username()` y `models.admin.create()` (existentes)

## Criterios de éxito

- [ ] El comando `flask create-admin admin Pass123` crea un admin en `admin_users`
- [ ] El campo `password_hash` contiene un hash (no texto plano) verificable con `check_password_hash()`
- [ ] El login con el admin creado funciona y redirige al dashboard
- [ ] Ejecutar el mismo comando dos veces falla con mensaje "el usuario ya existe"
- [ ] Login con contraseña incorrecta sigue fallando como antes

## Próximo paso

Implementar T22: agregar el comando en `app.py`, verificar los criterios de éxito y marcar como completada en `task_list.csv`.
