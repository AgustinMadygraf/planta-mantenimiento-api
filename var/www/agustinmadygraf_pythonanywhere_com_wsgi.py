"""
Path: var/www/agustinmadygraf_pythonanywhere_com_wsgi.py
"""

import sys
import os
from dotenv import load_dotenv

PROJECT_ROOT = '/home/agustinmadygraf/planta-mantenimiento-api'
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Carga el archivo .env antes de importar la app
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

from src.infrastructure.flask.app import app as application
