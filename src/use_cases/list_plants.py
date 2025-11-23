"""Use case for retrieving registered plants."""

from typing import Sequence

from src.entities.plant import Plant
from src.use_cases.ports.plant_repository import PlantRepository


class ListPlantsUseCase:
    """Coordinate the retrieval of plants from a repository."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self) -> Sequence[Plant]:
        return self._repository.list_plants()
