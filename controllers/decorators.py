"""
decorators.py - Decoradores de seguridad para rutas protegidas.

T11: Decorador login_required para verificar sesión admin.
"""

from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """Decorador: redirige a login si no hay sesión admin activa."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
