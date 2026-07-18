"""
scholarship.py - Operaciones de acceso a datos para la tabla scholarships.

Todas las funciones reciben ``db`` como primer parámetro (inyección desde
el controlador vía ``models.db.get_db()``). SQL explícito, sin ORM.

T05: Capa CRUD + búsqueda para scholarships.
"""


def get_all(db, published_only=False):
    """
    Devuelve todas las becas, opcionalmente solo las publicadas.

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        published_only: Si es ``True``, filtra solo las que tienen
            ``is_published = 1``.

    Returns:
        list[sqlite3.Row]: Lista de filas de scholarships ordenadas por
        ``created_at`` descendente.
    """
    if published_only:
        return db.execute(
            'SELECT * FROM scholarships WHERE is_published = 1'
            ' ORDER BY created_at DESC'
        ).fetchall()

    return db.execute(
        'SELECT * FROM scholarships ORDER BY created_at DESC'
    ).fetchall()


def get_by_id(db, beca_id):
    """
    Busca una beca por su ID.

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        beca_id: ID de la beca a buscar.

    Returns:
        sqlite3.Row | None: Fila de la beca encontrada, o ``None`` si no
        existe.
    """
    return db.execute(
        'SELECT * FROM scholarships WHERE id = ?', (beca_id,)
    ).fetchone()


def create(db, data):
    """
    Crea una nueva beca en la base de datos.

    Los campos se toman del dict ``data`` y se insertan posicionalmente
    en el orden definido por la tabla.

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        data: Dict con las claves del modelo:
            ``title``, ``institution``, ``description``, ``requirements``,
            ``deadline``, ``location``, ``link``, ``is_published``.

    Returns:
        int: ID autogenerado de la nueva beca (``lastrowid``).
    """
    cursor = db.execute(
        'INSERT INTO scholarships '
        '(title, institution, description, requirements, deadline, '
        ' location, link, is_published) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (
            data['title'],
            data['institution'],
            data['description'],
            data['requirements'],
            data['deadline'],
            data['location'],
            data['link'],
            data['is_published'],
        ),
    )
    return cursor.lastrowid


def update(db, beca_id, data):
    """
    Actualiza los campos de una beca existente.

    Además de los campos del dict ``data``, sincroniza automáticamente
    ``updated_at`` con ``CURRENT_TIMESTAMP``.

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        beca_id: ID de la beca a actualizar.
        data: Dict con las claves a actualizar:
            ``title``, ``institution``, ``description``, ``requirements``,
            ``deadline``, ``location``, ``link``, ``is_published``.

    Returns:
        int: Número de filas afectadas (0 si el ID no existe, 1 si se
        actualizó correctamente).
    """
    cursor = db.execute(
        'UPDATE scholarships SET title=?, institution=?, description=?,'
        ' requirements=?, deadline=?, location=?, link=?, is_published=?,'
        ' updated_at=CURRENT_TIMESTAMP WHERE id=?',
        (
            data['title'],
            data['institution'],
            data['description'],
            data['requirements'],
            data['deadline'],
            data['location'],
            data['link'],
            data['is_published'],
            beca_id,
        ),
    )
    return cursor.rowcount


def delete(db, beca_id):
    """
    Elimina físicamente una beca por su ID.

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        beca_id: ID de la beca a eliminar.

    Returns:
        int: Número de filas eliminadas (0 si el ID no existe, 1 si se
        eliminó correctamente).
    """
    cursor = db.execute('DELETE FROM scholarships WHERE id = ?', (beca_id,))
    return cursor.rowcount


def search(db, query, published_only=False):
    """
    Busca becas cuyo título, institución o descripción contengan el texto
    indicado. La búsqueda es case-insensitive (depende de collation de
    SQLite).

    Args:
        db: Conexión activa a SQLite (``sqlite3.Connection``).
        query: Término de búsqueda (se envuelve con ``%`` automáticamente).
        published_only: Si es ``True``, solo devuelve becas con
            ``is_published = 1``.

    Returns:
        list[sqlite3.Row]: Lista de filas que coinciden con la búsqueda,
        ordenadas por ``created_at`` descendente.
    """
    pattern = f'%{query}%'
    if published_only:
        return db.execute(
            'SELECT * FROM scholarships'
            ' WHERE is_published = 1'
            ' AND (title LIKE ? OR institution LIKE ? OR description LIKE ?)'
            ' ORDER BY created_at DESC',
            (pattern, pattern, pattern),
        ).fetchall()

    return db.execute(
        'SELECT * FROM scholarships'
        ' WHERE title LIKE ? OR institution LIKE ? OR description LIKE ?'
        ' ORDER BY created_at DESC',
        (pattern, pattern, pattern),
    ).fetchall()
