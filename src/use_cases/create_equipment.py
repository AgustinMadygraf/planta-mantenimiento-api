"""Use case for creating new equipment inside an area."""

from src.entities.equipment import Equipment
from src.use_cases.ports.plant_repository import PlantRepository


class CreateEquipmentUseCase:
    """Create equipment tied to an area."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, area_id: int, *, name: str, status: str | None = None) -> Equipment | None:
        return self._repository.create_equipment(area_id, name=name, status=status)
