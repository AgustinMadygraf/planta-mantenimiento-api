"""Use case for deleting equipment."""

from src.use_cases.ports.plant_repository import PlantRepository


class DeleteEquipmentUseCase:
    """Remove equipment and its attached systems."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, equipment_id: int) -> bool:
        return self._repository.delete_equipment(equipment_id)
