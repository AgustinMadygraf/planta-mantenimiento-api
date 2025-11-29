# Análisis de arquitectura y plan de refactor

Este documento resume hallazgos sobre la capa `src/infrastructure/sqlalchemy` y propone una ruta hacia una Arquitectura Limpia con énfasis en SOLID, POO y patrones de diseño.

## Avance reciente
- Se movió la implementación SQLAlchemy al gateway `interface_adapters/gateways/sqlalchemy/plant_repository.py`, manteniendo reexports retrocompatibles en `src/infrastructure/sqlalchemy`. Esto elimina dependencias directas de infraestructura en controladores y arranques de framework. 【F:src/interface_adapters/gateways/sqlalchemy/plant_repository.py†L1-L273】
- El contrato de acceso a datos ahora está segmentado por agregado (planta, área, equipo, sistema) en `src/use_cases/ports/plant_repository.py`, de modo que cada caso de uso consume solo lo que necesita. 【F:src/use_cases/ports/plant_repository.py†L1-L155】

### Pendiente
- Introducir un Unit of Work transaccional; hoy cada método abre su propia sesión y transacción, dificultando operaciones compuestas. 【F:src/interface_adapters/gateways/sqlalchemy/plant_repository.py†L27-L273】
- Enriquecer las entidades de dominio (actualmente dataclasses anémicas) para capturar reglas e invariantes. 【F:src/entities/plant.py†L1-L11】

## Diagnóstico actual (alto nivel)
- Las entidades de dominio se modelan como `dataclass` inmutables, pero los mapeos ORM (`PlantModel`, `AreaModel`, etc.) se definen junto con el repositorio concreto en la misma capa, generando acoplamiento fuerte entre dominio y persistencia. 
- Los casos de uso dependen directamente de `PlantRepository`, pero la implementación SQLAlchemy mezcla lógica de aplicación (validaciones básicas) con detalles de infraestructura.
- La configuración de base de datos y creación de sesiones está centrada en una base de datos MySQL, lo que dificulta sustituir el motor o reutilizar casos de uso en otros contextos.

## Problemas detectados en `src/infrastructure/sqlalchemy`
1. **Acoplamiento dominio ↔ infraestructura**: El repositorio concreto importa directamente entidades de dominio (`Plant`, `Area`, `Equipment`, `System`) y expone constructores en funciones de mapeo. Esto rompe el Principio de Inversión de Dependencias al hacer que la infraestructura conozca el modelo de dominio en detalle y viceversa. 【F:src/interface_adapters/gateways/sqlalchemy/plant_repository.py†L10-L273】
2. **Violaciones de SRP**: `SqlAlchemyPlantRepository` concentra lógica de conversión, validación (comprobar existencia de padres antes de crear hijos) y gestión de sesiones/transacciones. Una clase cumple múltiples motivos de cambio (estructura de dominio, política transaccional, elección de ORM). 【F:src/interface_adapters/gateways/sqlalchemy/plant_repository.py†L24-L273】
3. **OCP y extensibilidad limitada**: Aunque los puertos ahora están separados por agregado, los modelos ORM siguen pegados a SQLAlchemy y no hay Unit of Work que permita coordinar múltiples repositorios o motores alternativos. 【F:src/use_cases/ports/plant_repository.py†L1-L155】【F:src/interface_adapters/gateways/sqlalchemy/models.py†L1-L82】
4. **Modelo anémico**: Las entidades de dominio son `dataclass` sin comportamiento, por lo que la lógica de negocio se dispersa en infraestructura o casos de uso. Esto limita encapsulación y coherencia del estado. 【F:src/entities/plant.py†L1-L11】【F:src/entities/equipment.py†L1-L11】
5. **Falta de patrones de aislamiento**: No se observa un patrón Unit of Work para coordinar múltiples repositorios en una transacción. Tampoco hay DTOs de entrada/salida que separen el shape de datos de dominio del transporte hacia la capa de entrega.

## Propuesta de arquitectura objetivo
```
src/
  entities/                 # Entidades ricas, value objects, invariantes de dominio
  use_cases/                # Interactors que orquestan reglas de negocio
    ports/                  # Interfaces (p. ej. PlantRepository, UnitOfWork)
  interface_adapters/
    gateways/               # Adaptadores a persistencia (SQLAlchemy, APIs), mappers
    controllers/            # Entradas (FastAPI/Flask handlers) invocan casos de uso
    presenters/             # DTO/ViewModels para respuestas y validación de salida
  infrastructure/           # Configuración de frameworks, wiring, motores concretos
```
- **entities**: clases con comportamiento (por ejemplo, método `activate()`, validaciones de estado), value objects (p. ej. `Location`).
- **use_cases**: interactores que reciben puertos (repositorios, UoW, notificaciones) y devuelven DTOs de salida; no conocen ORM.
- **gateways**: implementaciones concretas de puertos usando SQLAlchemy; mapeos separados (`*Model`) y funciones de conversión con DTOs o mappers.
- **controllers**: adaptan la solicitud (FastAPI/Flask) al caso de uso, validan entrada (pydantic) y delegan lógica.
- **presenters**: formatean entidades/DTOs a la vista (JSON response, schemas), evitando que el framework conozca el dominio.

## Plan de refactor incremental
1. **Introducir puertos granulares**
   - Dividir `PlantRepository` en interfaces por agregado (`PlantRepository`, `AreaRepository`, `EquipmentRepository`, `SystemRepository`) y agregar un `UnitOfWork` para coordinar transacciones. Ubicar en `src/use_cases/ports/`.
2. **Enriquecer entidades**
   - Mover validaciones simples (por ejemplo, estados permitidos) y relaciones invariantes a métodos de entidad/value objects en `src/entities`. Añadir factories estáticos para creación consistente.
3. **Separar mapeos ORM**
   - Mantener `models.py` en `interface_adapters/gateways/sqlalchemy/models.py` como detalle de infraestructura. Evitar que las entidades dependan de SQLAlchemy.
4. **Crear mappers y DTOs**
   - Implementar mappers dedicados (`SqlAlchemyPlantMapper`) que conviertan entre modelos ORM y entidades/DTOs, reduciendo carga del repositorio.
5. **Refactor de repositorios**
   - Mover `SqlAlchemyPlantRepository` a `interface_adapters/gateways/sqlalchemy/plant_repository.py`. Hacerlo depender solo de puertos y mappers; inyectar `Session`/`sessionmaker` y `UnitOfWork`.
6. **Controllers y Presenters**
   - Para cada endpoint, crear un controlador en `interface_adapters/controllers` que reciba schemas de entrada, llame a casos de uso y utilice un presenter para devolver DTOs de salida.
7. **Configuración de infraestructura**
   - Conservar `config.py` y `session.py` en `infrastructure/sqlalchemy` pero exponer factories que registren repositorios y UoW sin que el dominio conozca SQLAlchemy.
8. **Migración iterativa**
   - Migrar caso de uso por caso de uso, reemplazando dependencias en los controladores. Mantener compatibilidad creando adaptadores temporales hasta terminar la separación completa.

## Ejemplos de código refactorizado

### Entidad de dominio (`src/entities/plant.py`)
```python
from dataclasses import dataclass

@dataclass(slots=True)
class Plant:
    id: int | None
    name: str
    location: str | None
    status: str

    def activate(self) -> None:
        self.status = "operativa"

    def deactivate(self) -> None:
        self.status = "inactiva"

    @classmethod
    def create(cls, name: str, location: str | None) -> "Plant":
        return cls(id=None, name=name, location=location, status="operativa")
```

### Caso de uso (`src/use_cases/create_plant.py`)
```python
from src.use_cases.ports.unit_of_work import UnitOfWork
from src.use_cases.ports.plant_repository import PlantRepository
from src.entities.plant import Plant

class CreatePlant:
    def __init__(self, uow: UnitOfWork, plants: PlantRepository):
        self.uow = uow
        self.plants = plants

    def execute(self, name: str, location: str | None) -> Plant:
        plant = Plant.create(name=name, location=location)
        with self.uow as uow:
            saved = self.plants.add(plant, session=uow.session)
            uow.commit()
        return saved
```

### Gateway SQLAlchemy (`src/interface_adapters/gateways/sqlalchemy/plant_repository.py`)
```python
from sqlalchemy.orm import Session
from src.use_cases.ports.plant_repository import PlantRepository
from src.entities.plant import Plant
from .models import PlantModel
from .mappers import to_entity, to_model

class SqlAlchemyPlantRepository(PlantRepository):
    def add(self, plant: Plant, session: Session) -> Plant:
        model = to_model(plant)
        session.add(model)
        session.flush()
        return to_entity(model)

    def get(self, plant_id: int, session: Session) -> Plant | None:
        model = session.get(PlantModel, plant_id)
        return to_entity(model) if model else None
```

### Controlador (`src/interface_adapters/controllers/plants.py`)
```python
from fastapi import APIRouter, Depends
from src.use_cases.create_plant import CreatePlant
from src.interface_adapters.presenters.plant_presenter import PlantPresenter

router = APIRouter()

@router.post("/plants")
def create_plant(payload: PlantCreateInput, uc: CreatePlant = Depends()):
    plant = uc.execute(name=payload.name, location=payload.location)
    return PlantPresenter.to_response(plant)
```

### Presenter (`src/interface_adapters/presenters/plant_presenter.py`)
```python
from src.entities.plant import Plant

class PlantPresenter:
    @staticmethod
    def to_response(plant: Plant) -> dict:
        return {
            "id": plant.id,
            "name": plant.name,
            "location": plant.location,
            "status": plant.status,
        }
```

## Riesgos, trade-offs y recomendaciones finales
- **Complejidad inicial**: Introducir UoW y mappers aumenta número de clases, pero mejora claridad de responsabilidades.
- **Migración gradual**: Mantener compatibilidad requiere adaptadores temporales; planificar hitos por agregado (plant, area, etc.).
- **Consistencia transaccional**: Adoptar UoW asegura que operaciones compuestas sean atómicas; revisar manejo actual de `session.begin()` en repositorios.
- **Pruebas**: Agregar pruebas unitarias para casos de uso y mappers para evitar dependencias a base de datos real, usando fakes/in-memory en gateways.
- **Configuración**: Externalizar parámetros de conexión y permitir alternar motores (SQLite en tests) favorece portabilidad.
