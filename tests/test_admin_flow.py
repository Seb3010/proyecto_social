#!/usr/bin/env python3
"""
test_admin_flow.py — Verificación del flujo admin completo.

Casos (según plan T25):
  1. Setup: crear base temporal y aplicar esquema real
  2. Crear admin temporal con password hash
  3. Hash no es texto plano, check_password_hash valida/rechaza
  4. Sin sesión → GET /admin → redirect a /admin/login
  5. Login con credenciales incorrectas → 200 + flash error, sin sesión
  6. Login correcto → 302 a /admin + admin_id en sesión
  7. Dashboard autenticado → 200 con username
  8. Alta con datos válidos → 302 + flash éxito + beca en DB
  9. GET /admin/becas/<id>/editar → 200 + título precargado
  10. Edición persiste cambios → 302 + flash + datos actualizados en DB
  11. POST con datos inválidos → 200 + errores, sin persistencia
  12. Logout → 302 a login + sesión limpia
  13. Cleanup: eliminar base temporal

Requerimientos:
  - Flask, sqlite3 (librería estándar), werkzeug
  - Sin pytest, sin dependencias nuevas
  - No modifica instance/becas.sqlite
"""

import os
import sys
import tempfile

# ── Preparar el path para importar app ──────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# ── Base temporal ────────────────────────────────────────────────────────
_db_handle, DB_PATH = tempfile.mkstemp(suffix='.db')
os.close(_db_handle)

# ── Importar app y redirigir a base temporal ────────────────────────────
# Esto debe hacerse antes de cualquier código que use get_db() / current_app
from app import app
app.config['DATABASE'] = DB_PATH
app.config['TESTING'] = True

from werkzeug.security import generate_password_hash, check_password_hash
from models.admin import create as create_admin, get_by_username
from models.scholarship import get_by_id as get_scholarship_by_id
from models.db import get_db

# ── Contadores de verificación ──────────────────────────────────────────
_checks = 0
_passed = 0
_failed = 0


def _check(condition, message):
    global _checks, _passed, _failed
    _checks += 1
    if condition:
        print(f"  ✓ PASS: {message}")
        _passed += 1
    else:
        print(f"  ✗ FAIL: {message}")
        _failed += 1


def _init_schema(db):
    """Aplica el DDL del esquema real en la conexión dada."""
    schema_path = os.path.join(PROJECT_ROOT, 'models', 'schema.sql')
    with open(schema_path, 'r') as f:
        db.executescript(f.read())


# ═══════════════════════════════════════════════════════════════════════════
# 1. SETUP
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("TEST: Flujo admin completo (T25)")
print("=" * 60)

print(f"\n[1/13] Setup — Crear base temporal y esquema")
print(f"     DB temporal: {DB_PATH}")

with app.app_context():
    db = get_db()
    _init_schema(db)
    db.commit()

_check(os.path.exists(DB_PATH), "Base temporal creada")

# ═══════════════════════════════════════════════════════════════════════════
# 2. Crear admin temporal con password hash
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[2/13] Crear admin temporal con password hash")

PASSWORD = 'testpass123'
password_hash = generate_password_hash(PASSWORD)

with app.app_context():
    db = get_db()
    admin_id = create_admin(db, 'testadmin', password_hash)
    db.commit()

print(f"     Admin ID: {admin_id} | Hash: {password_hash[:30]}...")
_check(admin_id is not None, "Admin creado con ID válido")
_check(isinstance(admin_id, int), "Admin ID es entero")

# ═══════════════════════════════════════════════════════════════════════════
# 3. Verificar hash: no es texto plano y check_password_hash valida/rechaza
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[3/13] Verificar hash — no es texto plano, check valida/rechaza")

with app.app_context():
    db = get_db()
    admin = get_by_username(db, 'testadmin')
    stored_hash = admin['password_hash']

_check(stored_hash != PASSWORD, "Hash NO es igual al password en texto plano")
_check(check_password_hash(stored_hash, PASSWORD),
       "check_password_hash valida el password correcto")
_check(not check_password_hash(stored_hash, 'wrongpass'),
       "check_password_hash rechaza password incorrecto")

# ═══════════════════════════════════════════════════════════════════════════
# 4. Sin sesión → GET /admin → redirect a /admin/login
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[4/13] GET /admin sin sesión — redirect a login")

client = app.test_client()

resp = client.get('/admin', follow_redirects=False)
print(f"     Status: {resp.status_code} | Location: {resp.location}")
_check(resp.status_code == 302, "Status 302 sin sesión (redirect)")
_check('/admin/login' in resp.location, "Location apunta a /admin/login")

# ═══════════════════════════════════════════════════════════════════════════
# 5. Login con credenciales incorrectas
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[5/13] POST /admin/login con credenciales incorrectas")

resp = client.post('/admin/login', data={
    'username': 'testadmin',
    'password': 'wrongpass',
}, follow_redirects=False)
body = resp.data.decode('utf-8')

print(f"     Status: {resp.status_code}")
_check(resp.status_code == 200, "Status 200 (re-renderiza login con error)")
_check('Usuario o contraseña incorrectos' in body,
       "Flash de error 'Usuario o contraseña incorrectos' visible en body")

# Verificar que NO se estableció sesión
with client.session_transaction() as sess:
    _check('admin_id' not in sess,
           "NO hay admin_id en sesión tras login fallido")

# ═══════════════════════════════════════════════════════════════════════════
# 6. Login correcto
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[6/13] POST /admin/login con credenciales correctas")

resp = client.post('/admin/login', data={
    'username': 'testadmin',
    'password': PASSWORD,
}, follow_redirects=False)
print(f"     Status: {resp.status_code} | Location: {resp.location}")
_check(resp.status_code == 302, "Status 302 tras login correcto (redirect)")
_check(resp.location.endswith('/admin'), "Location apunta a /admin")

# Verificar sesión establecida
with client.session_transaction() as sess:
    _check('admin_id' in sess, "admin_id presente en sesión tras login correcto")
    _check(sess['admin_id'] == admin_id, f"admin_id = {admin_id} (match con admin creado)")

# ═══════════════════════════════════════════════════════════════════════════
# 7. Dashboard autenticado
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[7/13] GET /admin autenticado — dashboard")

resp = client.get('/admin', follow_redirects=False)
body = resp.data.decode('utf-8')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 200, "Status 200 en dashboard autenticado")
_check('Panel de Administración' in body, "Título 'Panel de Administración' visible")
_check('testadmin' in body, "Nombre de usuario 'testadmin' visible en dashboard")

# ═══════════════════════════════════════════════════════════════════════════
# 8. Alta con datos válidos
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[8/13] POST /admin/becas/nueva con datos válidos")

resp = client.post('/admin/becas/nueva', data={
    'title': 'Beca Test T25',
    'institution': 'Universidad de Prueba',
    'description': 'Descripción de prueba para T25',
    'requirements': 'Requisitos de prueba',
    'deadline': '2026-12-31',
    'location': 'Online',
    'link': 'https://example.com/beca',
    'is_published': 'on',
}, follow_redirects=False)
print(f"     Status: {resp.status_code} | Location: {resp.location}")
_check(resp.status_code == 302, "Status 302 tras alta exitosa (redirect)")
_check(resp.location.endswith('/admin'), "Location apunta a /admin tras alta")

# Verificar flash de éxito (hacemos GET al dashboard, el flash está en sesión)
resp_dash = client.get('/admin', follow_redirects=False)
body_dash = resp_dash.data.decode('utf-8')
_check('Beca creada correctamente' in body_dash,
       "Flash de éxito 'Beca creada correctamente' visible en dashboard")

# Verificar que la beca existe en la base temporal
with app.app_context():
    db = get_db()
    beca_row = db.execute(
        "SELECT id, title FROM scholarships WHERE title = ?",
        ('Beca Test T25',)
    ).fetchone()

_check(beca_row is not None, "Beca creada existe en DB temporal")
beca_id = beca_row['id']
print(f"     Beca ID en DB: {beca_id}")

# ═══════════════════════════════════════════════════════════════════════════
# 9. GET /admin/becas/<id>/editar — precarga datos
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[9/13] GET /admin/becas/{beca_id}/editar — precarga datos")

resp = client.get(f'/admin/becas/{beca_id}/editar', follow_redirects=False)
body = resp.data.decode('utf-8')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 200, "Status 200 en formulario de edición")
_check('Beca Test T25' in body, "Título precargado 'Beca Test T25' visible en input")
_check('Editar Beca' in body, "Título de página 'Editar Beca' visible")

# ═══════════════════════════════════════════════════════════════════════════
# 10. Edición persiste cambios
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[10/13] POST /admin/becas/{beca_id}/editar — actualizar datos")

resp = client.post(f'/admin/becas/{beca_id}/editar', data={
    'title': 'Beca Test T25 Editada',
    'institution': 'Universidad de Prueba',
    'description': 'Descripción actualizada para T25',
    'requirements': 'Nuevos requisitos',
    'deadline': '2027-01-15',
    'location': 'Presencial',
    'link': 'https://example.com/beca-editada',
    'is_published': 'on',
}, follow_redirects=False)
print(f"     Status: {resp.status_code} | Location: {resp.location}")
_check(resp.status_code == 302, "Status 302 tras edición exitosa (redirect)")
_check(resp.location.endswith('/admin'),
       "Location apunta a /admin tras editar")

# Verificar flash de éxito
resp_dash = client.get('/admin', follow_redirects=False)
body_dash = resp_dash.data.decode('utf-8')
_check('Beca actualizada correctamente' in body_dash,
       "Flash de éxito 'Beca actualizada correctamente' visible en dashboard")

# Verificar cambios persistieron en DB
with app.app_context():
    db = get_db()
    updated = get_scholarship_by_id(db, beca_id)

_check(updated is not None, "Beca aún existe en DB tras edición")
_check(updated['title'] == 'Beca Test T25 Editada',
       "Título actualizado en DB: 'Beca Test T25 Editada'")
_check(updated['description'] == 'Descripción actualizada para T25',
       "Descripción actualizada en DB")
_check(updated['deadline'] == '2027-01-15',
       "Deadline actualizado en DB: '2027-01-15'")

# ═══════════════════════════════════════════════════════════════════════════
# 11. POST con datos inválidos
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[11/13] POST /admin/becas/nueva con datos inválidos (sin título)")

# Contar registros antes
with app.app_context():
    db = get_db()
    count_before = db.execute('SELECT COUNT(*) FROM scholarships').fetchone()[0]

resp = client.post('/admin/becas/nueva', data={
    'institution': 'Test Inst',
    'description': 'Sin título para probar validación',
}, follow_redirects=False)
body = resp.data.decode('utf-8')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 200, "Status 200 (re-renderiza form con errores)")
_check('El título es obligatorio' in body,
       "Error 'El título es obligatorio' visible en body")
_check('La institución es obligatoria' not in body,
       "NO aparece error de institución (sí se envió institución)")

# Verificar que NO se creó nuevo registro
with app.app_context():
    db = get_db()
    count_after = db.execute('SELECT COUNT(*) FROM scholarships').fetchone()[0]

_check(count_after == count_before,
       f"No se creó nueva beca ({count_before} registros antes y después)")

# ═══════════════════════════════════════════════════════════════════════════
# 12. Logout limpia sesión
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[12/13] POST /admin/logout — cerrar sesión")

# Confirmar sesión activa antes del logout
with client.session_transaction() as sess:
    _check('admin_id' in sess, "Sesión activa antes del logout")

resp = client.post('/admin/logout', follow_redirects=False)
print(f"     Status: {resp.status_code} | Location: {resp.location}")
_check(resp.status_code == 302, "Status 302 tras logout (redirect)")
_check('login' in resp.location, "Location apunta a login tras logout")

# Verificar sesión limpia
with client.session_transaction() as sess:
    _check('admin_id' not in sess,
           "admin_id NO está presente en sesión tras logout")

# Verificar que /admin redirige a login nuevamente
resp_admin = client.get('/admin', follow_redirects=False)
_check(resp_admin.status_code == 302,
       "Después de logout, GET /admin redirige (302)")
_check('/admin/login' in resp_admin.location,
       "Redirect a /admin/login después de logout")

# ═══════════════════════════════════════════════════════════════════════════
# 13. Cleanup — Eliminar base temporal
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[13/13] Cleanup — Eliminar base temporal")

try:
    os.unlink(DB_PATH)
    _check(True, f"Archivo temporal eliminado: {DB_PATH}")
except OSError as e:
    _check(False, f"No se pudo eliminar archivo temporal: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
status = "TODO OK" if _failed == 0 else "FALLOS DETECTADOS"
print(f"RESUMEN: {_passed}/{_checks} checks pasados, {_failed} fallos — {status}")
print("=" * 60)

if _failed > 0:
    sys.exit(1)
