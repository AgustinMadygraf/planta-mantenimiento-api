"""Use case for updating equipment data."""

from typing import Callable

from src.entities.equipment import Equipment
from src.use_cases.ports.plant_repository import EquipmentRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class UpdateEquipmentUseCase:
    """Apply changes to an equipment record."""

    def __init__(
        self, repository: EquipmentRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(
        self, equipment_id: int, *, name: str | None = None, status: str | None = None
    ) -> Equipment | None:
        with self._uow_factory() as uow:
            updated = self._repository.update_equipment(
                equipment_id, name=name, status=status, session=uow.session
            )
            if updated is None:
                uow.rollback()
                return None

            uow.commit()
            return updated
