"""Use case for deleting equipment."""

from typing import Callable

from src.use_cases.ports.plant_repository import EquipmentRepository
from src.use_cases.ports.unit_of_work import UnitOfWork


class DeleteEquipmentUseCase:
    """Remove equipment and its attached systems."""

    def __init__(
        self, repository: EquipmentRepository, uow_factory: Callable[[], UnitOfWork]
    ) -> None:
        self._repository = repository
        self._uow_factory = uow_factory

    def execute(self, equipment_id: int) -> bool:
        with self._uow_factory() as uow:
            deleted = self._repository.delete_equipment(
                equipment_id, session=uow.session
            )
            if not deleted:
                uow.rollback()
                return False

            uow.commit()
            return True
