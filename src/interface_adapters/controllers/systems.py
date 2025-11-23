"""HTTP controller for system endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.interface_adapters.presenters.system_presenter import present as present_system
from src.use_cases.delete_system import DeleteSystemUseCase
from src.use_cases.update_system import UpdateSystemUseCase
from src.use_cases.ports.plant_repository import PlantRepository


class SystemUpdatePayload(BaseModel):
    nombre: str | None = None
    estado: str | None = None


def _dump_payload(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


def build_router(repository: PlantRepository) -> APIRouter:
    router = APIRouter(prefix="/api/sistemas", tags=["Sistemas"])

    update_system_use_case = UpdateSystemUseCase(repository)
    delete_system_use_case = DeleteSystemUseCase(repository)

    @router.put("/{system_id}", summary="Actualiza un sistema")
    async def update_system(system_id: int, payload: SystemUpdatePayload) -> dict[str, int | str]:
        update_data = _dump_payload(payload)
        if not update_data:
            raise HTTPException(status_code=400, detail="No se enviaron campos para actualizar")

        updated = update_system_use_case.execute(system_id, name=update_data.get("nombre"), status=update_data.get("estado"))
        if updated is None:
            raise HTTPException(status_code=404, detail="Sistema no encontrado")

        return present_system(updated)

    @router.delete("/{system_id}", summary="Elimina un sistema", status_code=204)
    async def delete_system(system_id: int) -> None:
        deleted = delete_system_use_case.execute(system_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Sistema no encontrado")

    return router


