"""HTTP controller for plant endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.interface_adapters.gateways.in_memory_plant_repository import InMemoryPlantRepository
from src.interface_adapters.presenters.area_presenter import present_many as present_areas
from src.interface_adapters.presenters.plant_presenter import present, present_many
from src.use_cases.get_plant import GetPlantUseCase
from src.use_cases.list_plant_areas import ListPlantAreasUseCase
from src.use_cases.list_plants import ListPlantsUseCase
from src.use_cases.update_plant import UpdatePlantUseCase

router = APIRouter(prefix="/api/plantas", tags=["Plantas"])

_repository = InMemoryPlantRepository()
_list_plants_use_case = ListPlantsUseCase(_repository)
_get_plant_use_case = GetPlantUseCase(_repository)
_update_plant_use_case = UpdatePlantUseCase(_repository)
_list_plant_areas_use_case = ListPlantAreasUseCase(_repository)


class PlantUpdatePayload(BaseModel):
    name: str | None = None
    location: str | None = None
    status: str | None = None


def _dump_payload(model: BaseModel) -> dict[str, Any]:
    """Support Pydantic v1 and v2 when extracting payload data."""

    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


@router.get("", summary="Lista las plantas registradas")
async def list_plants() -> list[dict[str, str | int]]:
    plants = _list_plants_use_case.execute()
    return present_many(plants)


@router.get("/{plant_id}", summary="Obtiene una planta por su identificador")
async def get_plant(plant_id: int) -> dict[str, str | int]:
    plant = _get_plant_use_case.execute(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Planta no encontrada")
    return present(plant)


@router.put("/{plant_id}", summary="Actualiza los datos de una planta")
async def update_plant(plant_id: int, payload: PlantUpdatePayload) -> dict[str, str | int]:
    update_data = _dump_payload(payload)
    if not update_data:
        raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

    updated = _update_plant_use_case.execute(plant_id, **update_data)
    if updated is None:
        raise HTTPException(status_code=404, detail="Planta no encontrada")

    return present(updated)


@router.get("/{plant_id}/areas", summary="Lista las áreas de una planta")
async def list_plant_areas(plant_id: int) -> list[dict[str, int | str]]:
    plant = _get_plant_use_case.execute(plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Planta no encontrada")

    areas = _list_plant_areas_use_case.execute(plant_id)
    return present_areas(areas)
