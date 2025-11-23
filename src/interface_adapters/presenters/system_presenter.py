"""Transform system entities into API responses."""

from typing import Sequence

from src.entities.system import System


def present(system: System) -> dict[str, int | str]:
    return {
        "id": system.id,
        "equipoId": system.equipment_id,
        "nombre": system.name,
        "estado": system.status,
    }


def present_many(systems: Sequence[System]) -> list[dict[str, int | str]]:
    return [present(system) for system in systems]
