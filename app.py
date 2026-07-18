"""
app.py - Entrypoint de la aplicación Flask.

Arquitectura MVC para el sistema de becas.
T02: Bootstrap mínimo del entrypoint Flask.
T03: Conexión SQLite configurada.
T07: Blueprint de listado público + búsqueda registrado.
T09: Blueprint de autenticación registrado.
"""

import os
import click
from flask import Flask
from werkzeug.security import generate_password_hash
from models.db import init_app, get_db
from models.admin import get_by_username, create as create_admin_user
from controllers.becas import becas_bp
from controllers.auth import auth_bp

app = Flask(__name__, instance_relative_config=True)

# ---------------------------------------------------------------------------
# Configuración mínima
# ---------------------------------------------------------------------------
# SECRET_KEY: usado para sesiones (necesario desde T09 - login admin).
# DATABASE: ruta absoluta al archivo SQLite dentro de instance/.
app.config.from_mapping(
    SECRET_KEY='dev-secret-key-change-in-production',
    DATABASE=os.path.join(app.instance_path, 'becas.sqlite'),
)

# Asegurar que el directorio instance/ existe (ahí vivirá la base SQLite).
os.makedirs(app.instance_path, exist_ok=True)

# Inicializar helper de base de datos SQLite (T03).
init_app(app)

# Registrar blueprint de rutas públicas (T07).
app.register_blueprint(becas_bp)

# Registrar blueprint de autenticación (T09).
app.register_blueprint(auth_bp)


# ---------------------------------------------------------------------------
# Comandos CLI
# ---------------------------------------------------------------------------
@app.cli.command('create-admin')
@click.argument('username')
@click.argument('password')
def create_admin(username, password):
    """Crea un admin con contraseña hasheada."""
    db = get_db()
    existing = get_by_username(db, username)
    if existing is not None:
        click.echo('El usuario ya existe')
        raise SystemExit(1)

    password_hash = generate_password_hash(password)
    create_admin_user(db, username, password_hash)
    click.echo(f'Admin {username} creado correctamente')


if __name__ == '__main__':
    app.run(debug=True)
