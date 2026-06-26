"""
becas.py - Blueprint de rutas públicas para el listado y búsqueda de becas.

T07: Vista pública con listado de becas publicadas y búsqueda por texto.
"""

from flask import Blueprint, render_template, request
from models.db import get_db
from models.scholarship import get_all, search

becas_bp = Blueprint('becas', __name__)


@becas_bp.route('/')
def listado():
    """Muestra el listado de becas publicadas (is_published=1)."""
    db = get_db()
    becas = get_all(db, published_only=True)
    return render_template('listado.html', becas=becas, query='')


@becas_bp.route('/buscar')
def buscar():
    """Busca becas por texto en título, institución o descripción."""
    db = get_db()
    q = request.args.get('q', '').strip()
    if q:
        becas = search(db, q)
    else:
        becas = get_all(db, published_only=True)
    return render_template('listado.html', becas=becas, query=q)
