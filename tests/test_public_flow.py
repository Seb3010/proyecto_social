#!/usr/bin/env python3
"""
test_public_flow.py — Verificación del flujo público de becas.

Casos:
  1. Setup: crear beca publicada + borrador en base temporal
  2. GET / → 200, publicada visible, borrador ausente
  3. GET /buscar?q=Beca+Publicada → 200, publicada en resultados
  4. GET /buscar?q=Beca+Borrador → 200, borrador AUSENTE de resultados
  5. GET /becas/<id-publicada> → 200, título visible
  6. GET /becas/<id-borrador> → 404
  7. GET /becas/999999 → 404
  8. Modelo: admin sigue viendo ambas (2 con published_only=False, 1 con True)
  9. Cleanup: eliminar archivo temporal

Requerimientos:
  - Flask, sqlite3 (librería estándar)
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
# Esto debe hacerse antes de cualquier código que use get_db()
from app import app
app.config['DATABASE'] = DB_PATH
app.config['TESTING'] = True

from models.scholarship import create, get_all, get_by_id
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
print("TEST: Flujo público de becas (T24)")
print("=" * 60)

print(f"\n[1/9] Setup — Crear base temporal y datos de prueba")
print(f"     DB temporal: {DB_PATH}")

with app.app_context():
    db = get_db()
    _init_schema(db)

    pub_id = create(db, {
        'title': 'Beca Publicada T24',
        'institution': 'Universidad Test',
        'description': 'Beca pública para verificación T24',
        'requirements': 'Requisitos estándar',
        'deadline': '2026-12-31',
        'location': 'Online',
        'link': 'https://example.com/publicada',
        'is_published': 1,
    })

    draft_id = create(db, {
        'title': 'Beca Borrador T24',
        'institution': 'Universidad Test',
        'description': 'Beca borrador que no debe aparecer',
        'requirements': 'No aplicar',
        'deadline': '2026-12-31',
        'location': 'Online',
        'link': 'https://example.com/borrador',
        'is_published': 0,
    })

    db.commit()

print(f"     Beca publicada ID: {pub_id}")
print(f"     Beca borrador ID:  {draft_id}")
_check(pub_id is not None, "ID de beca publicada generado")
_check(draft_id is not None, "ID de beca borrador generado")

# Cliente de prueba
client = app.test_client()

# ═══════════════════════════════════════════════════════════════════════════
# 2. GET / — Listado público
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[2/9] GET / — Listado público")
resp = client.get('/')
body = resp.data.decode('utf-8')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 200, "Status 200 en listado público")
_check('Beca Publicada T24' in body, "Beca publicada visible en listado")
_check('Beca Borrador T24' not in body, "Beca borrador NO visible en listado")

# ═══════════════════════════════════════════════════════════════════════════
# 3. GET /buscar?q=Beca+Publicada — Búsqueda de publicada
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[3/9] GET /buscar?q=Beca+Publicada — Búsqueda de publicada")
resp = client.get('/buscar?q=Beca+Publicada')
body = resp.data.decode('utf-8')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 200, "Status 200 en búsqueda de publicada")
_check('Beca Publicada T24' in body,
       "Publicada visible en resultados de búsqueda")

# ═══════════════════════════════════════════════════════════════════════════
# 4. GET /buscar?q=Beca+Borrador — Borrador ausente en resultados
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[4/9] GET /buscar?q=Beca+Borrador — Borrador ausente en resultados")
resp = client.get('/buscar?q=Beca+Borrador')
body = resp.data.decode('utf-8')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 200, "Status 200 en búsqueda de borrador")
_check('Beca Borrador T24' not in body,
       "Borrador NO aparece aunque coincida textualmente")

# ═══════════════════════════════════════════════════════════════════════════
# 5. GET /becas/<pub_id> — Detalle de beca publicada
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[5/9] GET /becas/{pub_id} — Detalle de beca publicada")
resp = client.get(f'/becas/{pub_id}')
body = resp.data.decode('utf-8')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 200, "Status 200 en detalle de publicada")
_check('Beca Publicada T24' in body, "Título de publicada visible en detalle")

# ═══════════════════════════════════════════════════════════════════════════
# 6. GET /becas/<draft_id> — Detalle de beca borrador → 404
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[6/9] GET /becas/{draft_id} — Detalle de borrador (debe ser 404)")
resp = client.get(f'/becas/{draft_id}')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 404, "Status 404 en detalle de beca borrador")

# ═══════════════════════════════════════════════════════════════════════════
# 7. GET /becas/999999 — ID inexistente → 404
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[7/9] GET /becas/999999 — ID inexistente (debe ser 404)")
resp = client.get('/becas/999999')
print(f"     Status: {resp.status_code}")
_check(resp.status_code == 404, "Status 404 en ID inexistente")

# ═══════════════════════════════════════════════════════════════════════════
# 8. Modelo — Admin sigue viendo ambas
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[8/9] Modelo — Admin conserva acceso a todas")
with app.app_context():
    db = get_db()
    todas = get_all(db, published_only=False)
    publicadas = get_all(db, published_only=True)

print(f"     get_all(published_only=False): {len(todas)} registros")
print(f"     get_all(published_only=True):  {len(publicadas)} registros")
_check(len(todas) == 2,
       "get_all(published_only=False) devuelve 2 (publicada + borrador)")
_check(len(publicadas) == 1,
       "get_all(published_only=True) devuelve solo 1 (solo publicada)")

# ═══════════════════════════════════════════════════════════════════════════
# 9. Cleanup — Eliminar base temporal
# ═══════════════════════════════════════════════════════════════════════════
print(f"\n[9/9] Cleanup — Eliminar base temporal")
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
