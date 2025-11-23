"""Use case for updating plant information."""

from src.entities.plant import Plant
from src.use_cases.ports.plant_repository import PlantRepository


class UpdatePlantUseCase:
    """Apply updates to a plant and return the resulting entity."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(
        self,
        plant_id: int,
        *,
        name: str | None = None,
        location: str | None = None,
        status: str | None = None,
    ) -> Plant | None:
        return self._repository.update_plant(
            plant_id,
            name=name,
            location=location,
            status=status,
        )
