"""Use case for creating a new area within a plant."""

from typing import Callable

from src.entities.area import Area
from src.use_cases.ports.plant_repository import AreaRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class CreateAreaUseCase:
    """Create an area associated with a plant."""

    def __init__(
        self, repository: AreaRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(
        self, plant_id: int, *, name: str, status: str | None = None
    ) -> Area | None:
        with self._uow_factory() as uow:
            created = self._repository.create_area(
                plant_id, name=name, status=status, session=uow.session
            )
            if created is None:
                uow.rollback()
                return None

            uow.commit()
            return created
