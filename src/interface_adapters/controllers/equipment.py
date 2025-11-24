"""HTTP controller for equipment endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.interface_adapters.presenters.equipment_presenter import present as present_equipment
from src.interface_adapters.presenters.system_presenter import present_many as present_systems
from src.use_cases.ports.plant_repository import PlantRepository
from src.use_cases.create_system import CreateSystemUseCase
from src.use_cases.delete_equipment import DeleteEquipmentUseCase
from src.use_cases.get_equipment import GetEquipmentUseCase
from src.use_cases.list_equipment_systems import ListEquipmentSystemsUseCase
from src.use_cases.update_equipment import UpdateEquipmentUseCase

class EquipmentUpdatePayload(BaseModel):
    nombre: str | None = None
    estado: str | None = None


class SystemCreatePayload(BaseModel):
    nombre: str = Field(..., min_length=1)
    estado: str | None = None


def _dump_payload(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


def build_router(repository: PlantRepository) -> APIRouter:
    router = APIRouter(prefix="/api/equipos", tags=["Equipos"])

    get_equipment_use_case = GetEquipmentUseCase(repository)
    update_equipment_use_case = UpdateEquipmentUseCase(repository)
    delete_equipment_use_case = DeleteEquipmentUseCase(repository)
    list_equipment_systems_use_case = ListEquipmentSystemsUseCase(repository)
    create_system_use_case = CreateSystemUseCase(repository)

    @router.put("/{equipment_id}", summary="Actualiza un equipo")
    async def update_equipment(equipment_id: int, payload: EquipmentUpdatePayload) -> dict[str, int | str]:
        update_data = _dump_payload(payload)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

        updated = update_equipment_use_case.execute(
            equipment_id,
            name=update_data.get("nombre"),
            status=update_data.get("estado"),
        )
        if updated is None:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")

        return present_equipment(updated)

    @router.delete("/{equipment_id}", summary="Elimina un equipo", status_code=204)
    async def delete_equipment(equipment_id: int) -> None:
        deleted = delete_equipment_use_case.execute(equipment_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")

    @router.get("/{equipment_id}/sistemas", summary="Lista los sistemas de un equipo")
    async def list_equipment_systems(equipment_id: int) -> list[dict[str, int | str]]:
        equipment = get_equipment_use_case.execute(equipment_id)
        if equipment is None:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")

        systems = list_equipment_systems_use_case.execute(equipment_id)
        return present_systems(systems)

    @router.post("/{equipment_id}/sistemas", summary="Crea un sistema dentro de un equipo", status_code=201)
    async def create_system(equipment_id: int, payload: SystemCreatePayload) -> dict[str, int | str]:
        equipment = get_equipment_use_case.execute(equipment_id)
        if equipment is None:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")

        created = create_system_use_case.execute(equipment_id, name=payload.nombre, status=payload.estado)
        if created is None:
            raise HTTPException(status_code=404, detail="No se pudo crear el sistema")

        return present_systems([created])[0]

    return router


