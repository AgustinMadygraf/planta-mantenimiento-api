"""Use case for updating plant information."""

from typing import Callable

from src.entities.plant import Plant
from src.use_cases.ports.plant_repository import PlantRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class UpdatePlantUseCase:
    """Apply updates to a plant and return the resulting entity."""

    def __init__(
        self, repository: PlantRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(
        self,
        plant_id: int,
        *,
        name: str | None = None,
        location: str | None = None,
        status: str | None = None,
    ) -> Plant | None:
        with self._uow_factory() as uow:
            updated = self._repository.update_plant(
                plant_id,
                name=name,
                location=location,
                status=status,
                session=uow.session,
            )
            if updated is None:
                uow.rollback()
                return None

            uow.commit()
            return updated
