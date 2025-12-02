# Dependency Injection Overview

This project keeps the wiring of repositories, unit-of-work factories, and authentication services in `src/infrastructure/flask/app.py`. `Flask-Injector` ensures that each entrypoint receives a singleton `PlantDataRepository`, the shared `UnitOfWorkFactory`, and the `AuthService` with `Flask-JWT-Extended` configured.

If you want to expand the Injector configuration to cover use cases, define a dedicated module such as:

```python
from injector import Module, provider, singleton

from src.infrastructure.flask.app import UnitOfWorkFactory
from src.infrastructure.flask.auth import AuthService
from src.interface_adapters.gateways.in_memory_plant_repository import (
    InMemoryPlantRepository,
)
from src.use_cases.create_plant import CreatePlantUseCase
from src.use_cases.list_plants import ListPlantsUseCase


class UseCaseModule(Module):
    @provider
    def provide_create_plant(
        self,
        repository: PlantDataRepository,
        uow_factory: UnitOfWorkFactory,
    ) -> CreatePlantUseCase:
        return CreatePlantUseCase(repository, uow_factory)

    @provider
    def provide_list_plants(self, repository: PlantDataRepository) -> ListPlantsUseCase:
        return ListPlantsUseCase(repository)

    # Add providers for the remaining read/write use cases as needed.
```

Then pass the module into `FlaskInjector` along with the base binder:

```python
FlaskInjector(app=flask_app, modules=[configure_binder, UseCaseModule()])
```

This keeps the binding logic centralized, makes tests easier because you can replace individual use cases with fakes, and keeps controllers focused on translation rather than instantiation.
