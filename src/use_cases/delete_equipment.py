"""Use case for deleting equipment."""

from src.use_cases.ports.plant_repository import EquipmentRepository


class DeleteEquipmentUseCase:
    """Remove equipment and its attached systems."""

    def __init__(self, repository: EquipmentRepository) -> None:
        self._repository = repository

    def execute(self, equipment_id: int) -> bool:
        return self._repository.delete_equipment(equipment_id)
