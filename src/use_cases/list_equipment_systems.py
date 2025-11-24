"""Use case for listing systems associated with equipment."""

from typing import Sequence

from src.entities.system import System
from src.use_cases.ports.plant_repository import PlantRepository


class ListEquipmentSystemsUseCase:
    """Retrieve systems tied to a specific equipment."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, equipment_id: int) -> Sequence[System]:
        return self._repository.list_systems(equipment_id)
