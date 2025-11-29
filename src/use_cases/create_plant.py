"""Use case for registering a new plant."""

from typing import Callable

from src.entities.plant import Plant
from src.use_cases.ports.plant_repository import PlantRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class CreatePlantUseCase:
    """Create a plant using the repository contract."""

    def __init__(
        self, repository: PlantRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(
        self, *, name: str, location: str | None = None, status: str | None = None
    ) -> Plant:
        with self._uow_factory() as uow:
            created = self._repository.create_plant(
                name=name, location=location, status=status, session=uow.session
            )
            uow.commit()
            return created
