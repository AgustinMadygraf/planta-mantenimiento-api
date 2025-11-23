# Planta Mantenimiento API

API de demostración para gestionar plantas industriales, áreas, equipos y sistemas. El proyecto aplica principios de arquitectura limpia (entidades + casos de uso + adaptadores + infraestructura), inyección de dependencias y separación de responsabilidades para ilustrar un backend mantenible.

## Arquitectura
- **Entities (`src/entities/`)**: modelos de dominio inmutables para plantas, áreas, equipos y sistemas.
- **Use cases (`src/use_cases/`)**: coordinan la lógica de aplicación mediante puertos de repositorio. Cada archivo implementa una operación puntual (listar, crear, actualizar, eliminar).
- **Interface adapters (`src/interface_adapters/`)**: controladores FastAPI, presenters y gateways. El gateway `InMemoryPlantRepository` centraliza los datos temporales y se expone mediante `providers.plant_repository` para facilitar la inyección en controladores y casos de uso.
- **Infrastructure (`src/infrastructure/fastapi/`)**: composición de la aplicación, middlewares y registro de routers.

## Ejecución local
1. Crear y activar un entorno virtual (opcional pero recomendado).
2. Instalar dependencias básicas:
   ```bash
   pip install fastapi uvicorn
   ```
3. Iniciar el servidor en modo recarga:
   ```bash
   python run.py
   ```
4. La API quedará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

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
- Los IDs se generan incrementalmente en memoria; la API está pensada para pruebas y demos rápidas.
- Las respuestas y errores siguen mensajes en español para alinearse con el frontend.
- La capa de presenters traduce los atributos de dominio a las claves esperadas por el contrato (`nombre`, `plantaId`, `areaId`, `equipoId`).
