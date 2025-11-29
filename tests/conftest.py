"""Configuración común para las pruebas."""

import sys
from pathlib import Path

# Garantiza que el paquete `src` sea importable al ejecutar `pytest` como script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
