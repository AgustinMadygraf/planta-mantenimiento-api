"""HTTP controller for plant endpoints."""

from fastapi import APIRouter

from src.interface_adapters.gateways.in_memory_plant_repository import InMemoryPlantRepository
from src.interface_adapters.presenters.plant_presenter import present_many
from src.use_cases.list_plants import ListPlantsUseCase

router = APIRouter(prefix="/api/plantas", tags=["Plantas"])

_list_plants_use_case = ListPlantsUseCase(InMemoryPlantRepository())


@router.get("", summary="Lista las plantas registradas")
async def list_plants() -> list[dict[str, str | int]]:
    plants = _list_plants_use_case.execute()
    return present_many(plants)
