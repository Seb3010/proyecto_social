"""
app.py - Entrypoint de la aplicación Flask.

Arquitectura MVC para el sistema de becas.
T02: Bootstrap mínimo del entrypoint Flask.
Siguiente: T03 - Configurar conexión SQLite.
"""

import os
from flask import Flask
from models.db import init_app

app = Flask(__name__, instance_relative_config=True)

# ---------------------------------------------------------------------------
# Configuración mínima
# ---------------------------------------------------------------------------
# SECRET_KEY: usado para sesiones (necesario desde T09 - login admin).
# DATABASE: ruta absoluta al archivo SQLite dentro de instance/.
app.config.from_mapping(
    SECRET_KEY='dev-secret-key-change-in-production',
    DATABASE=os.path.join(app.instance_path, 'becas.sqlite'),
)

# Asegurar que el directorio instance/ existe (ahí vivirá la base SQLite).
os.makedirs(app.instance_path, exist_ok=True)

# Inicializar helper de base de datos SQLite (T03).
init_app(app)


# ---------------------------------------------------------------------------
# Placeholder temporal - T02/T03
# Se reemplazará con rutas reales en T07 (listado público) y T12+ (admin).
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    """Confirma que el servidor Flask arrancó correctamente."""
    return 'Servidor funcionando. Proximamente: listado de becas.'


if __name__ == '__main__':
    app.run(debug=True)
