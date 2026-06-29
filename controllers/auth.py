"""
auth.py - Blueprint de autenticación para administradores.

T09: Login de admin con sesión Flask.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for
from models.db import get_db
from models.admin import get_by_username
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Muestra formulario de login y procesa credenciales."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        admin = get_by_username(db, username)

        if admin is None or not check_password_hash(admin['password_hash'], password):
            error = 'Usuario o contraseña incorrectos'
        else:
            session['admin_id'] = admin['id']
            return redirect(url_for('auth.dashboard'))

    return render_template('login.html', error=error)


@auth_bp.route('/admin/logout', methods=['POST'])
def logout():
    """Cierra la sesión del administrador."""
    session.clear()
    return redirect(url_for('auth.login'))
