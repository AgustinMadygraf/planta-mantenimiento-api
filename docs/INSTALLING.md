# Instalacion y puesta en marcha

Sigue estos pasos para configurar el proyecto en un entorno local usando MySQL + SQLAlchemy.

## Prerrequisitos
- Python 3.10+
- Servidor MySQL accesible y un esquema creado (por defecto `planta_mantenimiento`).
- Dependencias: `fastapi`, `uvicorn`, `flask`, `SQLAlchemy`, `PyMySQL`, `alembic`.

## 1) Crear entorno virtual (opcional)
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

## 2) Instalar dependencias
```bash
pip install fastapi uvicorn flask SQLAlchemy PyMySQL python-dotenv alembic
```

## 3) Configurar variables de entorno con `.env`
1. Copia el archivo de ejemplo y edita los valores:
   ```bash
   cp env.example .env
   ```
2. Configura la conexion a MySQL:
   - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
   - Parametros de pool (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`)
   - Opcional: `DB_ECHO=true` para ver el SQL generado.
   - Opcional: `DB_URL` con la URL completa.
3. Ajusta otros valores relevantes:
   - `CORS_ORIGINS` separada por comas (`http://localhost:5173` por defecto).
   - Genera una clave segura para `AUTH_SECRET_KEY`:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
     Copia el valor en `.env`.
   - Opcional: `AUTH_SUPERADMIN_USERNAME` y `AUTH_SUPERADMIN_PASSWORD`.

Si `.env` no existe, los valores por defecto se usan solo en desarrollo. `DB_*` invalidos terminan la ejecucion con un error.

> Si ves `Access denied for user 'root'@'localhost'`, revisa `DB_USER/DB_PASSWORD` y permisos de MySQL.

## 4) Inicializar la base de datos
Alembic es el flujo oficial. Usa las mismas definiciones ORM (`Base.metadata` en `src/infrastructure/sqlalchemy/models.py`) y las variables `DB_*`.

```bash
alembic upgrade head
```

Tras modificar modelos:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

Revisa el diff autogenerado (tip: asegurate de que `UniqueConstraint`, defaults y `ondelete` quedan correctos).

Si puntos de despliegue ya tienen el esquema correcto (p.ej., creado manualmente antes de Alembic), registra la version sin tocar tablas:

```bash
alembic stamp head
```

## 5) Ejecutar el servidor
- **FastAPI**: `python run.py` (puerto 8000 por defecto).
- **Flask**: `python run_flask.py` (puerto 5000 por defecto).

Ambos entrypoints usan el mismo repositorio SQLAlchemy y respetan `DB_*` y `AUTH_*`.

## 6) Generar diagrama ER (opcional)
1. Instala dependencias: `pip install eralchemy2 graphviz` y asegurate de que `dot` este en el PATH.
2. Ejecuta:
   ```bash
   python scripts/generate_erd.py
   ```
   Por defecto genera `docs/er_diagram.png` a partir del metadata declarativo. Si defines `DB_URL`, refleja el esquema de la base especificada.