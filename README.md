# Planta Mantenimiento API

API de demostracion para gestionar plantas industriales, areas, equipos y sistemas. Aplica arquitectura limpia (entidades + casos de uso + adaptadores + infraestructura), inyeccion de dependencias y separacion de responsabilidades.

## Arquitectura
- **Entities (`src/entities/`)**: modelos de dominio inmutables para plantas, areas, equipos y sistemas.
- **Use cases (`src/use_cases/`)**: coordinan la logica de aplicacion mediante puertos de repositorio.
- **Interface adapters (`src/interface_adapters/`)**: controladores (FastAPI y Flask), presenters y gateways.
- **Infrastructure (`src/infrastructure/`)**: composicion de la app, middlewares, wiring de dependencias y acceso a base de datos.
- **Shared (`src/shared/`)**: utilidades comunes (config, logger, helpers).

## Ejecucion local
1. Crear y activar un entorno virtual (opcional pero recomendado).
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Copiar `env.example` a `.env` y ajustar las credenciales MySQL y `CORS_ORIGINS` si aplica.
4. Levantar el servidor Flask (https, puerto 8000 por defecto):
   ```bash
   python run.py
   ```
   Documentacion interactiva: `https://localhost:8000/docs`.

Detalles extendidos en `docs/INSTALLING.md` (entorno, variables `DB_*`, ejecucion con Flask/FastAPI y SSL local).

## Migraciones con Alembic
- Usa `alembic upgrade head` para aplicar el esquema que expone `Base.metadata` en `src/infrastructure/sqlalchemy/models.py`.
- Cuando cambies modelos, genera una revisión y aplícala:
  ```bash
  alembic revision --autogenerate -m "describe change"
  alembic upgrade head
  ```
  Revisa el diff autogenerado antes de aplicarlo.
- Para marcar una base existente como al día cuando el esquema ya coincide, ejecuta `alembic stamp head`.

## Notas de implementacion
- Respuestas y errores en espanol para alinear con el frontend.
- Presenters traducen atributos de dominio a las claves esperadas por el contrato (`nombre`, `plantaId`, `areaId`, `equipoId`).
- Decisiones de esquema MySQL y SQLAlchemy (tipos, unicidad, pooling) se documentan en `docs/INSTALLING.md`.

## Documentacion y endpoints
- Contratos backend: `docs/backend-endpoints.md` (si aplica) y `docs/frontend-api-contract.md`.
- Error reporting esperado por la UI: `docs/asset-loading-error-report.md`.
- Diagrama ER opcional: `scripts/generate_erd.py` (requiere `eralchemy2` + `graphviz`).
