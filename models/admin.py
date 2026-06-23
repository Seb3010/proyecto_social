"""
admin.py - Operaciones de acceso a datos para la tabla admin_users.

Todas las funciones reciben ``db`` como primer parámetro (inyección desde
el controlador vía ``models.db.get_db()``). SQL explícito, sin ORM.

T06: Capa básica de consulta y creación para admin_users.
"""


def get_by_username(db, username):
    """
    Busca un administrador por su nombre de usuario.

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        username: Nombre de usuario a buscar.

    Returns:
        sqlite3.Row | None: Fila del administrador encontrado, o ``None``
        si no existe.
    """
    return db.execute(
        'SELECT * FROM admin_users WHERE username = ?', (username,)
    ).fetchone()


def get_by_id(db, admin_id):
    """
    Busca un administrador por su ID.

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        admin_id: ID del administrador a buscar.

    Returns:
        sqlite3.Row | None: Fila del administrador encontrado, o ``None``
        si no existe.
    """
    return db.execute(
        'SELECT * FROM admin_users WHERE id = ?', (admin_id,)
    ).fetchone()


def create(db, username, password_hash):
    """
    Crea un nuevo administrador en la base de datos.

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        username: Nombre de usuario del nuevo administrador.
        password_hash: Hash de la contraseña (generado externamente, ver T22).

    Returns:
        int: ID autogenerado del nuevo administrador (``lastrowid``).
    """
    cursor = db.execute(
        'INSERT INTO admin_users (username, password_hash) VALUES (?, ?)',
        (username, password_hash),
    )
    return cursor.lastrowid
