# Instalación y puesta en marcha

Sigue estos pasos para configurar el proyecto en un entorno local usando MySQL + SQLAlchemy.

## Prerrequisitos
- Python 3.10+
- Servidor MySQL accesible y un esquema creado (por defecto `planta_mantenimiento`).
- Dependencias: `fastapi`, `uvicorn`, `flask`, `SQLAlchemy`, `PyMySQL`.

## 1) Crear entorno virtual (opcional)
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

## 2) Instalar dependencias
```bash
pip install fastapi uvicorn flask SQLAlchemy PyMySQL python-dotenv
```

## 3) Configurar variables de entorno con `.env`
1. Copia el archivo de ejemplo y edita los valores:
   ```bash
   cp env.example .env
   ```
2. Configura la conexión a MySQL:
   - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
   - Parámetros de pool (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`)
   - Opcional: `DB_ECHO=true` para ver el SQL generado.
   - Opcional: `DB_URL` si prefieres definir la URL completa (p.ej. `mysql+pymysql://user:pass@host:3306/db`).
3. Ajusta otros valores relevantes:
   - `CORS_ORIGINS` para permitir tu front-end (lista separada por comas, por defecto `http://localhost:5173`).
   - **Genera una clave segura para `AUTH_SECRET_KEY`** ejecutando en la terminal:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
     Copia el valor generado y asígnalo en `.env`:
     ```
     AUTH_SECRET_KEY=<valor_generado>
     ```
   - `AUTH_SUPERADMIN_USERNAME` y `AUTH_SUPERADMIN_PASSWORD` para habilitar un usuario de respaldo independiente de MySQL.

Si `.env` no existe, la aplicación usará valores por defecto (adecuados solo para desarrollo). Si algún `DB_*` no es un número válido,
el arranque se detendrá con un mensaje explicativo.

> Si ves errores como `Access denied for user 'root'@'localhost'`, revisa `DB_USER/DB_PASSWORD` y los permisos de MySQL.

## 4) Crear tablas sin migraciones
Ejecuta el script de arranque para materializar el esquema (incluida la tabla `users` para autenticación):
```bash
python start_db.py
```
El script usa la configuración de `.env`, crea todas las tablas declaradas en SQLAlchemy y captura errores de conexión mostrando
mensajes en español con la causa probable.

## 5) Ejecutar el servidor
- **FastAPI**: `python run.py` (puerto 8000 por defecto, configurable con `FASTAPI_PORT` en `.env`)
- **Flask**: `python run_flask.py` (puerto 5000 por defecto, configurable con `FLASK_PORT` en `.env`)

Ambos entrypoints comparten el mismo repositorio SQLAlchemy y respetan las variables `DB_*` y `AUTH_*` configuradas.

## 6) Generar diagrama ER (opcional)
Si quieres visualizar el modelo entidad-relación:

1. Instala las dependencias opcionales: `pip install eralchemy2 graphviz` y asegúrate de que `dot` esté en tu `PATH`.
2. Ejecuta el script:
   ```bash
   python scripts/generate_erd.py
   ```
   Por defecto genera `docs/er_diagram.png` a partir del metadata declarativo. Si defines `DB_URL`, reflejará el esquema real de
   la base indicada.
