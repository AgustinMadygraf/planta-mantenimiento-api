"""Transform area entities into API responses."""

from typing import Sequence

from src.entities.area import Area


def present(area: Area) -> dict[str, int | str]:
    return {
        "id": area.id,
        "plantaId": area.plant_id,
        "nombre": area.name,
        "estado": area.status,
    }


def present_many(areas: Sequence[Area]) -> list[dict[str, int | str]]:
    return [present(area) for area in areas]
