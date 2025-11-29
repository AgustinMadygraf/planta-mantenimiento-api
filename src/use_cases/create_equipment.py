"""Use case for creating new equipment inside an area."""

from typing import Callable

from src.entities.equipment import Equipment
from src.use_cases.ports.plant_repository import EquipmentRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class CreateEquipmentUseCase:
    """Create equipment tied to an area."""

    def __init__(
        self, repository: EquipmentRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(
        self, area_id: int, *, name: str, status: str | None = None
    ) -> Equipment | None:
        with self._uow_factory() as uow:
            created = self._repository.create_equipment(
                area_id, name=name, status=status, session=uow.session
            )
            if created is None:
                uow.rollback()
                return None

            uow.commit()
            return created
