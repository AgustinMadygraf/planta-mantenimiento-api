"""Transform plant entities into API responses."""

from typing import Sequence

from src.entities.plant import Plant


def present(plant: Plant) -> dict[str, str | int]:
    return {
        "id": plant.id,
        "nombre": plant.name,
        "ubicacion": plant.location,
        "estado": plant.status,
    }


def present_many(plants: Sequence[Plant]) -> list[dict[str, str | int]]:
    return [present(plant) for plant in plants]
