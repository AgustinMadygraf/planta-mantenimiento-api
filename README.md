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

## Validación y serialización
- Las rutas de Flask validan cada payload con los esquemas Pydantic de `src/interface_adapters/schemas`, que escuchan campos en español (`nombre`, `estado`, etc.) pero exponen `name`, `status`, `location`, etc. a los casos de uso.
- El helper `_validate_payload` se encarga de lanzar `400 Bad Request` con mensajes detallados si algo falta o no cumple los constraints (longitud, valores en blanco). Esto mantiene los controladores ligeros y el contrato fiable.

## Autenticación JWT
- La aplicación usa `Flask-JWT-Extended` para emitir tokens estándar (`create_access_token`) y validar el header `Authorization: Bearer ...`.
- Los claims `role`, `areas` y `equipos` se incluyen como `additional_claims` y se convierten en `AuthClaims` antes de pasar a los `ScopeAuthorizer`.
- Configura `AUTH_SECRET_KEY` y `AUTH_TOKEN_TTL_SECONDS` en `.env`; Flask expone el token TTL en `JWT_ACCESS_TOKEN_EXPIRES` para mantener la caducidad sincronizada.

## Inyección de dependencias
- `Flask-Injector` se encarga del wiring de `PlantDataRepository`, `UnitOfWorkFactory` y `AuthService` dentro de `create_app` (`src/infrastructure/flask/app.py:66-93`).
- Mantén las dependencias registradas ahí al modificar repositorios o factories para que el binder tenga una sola fuente de verdad para toda la aplicación.
- Más detalles y un ejemplo de `UseCaseModule` están documentados en `docs/dependency-injection.md`.

## Notas de implementacion
- Respuestas y errores en espanol para alinear con el frontend.
- Presenters traducen atributos de dominio a las claves esperadas por el contrato (`nombre`, `plantaId`, `areaId`, `equipoId`).
- Decisiones de esquema MySQL y SQLAlchemy (tipos, unicidad, pooling) se documentan en `docs/INSTALLING.md`.

## Documentacion y endpoints
- Contratos backend: `docs/backend-endpoints.md` (si aplica) y `docs/frontend-api-contract.md`.
- Error reporting esperado por la UI: `docs/asset-loading-error-report.md`.
- Diagrama ER opcional: `scripts/generate_erd.py` (requiere `eralchemy2` + `graphviz`).
