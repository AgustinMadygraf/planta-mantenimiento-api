"""Use case for retrieving a single equipment."""

from src.entities.equipment import Equipment
from src.use_cases.ports.plant_repository import PlantRepository


class GetEquipmentUseCase:
    """Fetch equipment by identifier."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, equipment_id: int) -> Equipment | None:
        return self._repository.get_equipment(equipment_id)
