"""Use case for updating equipment data."""

from src.entities.equipment import Equipment
from src.use_cases.ports.plant_repository import PlantRepository


class UpdateEquipmentUseCase:
    """Apply changes to an equipment record."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, equipment_id: int, *, name: str | None = None, status: str | None = None) -> Equipment | None:
        return self._repository.update_equipment(equipment_id, name=name, status=status)
