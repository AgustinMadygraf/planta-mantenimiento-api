"""HTTP controller for area endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.interface_adapters.presenters.area_presenter import present as present_area
from src.interface_adapters.presenters.equipment_presenter import present_many as present_equipment
from src.use_cases.ports.plant_repository import PlantRepository
from src.use_cases.create_equipment import CreateEquipmentUseCase
from src.use_cases.delete_area import DeleteAreaUseCase
from src.use_cases.get_area import GetAreaUseCase
from src.use_cases.list_area_equipment import ListAreaEquipmentUseCase
from src.use_cases.update_area import UpdateAreaUseCase

class AreaUpdatePayload(BaseModel):
    nombre: str | None = None
    estado: str | None = None


class EquipmentCreatePayload(BaseModel):
    nombre: str = Field(..., min_length=1)
    estado: str | None = None


def _dump_payload(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


def build_router(repository: PlantRepository) -> APIRouter:
    router = APIRouter(prefix="/api/areas", tags=["Áreas"])

    get_area_use_case = GetAreaUseCase(repository)
    update_area_use_case = UpdateAreaUseCase(repository)
    delete_area_use_case = DeleteAreaUseCase(repository)
    list_area_equipment_use_case = ListAreaEquipmentUseCase(repository)
    create_equipment_use_case = CreateEquipmentUseCase(repository)

    @router.put("/{area_id}", summary="Actualiza un área")
    async def update_area(area_id: int, payload: AreaUpdatePayload) -> dict[str, int | str]:
        update_data = _dump_payload(payload)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

        updated = update_area_use_case.execute(area_id, name=update_data.get("nombre"), status=update_data.get("estado"))
        if updated is None:
            raise HTTPException(status_code=404, detail="Área no encontrada")

        return present_area(updated)

    @router.delete("/{area_id}", summary="Elimina un área", status_code=204)
    async def delete_area(area_id: int) -> None:
        deleted = delete_area_use_case.execute(area_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Área no encontrada")

    @router.get("/{area_id}/equipos", summary="Lista los equipos de un área")
    async def list_area_equipment(area_id: int) -> list[dict[str, int | str]]:
        area = get_area_use_case.execute(area_id)
        if area is None:
            raise HTTPException(status_code=404, detail="Área no encontrada")

        equipment = list_area_equipment_use_case.execute(area_id)
        return present_equipment(equipment)

    @router.post("/{area_id}/equipos", summary="Crea un equipo dentro de un área", status_code=201)
    async def create_equipment(area_id: int, payload: EquipmentCreatePayload) -> dict[str, int | str]:
        area = get_area_use_case.execute(area_id)
        if area is None:
            raise HTTPException(status_code=404, detail="Área no encontrada")

        created = create_equipment_use_case.execute(area_id, name=payload.nombre, status=payload.estado)
        if created is None:
            raise HTTPException(status_code=404, detail="No se pudo crear el equipo")

        return present_equipment([created])[0]

    return router


