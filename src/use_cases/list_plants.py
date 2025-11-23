"""Use case for retrieving registered plants."""

from typing import Protocol, Sequence

from src.entities.plant import Plant


class PlantRepository(Protocol):
    """Contract required to retrieve plant information."""

    def list_plants(self) -> Sequence[Plant]:
        ...


class ListPlantsUseCase:
    """Coordinate the retrieval of plants from a repository."""

    def __init__(self, repository: PlantRepository) -> None:
        self._repository = repository

    def execute(self) -> Sequence[Plant]:
        return self._repository.list_plants()
