"""
db.py - Conexión a SQLite usando sqlite3 de la librería estándar.

Sigue el patrón recomendado por Flask:
  - get_db()    → devuelve conexión para el request actual (cacheada en g).
  - close_db()  → cierra la conexión al finalizar el request.
  - init_app()  → registra close_db como teardown de la app.

T03: Helper inicial de conexión SQLite.
T04: Esquema creado (scholarships + admin_users) + comando flask init-db.
"""

import sqlite3
import click
from flask import g, current_app


def get_db():
    """
    Devuelve una conexión a SQLite para el request actual.

    La conexión se cachea en el objeto ``g`` de Flask para reutilizarla
    durante todo el ciclo del request. Se crea automáticamente la
    primera vez que se llama por request.

    Returns:
        sqlite3.Connection: Conexión activa con:
            - row_factory = sqlite3.Row  → acceso tipo dict a las filas.
            - PRAGMA foreign_keys = ON   → integridad referencial activa.
            - detect_types = PARSE_DECLTYPES → tipos declarados en schema.
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')

    return g.db


def close_db(e=None):
    """
    Cierra la conexión a SQLite al finalizar el request.

    Se ejecuta siempre que haya una conexión en ``g``, incluso si
    ocurrió una excepción durante el request.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """
    Inicializa la base de datos aplicando el esquema DDL.
    Borra cualquier tabla existente y crea tablas vacías.
    """
    db = get_db()
    with current_app.open_resource('models/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Limpia los datos existentes y crea las tablas del esquema (T04)."""
    init_db()
    click.echo('Base de datos inicializada correctamente (Tablas creadas).')


def init_app(app):
    """
    Inicializa el helper de base de datos en la aplicación Flask.

    Registra ``close_db`` como función a ejecutar al finalizar cada
    request (teardown_appcontext). También agrega el comando CLI
    'init-db' para poder inicializar la base desde la terminal.

    Args:
        app: Instancia de Flask.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
