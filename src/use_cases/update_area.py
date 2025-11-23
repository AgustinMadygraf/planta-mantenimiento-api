"""Use case for updating an area."""

from src.entities.area import Area
from src.use_cases.ports.plant_repository import PlantRepository


class UpdateAreaUseCase:
    """Apply partial updates to an area."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self, area_id: int, *, name: str | None = None, status: str | None = None) -> Area | None:
        return self._repository.update_area(area_id, name=name, status=status)
