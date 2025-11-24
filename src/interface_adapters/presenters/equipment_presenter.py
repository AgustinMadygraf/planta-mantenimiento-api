"""Transform equipment entities into API responses."""

from typing import Sequence

from src.entities.equipment import Equipment


def present(equipment: Equipment) -> dict[str, int | str]:
    return {
        "id": equipment.id,
        "areaId": equipment.area_id,
        "nombre": equipment.name,
        "estado": equipment.status,
    }


def present_many(equipment: Sequence[Equipment]) -> list[dict[str, int | str]]:
    return [present(item) for item in equipment]
