# Instalación y puesta en marcha

Sigue estos pasos para configurar el proyecto en un entorno local usando MySQL + SQLAlchemy.

## Prerrequisitos
- Python 3.10+
- Servidor MySQL accesible y un esquema creado (por defecto `planta_mantenimiento`).
- Dependencias: `fastapi`, `uvicorn`, `flask`, `SQLAlchemy`, `PyMySQL`.

## 1) Crear entorno virtual (opcional)
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\\Scripts\\activate
```

## 2) Instalar dependencias
```bash
pip install fastapi uvicorn flask SQLAlchemy PyMySQL
```

## 3) Configurar variables de entorno
1. Copia el archivo de ejemplo:
   ```bash
   cp env.example .env
   ```
2. Ajusta los valores de conexión MySQL según tu entorno:
   - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
   - Parámetros de pool (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`)
   - Opcional: `DB_ECHO=true` para ver SQL generado.
   - Opcional: `CORS_ORIGINS` (lista separada por comas) para permitir tu front-end, por defecto `http://localhost:5173`.

Si `.env` no existe, la aplicación usará valores por defecto y mostrará una advertencia; si algún `DB_*` no es un número válido, el arranque detendrá con un mensaje explicativo.

> Si ves errores como `Access denied for user 'root'@'localhost'`, revisa `DB_USER/DB_PASSWORD` y los permisos de MySQL.

## 4) Crear tablas sin migraciones
Ejecuta el script de arranque:
```bash
python start_db.py
```
El script capturará errores de conexión y mostrará mensajes en español con la causa probable.

## 5) Ejecutar el servidor
- **FastAPI**: `python run.py` (puerto 8000 por defecto)
- **Flask**: `python run_flask.py` (puerto 5000 por defecto)

Ambos entrypoints comparten el mismo repositorio SQLAlchemy y respetan las variables `DB_*` configuradas.
