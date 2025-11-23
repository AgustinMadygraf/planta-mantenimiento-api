"""HTTP controller for plant endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.interface_adapters.presenters.area_presenter import (
    present as present_area,
    present_many as present_areas,
)
from src.interface_adapters.presenters.plant_presenter import present, present_many
from src.use_cases.ports.plant_repository import PlantRepository
from src.use_cases.create_area import CreateAreaUseCase
from src.use_cases.create_plant import CreatePlantUseCase
from src.use_cases.delete_plant import DeletePlantUseCase
from src.use_cases.get_plant import GetPlantUseCase
from src.use_cases.list_plant_areas import ListPlantAreasUseCase
from src.use_cases.list_plants import ListPlantsUseCase
from src.use_cases.update_plant import UpdatePlantUseCase

class PlantCreatePayload(BaseModel):
    nombre: str = Field(..., min_length=1)
    ubicacion: str | None = None
    estado: str | None = None


class PlantUpdatePayload(BaseModel):
    nombre: str | None = None
    ubicacion: str | None = None
    estado: str | None = None


class AreaCreatePayload(BaseModel):
    nombre: str = Field(..., min_length=1)
    estado: str | None = None


def _dump_payload(model: BaseModel) -> dict[str, Any]:
    """Support Pydantic v1 and v2 when extracting payload data."""

    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


def _map_localized_fields(payload: dict[str, Any]) -> dict[str, Any]:
    mapped = {
        "name": payload.get("nombre"),
        "location": payload.get("ubicacion"),
        "status": payload.get("estado"),
    }

    return {key: value for key, value in mapped.items() if value is not None}


def build_router(repository: PlantRepository) -> APIRouter:
    router = APIRouter(prefix="/api/plantas", tags=["Plantas"])

    list_plants_use_case = ListPlantsUseCase(repository)
    get_plant_use_case = GetPlantUseCase(repository)
    create_plant_use_case = CreatePlantUseCase(repository)
    update_plant_use_case = UpdatePlantUseCase(repository)
    delete_plant_use_case = DeletePlantUseCase(repository)
    list_plant_areas_use_case = ListPlantAreasUseCase(repository)
    create_area_use_case = CreateAreaUseCase(repository)

    @router.get("", summary="Lista las plantas registradas")
    async def list_plants() -> list[dict[str, str | int]]:
        plants = list_plants_use_case.execute()
        return present_many(plants)

    @router.post("", summary="Crea una nueva planta", status_code=201)
    async def create_plant(payload: PlantCreatePayload) -> dict[str, str | int]:
        data = _map_localized_fields(_dump_payload(payload))
        created = create_plant_use_case.execute(
            name=data["name"],
            location=data.get("location"),
            status=data.get("status"),
        )
        return present(created)

    @router.get("/{plant_id}", summary="Obtiene una planta por su identificador")
    async def get_plant(plant_id: int) -> dict[str, str | int]:
        plant = get_plant_use_case.execute(plant_id)
        if plant is None:
            raise HTTPException(status_code=404, detail="Planta no encontrada")
        return present(plant)

    @router.put("/{plant_id}", summary="Actualiza los datos de una planta")
    async def update_plant(plant_id: int, payload: PlantUpdatePayload) -> dict[str, str | int]:
        update_data = _map_localized_fields(_dump_payload(payload))
        if not update_data:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

        updated = update_plant_use_case.execute(plant_id, **update_data)
        if updated is None:
            raise HTTPException(status_code=404, detail="Planta no encontrada")

        return present(updated)

    @router.delete("/{plant_id}", summary="Elimina una planta", status_code=204)
    async def delete_plant(plant_id: int) -> None:
        deleted = delete_plant_use_case.execute(plant_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Planta no encontrada")

    @router.get("/{plant_id}/areas", summary="Lista las áreas de una planta")
    async def list_plant_areas(plant_id: int) -> list[dict[str, int | str]]:
        plant = get_plant_use_case.execute(plant_id)
        if plant is None:
            raise HTTPException(status_code=404, detail="Planta no encontrada")

        areas = list_plant_areas_use_case.execute(plant_id)
        return present_areas(areas)

    @router.post("/{plant_id}/areas", summary="Crea un área dentro de la planta", status_code=201)
    async def create_plant_area(plant_id: int, payload: AreaCreatePayload) -> dict[str, int | str]:
        plant = get_plant_use_case.execute(plant_id)
        if plant is None:
            raise HTTPException(status_code=404, detail="Planta no encontrada")

        created = create_area_use_case.execute(plant_id, name=payload.nombre, status=payload.estado)
        if created is None:
            raise HTTPException(status_code=404, detail="No se pudo crear el área")

        return present_area(created)

    return router


