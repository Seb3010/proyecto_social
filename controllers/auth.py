"""
auth.py - Blueprint de autenticación para administradores.

T09: Login de admin con sesión Flask.
T12: Dashboard admin protegido con login_required.
T13: Formulario y procesamiento de nueva beca.
"""

import re
from flask import Blueprint, render_template, request, session, redirect, url_for, abort, flash
from models.db import get_db
from models.admin import get_by_username, get_by_id
from models.scholarship import get_all, create, update
from models.scholarship import get_by_id as get_scholarship_by_id
from werkzeug.security import check_password_hash
from controllers.decorators import login_required

auth_bp = Blueprint('auth', __name__)


def _validar_beca(data):
    """Valida datos de beca. Devuelve lista de errores (vacía si ok)."""
    errores = []
    if not data.get('title', '').strip():
        errores.append('El título es obligatorio.')
    if not data.get('institution', '').strip():
        errores.append('La institución es obligatoria.')

    deadline = data.get('deadline', '').strip()
    if deadline and not re.match(r'^\d{4}-\d{2}-\d{2}$', deadline):
        errores.append('La fecha límite debe tener formato YYYY-MM-DD.')

    link = data.get('link', '').strip()
    if link and not re.match(r'^https?://', link):
        errores.append('El link debe ser una URL válida (https://...).')

    return errores


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Muestra formulario de login y procesa credenciales."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        admin = get_by_username(db, username)

        if admin is None or not check_password_hash(admin['password_hash'], password):
            flash('Usuario o contraseña incorrectos', 'error')
        else:
            session['admin_id'] = admin['id']
            flash('Bienvenido al panel', 'success')
            return redirect(url_for('auth.dashboard'))

    return render_template('login.html')


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
        errores = _validar_beca(data)
        if errores:
            return render_template('nueva_beca.html', errores=errores, beca=data)
        create(db, data)
        flash('Beca creada correctamente', 'success')
        return redirect(url_for('auth.dashboard'))
    return render_template('nueva_beca.html')


@auth_bp.route('/admin/becas/<int:beca_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_beca(beca_id):
    """Muestra formulario precargado y procesa la actualización de beca."""
    db = get_db()
    beca = get_scholarship_by_id(db, beca_id)
    if beca is None:
        abort(404)

    if request.method == 'POST':
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
        errores = _validar_beca(data)
        if errores:
            data['id'] = beca_id
            return render_template('nueva_beca.html', errores=errores, beca=data, editando=True)
        update(db, beca_id, data)
        flash('Beca actualizada correctamente', 'success')
        return redirect(url_for('auth.dashboard'))

    return render_template('nueva_beca.html', beca=beca, editando=True)


@auth_bp.route('/admin/logout', methods=['POST'])
@login_required
def logout():
    """Cierra la sesión del administrador."""
    session.clear()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('auth.login'))
