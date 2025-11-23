"""
Path: shared/config.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

def get_env(var_name, default=None):
    "Obtiene una variable de entorno"
    return os.environ.get(var_name, default)

def get_mysql_config():
    "Obtiene la configuración de MySQL"
    return {
        "host": get_env("MYSQL_HOST"),
        "port": int(get_env("MYSQL_PORT", 3306)),
        "user": get_env("MYSQL_USER"),
        "password": get_env("MYSQL_PASSWORD"),
        "database": get_env("MYSQL_DB"),
        "connect_timeout": 3
    }

def get_use_db():
    "Obtiene el valor de USE_DB"
    return get_env("USE_DB")

def get_static_path():
    "Obtiene la ruta base de archivos estáticos"
    return get_env("STATIC_PATH", "static")

def get_config():
    "Load configuration from environment variables"
    config = {
        # --- Logging ---
        "LOG_LEVEL": os.getenv("LOG_LEVEL"),

        # --- WooCommerce API ---
        "URL": os.getenv("URL"),  # p.ej. https://midominio.com/
        "CK": os.getenv("CK"),    # consumer key
        "CS": os.getenv("CS"),    # consumer secret

        # --- MySQL (si aplica) ---
        "MYSQL_HOST": os.getenv("MYSQL_HOST"),
        "MYSQL_PORT": os.getenv("MYSQL_PORT"),
        "MYSQL_USER": os.getenv("MYSQL_USER"),
        "MYSQL_PASSWORD": os.getenv("MYSQL_PASSWORD"),
        "MYSQL_DATABASE": os.getenv("MYSQL_DATABASE"),

        # --- API Base URL ---
        "API_BASE": os.getenv("API_BASE"),
    }
    return config
