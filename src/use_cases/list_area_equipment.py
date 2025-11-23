"""Use case for listing equipment belonging to an area."""

from typing import Sequence

from src.entities.equipment import Equipment
from src.use_cases.ports.plant_repository import PlantRepository


class ListAreaEquipmentUseCase:
    """Retrieve equipment associated with an area."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, area_id: int) -> Sequence[Equipment]:
        return self._repository.list_equipment(area_id)
