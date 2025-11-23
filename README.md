# Planta Mantenimiento API

API de demostración para gestionar plantas industriales, áreas, equipos y sistemas. El proyecto aplica principios de arquitectura limpia (entidades + casos de uso + adaptadores + infraestructura), inyección de dependencias y separación de responsabilidades para ilustrar un backend mantenible.

## Arquitectura
- **Entities (`src/entities/`)**: modelos de dominio inmutables para plantas, áreas, equipos y sistemas.
- **Use cases (`src/use_cases/`)**: coordinan la lógica de aplicación mediante puertos de repositorio. Cada archivo implementa una operación puntual (listar, crear, actualizar, eliminar).
- **Interface adapters (`src/interface_adapters/`)**: controladores (FastAPI y Flask), presenters y gateways.
- **Infrastructure (`src/infrastructure/`)**: composición de la aplicación, middlewares, wiring de dependencias y acceso a base de datos.

## Ejecución local
1. Crear y activar un entorno virtual (opcional pero recomendado).
2. Instalar dependencias básicas:
   ```bash
   pip install fastapi uvicorn flask SQLAlchemy PyMySQL
   ```
3. Iniciar el servidor en modo recarga (FastAPI):
   ```bash
   python run.py
   ```
4. La API quedará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

### Servir con Flask
- Entrypoint: `python run_flask.py`
- Puerto por defecto: `http://localhost:5000`
- Usa las mismas rutas bajo el prefijo `/api` y el mismo repositorio SQLAlchemy configurado por variables `DB_*`.

## Endpoints principales
Las rutas siguen el contrato descrito en `docs/backend-endpoints.md` y devuelven cuerpos en español.

### Plantas
- `GET /api/plantas` → lista de plantas.
- `POST /api/plantas` con `{ "nombre": string, "ubicacion"?: string, "estado"?: string }` → planta creada.
- `GET /api/plantas/{id}` → detalle de planta.
- `PUT /api/plantas/{id}` con `{ "nombre"?, "ubicacion"?, "estado"? }` → planta actualizada.
- `DELETE /api/plantas/{id}` → elimina la planta (y en cascada sus áreas/equipos/sistemas).
- `GET /api/plantas/{plantaId}/areas` → áreas de la planta.
- `POST /api/plantas/{plantaId}/areas` con `{ "nombre": string, "estado"?: string }` → área creada.

### Áreas
- `PUT /api/areas/{id}` con `{ "nombre"?, "estado"? }` → área actualizada.
- `DELETE /api/areas/{id}` → elimina área y recursos asociados.
- `GET /api/areas/{areaId}/equipos` → equipos del área.
- `POST /api/areas/{areaId}/equipos` con `{ "nombre": string, "estado"?: string }` → equipo creado.

### Equipos
- `PUT /api/equipos/{id}` con `{ "nombre"?, "estado"? }` → equipo actualizado.
- `DELETE /api/equipos/{id}` → elimina equipo y sus sistemas.
- `GET /api/equipos/{equipoId}/sistemas` → sistemas del equipo.
- `POST /api/equipos/{equipoId}/sistemas` con `{ "nombre": string, "estado"?: string }` → sistema creado.

### Sistemas
- `PUT /api/sistemas/{id}` con `{ "nombre"?, "estado"? }` → sistema actualizado.
- `DELETE /api/sistemas/{id}` → elimina sistema.

## Notas de implementación
- Las respuestas y errores siguen mensajes en español para alinearse con el frontend.
- La capa de presenters traduce los atributos de dominio a las claves esperadas por el contrato (`nombre`, `plantaId`, `areaId`, `equipoId`).

## Decisiones de MySQL + SQLAlchemy

### Esquema y tipos de datos
- **Opciones evaluadas**:
  - `ENUM` vs `VARCHAR(50)` para `estado`: `ENUM` valida valores pero dificulta cambios; `VARCHAR` permite nuevos estados sin migrar.
  - Unicidad global vs unicidad por jerarquía: restringir sólo `name` podía bloquear homónimos legítimos entre plantas distintas.
  - `BIGINT` vs `INT` auto-incremental: `BIGINT` ofrece más rango pero ocupa más espacio y no es necesario para el volumen esperado.
- **Recomendación implementada**:
  - Claves primarias `INT` autoincrementales.
  - `estado` como `VARCHAR(50)` con valores por defecto (`operativa` en planta/área, `operativo` en equipo/sistema).
  - Restricciones de unicidad por nivel padre: `plants.name` único, `areas (plant_id, name)`, `equipment (area_id, name)`, `systems (equipment_id, name)`.
  - Longitudes: `name VARCHAR(150)`, `location VARCHAR(255)`.

### SQLAlchemy Core vs Declarative ORM
- **Core**: menos magia, ideal para consultas dinámicas complejas, pero requiere más código repetitivo para mapear a entidades.
- **Declarative ORM**: reduce boilerplate, facilita relaciones y cascadas, y mapea directo a entidades de dominio con menos código.
- **Recomendación implementada**: Declarative ORM (`src/infrastructure/db/models.py`) con relaciones y cascadas `delete-orphan` para respetar la jerarquía planta → área → equipo → sistema.

### Patrón de sesión
- **scoped_session**: útil para apps WSGI con hilo por request, pero añade estado global difícil de testear.
- **Sesión por request con `sessionmaker`**: crea sesiones efímeras y explícitas, facilita pruebas y evita fugas de conexión.
- **Recomendación implementada**: `sessionmaker` con `expire_on_commit=False`, `autoflush=False` y uso mediante context manager en el repositorio (`SqlAlchemyPlantRepository`).

### Pooling, timeouts y credenciales
- **Opciones**: usar valores por defecto del driver (flexible pero opaco) vs. parametrizar pool y timeouts para entornos restringidos.
- **Recomendación implementada**: parámetros configurables por entorno con valores conservadores (`pool_size=5`, `max_overflow=10`, `pool_timeout=30s`, `pool_recycle=1800s`). Permiten operar en entornos de desarrollo sin agotar conexiones y ajustarse en producción mediante variables `DB_*`.

## Inicializar la base de datos
No se gestionan migraciones; las tablas pueden crearse directamente con:

```bash
python start_db.py
```

Variables de entorno soportadas (con valores por defecto):

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=""
DB_NAME=planta_mantenimiento
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_ECHO=false
```
