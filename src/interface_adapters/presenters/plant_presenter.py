"""Transform plant entities into API responses."""

from typing import Sequence

from src.entities.plant import Plant


def present(plant: Plant) -> dict[str, str | int]:
    return {
        "id": plant.id,
        "name": plant.name,
        "location": plant.location,
        "status": plant.status,
    }


def present_many(plants: Sequence[Plant]) -> list[dict[str, str | int]]:
    return [present(plant) for plant in plants]
