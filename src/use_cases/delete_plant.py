"""Use case for deleting an existing plant."""

from typing import Callable

from src.use_cases.ports.plant_repository import PlantRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class DeletePlantUseCase:
    """Remove a plant and its related resources."""

    def __init__(
        self, repository: PlantRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(self, plant_id: int) -> bool:
        with self._uow_factory() as uow:
            deleted = self._repository.delete_plant(plant_id, session=uow.session)
            if not deleted:
                uow.rollback()
                return False

            uow.commit()
            return True
