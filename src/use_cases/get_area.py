"""Use case for retrieving a single area."""

from src.entities.area import Area
from src.use_cases.ports.plant_repository import AreaRepository


class GetAreaUseCase:
    """Fetch an area by its identifier."""

    def __init__(self, repository: AreaRepository) -> None:
        self._repository = repository

    def execute(self, area_id: int) -> Area | None:
        return self._repository.get_area(area_id)
