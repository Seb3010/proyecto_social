"""
auth.py - Blueprint de autenticación para administradores.

T09: Login de admin con sesión Flask.
T12: Dashboard admin protegido con login_required.
T13: Formulario y procesamiento de nueva beca.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, abort
from models.db import get_db
from models.admin import get_by_username, get_by_id
from models.scholarship import get_all, create
from models.scholarship import get_by_id as get_scholarship_by_id
from werkzeug.security import check_password_hash
from controllers.decorators import login_required

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


@auth_bp.route('/admin')
@login_required
def dashboard():
    """Muestra el panel principal con todas las becas."""
    db = get_db()
    admin = get_by_id(db, session['admin_id'])
    becas = get_all(db)
    return render_template('dashboard.html', admin=admin, becas=becas)


@auth_bp.route('/admin/becas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_beca():
    """Muestra formulario de alta y procesa la creación de beca."""
    if request.method == 'POST':
        db = get_db()
        data = {
            'title': request.form.get('title', ''),
            'institution': request.form.get('institution', ''),
            'description': request.form.get('description', ''),
            'requirements': request.form.get('requirements', ''),
            'deadline': request.form.get('deadline', ''),
            'location': request.form.get('location', ''),
            'link': request.form.get('link', ''),
            'is_published': 1 if request.form.get('is_published') else 0,
        }
        create(db, data)
        return redirect(url_for('auth.dashboard'))
    return render_template('nueva_beca.html')


@auth_bp.route('/admin/becas/<int:beca_id>/editar')
@login_required
def editar_beca(beca_id):
    """Muestra formulario precargado para editar una beca existente."""
    db = get_db()
    beca = get_scholarship_by_id(db, beca_id)
    if beca is None:
        abort(404)
    return render_template('nueva_beca.html', beca=beca, editando=True)


@auth_bp.route('/admin/logout', methods=['POST'])
@login_required
def logout():
    """Cierra la sesión del administrador."""
    session.clear()
    return redirect(url_for('auth.login'))
