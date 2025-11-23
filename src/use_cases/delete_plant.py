"""Use case for deleting an existing plant."""

from src.use_cases.ports.plant_repository import PlantRepository


class DeletePlantUseCase:
    """Remove a plant and its related resources."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, plant_id: int) -> bool:
        return self._repository.delete_plant(plant_id)
