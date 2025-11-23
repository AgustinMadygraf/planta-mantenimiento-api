"""Blueprint HTTP controller for Flask endpoints."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

from src.interface_adapters.presenters.area_presenter import present as present_area
from src.interface_adapters.presenters.area_presenter import present_many as present_areas
from src.interface_adapters.presenters.equipment_presenter import (
    present as present_equipment,
    present_many as present_equipment_list,
)
from src.interface_adapters.presenters.plant_presenter import present as present_plant
from src.interface_adapters.presenters.plant_presenter import present_many as present_plants
from src.interface_adapters.presenters.system_presenter import (
    present as present_system,
    present_many as present_systems,
)
from src.use_cases.create_area import CreateAreaUseCase
from src.use_cases.create_equipment import CreateEquipmentUseCase
from src.use_cases.create_plant import CreatePlantUseCase
from src.use_cases.create_system import CreateSystemUseCase
from src.use_cases.delete_area import DeleteAreaUseCase
from src.use_cases.delete_equipment import DeleteEquipmentUseCase
from src.use_cases.delete_plant import DeletePlantUseCase
from src.use_cases.delete_system import DeleteSystemUseCase
from src.use_cases.get_area import GetAreaUseCase
from src.use_cases.get_equipment import GetEquipmentUseCase
from src.use_cases.get_plant import GetPlantUseCase
from src.use_cases.get_system import GetSystemUseCase
from src.use_cases.list_area_equipment import ListAreaEquipmentUseCase
from src.use_cases.list_equipment_systems import ListEquipmentSystemsUseCase
from src.use_cases.list_plant_areas import ListPlantAreasUseCase
from src.use_cases.list_plants import ListPlantsUseCase
from src.use_cases.ports.plant_repository import PlantRepository
from src.use_cases.update_area import UpdateAreaUseCase
from src.use_cases.update_equipment import UpdateEquipmentUseCase
from src.use_cases.update_plant import UpdatePlantUseCase
from src.use_cases.update_system import UpdateSystemUseCase


def _map_localized_fields(payload: dict[str, Any]) -> dict[str, Any]:
    mapped = {
        "name": payload.get("nombre"),
        "location": payload.get("ubicacion"),
        "status": payload.get("estado"),
    }
    return {key: value for key, value in mapped.items() if value is not None}


def _require_json() -> dict[str, Any]:
    data = request.get_json(silent=True)
    if data is None:
        raise BadRequest("Cuerpo JSON inválido o ausente")
    return data


def _require_fields(payload: dict[str, Any], required: list[str]) -> None:
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise BadRequest(f"Faltan campos obligatorios: {', '.join(missing)}")


def build_blueprint(repository: PlantRepository) -> Blueprint:
    api_bp = Blueprint("api", __name__, url_prefix="/api")

    @api_bp.errorhandler(BadRequest)
    def handle_bad_request(error: BadRequest):
        return jsonify({"detail": error.description}), 400

    @api_bp.errorhandler(NotFound)
    def handle_not_found(error: NotFound):
        return jsonify({"detail": error.description}), 404

    list_plants_use_case = ListPlantsUseCase(repository)
    get_plant_use_case = GetPlantUseCase(repository)
    create_plant_use_case = CreatePlantUseCase(repository)
    update_plant_use_case = UpdatePlantUseCase(repository)
    delete_plant_use_case = DeletePlantUseCase(repository)
    list_plant_areas_use_case = ListPlantAreasUseCase(repository)
    create_area_use_case = CreateAreaUseCase(repository)

    get_area_use_case = GetAreaUseCase(repository)
    update_area_use_case = UpdateAreaUseCase(repository)
    delete_area_use_case = DeleteAreaUseCase(repository)
    list_area_equipment_use_case = ListAreaEquipmentUseCase(repository)
    create_equipment_use_case = CreateEquipmentUseCase(repository)

    get_equipment_use_case = GetEquipmentUseCase(repository)
    update_equipment_use_case = UpdateEquipmentUseCase(repository)
    delete_equipment_use_case = DeleteEquipmentUseCase(repository)
    list_equipment_systems_use_case = ListEquipmentSystemsUseCase(repository)
    create_system_use_case = CreateSystemUseCase(repository)

    get_system_use_case = GetSystemUseCase(repository)
    update_system_use_case = UpdateSystemUseCase(repository)
    delete_system_use_case = DeleteSystemUseCase(repository)

    @api_bp.get("/plantas")
    def list_plants():
        plants = list_plants_use_case.execute()
        return jsonify(present_plants(plants))

    @api_bp.post("/plantas")
    def create_plant():
        payload = _require_json()
        _require_fields(payload, ["nombre"])
        data = _map_localized_fields(payload)
        created = create_plant_use_case.execute(
            name=data["name"],
            location=data.get("location"),
            status=data.get("status"),
        )
        return jsonify(present_plant(created)), 201

    @api_bp.get("/plantas/<int:plant_id>")
    def get_plant(plant_id: int):
        plant = get_plant_use_case.execute(plant_id)
        if plant is None:
            raise NotFound("Planta no encontrada")
        return jsonify(present_plant(plant))

    @api_bp.put("/plantas/<int:plant_id>")
    def update_plant(plant_id: int):
        payload = _require_json()
        update_data = _map_localized_fields(payload)
        if not update_data:
            raise BadRequest("No se enviaron campos para actualizar")

        updated = update_plant_use_case.execute(plant_id, **update_data)
        if updated is None:
            raise NotFound("Planta no encontrada")

        return jsonify(present_plant(updated))

    @api_bp.delete("/plantas/<int:plant_id>")
    def delete_plant(plant_id: int):
        deleted = delete_plant_use_case.execute(plant_id)
        if not deleted:
            raise NotFound("Planta no encontrada")
        return ("", 204)

    @api_bp.get("/plantas/<int:plant_id>/areas")
    def list_plant_areas(plant_id: int):
        plant = get_plant_use_case.execute(plant_id)
        if plant is None:
            raise NotFound("Planta no encontrada")

        areas = list_plant_areas_use_case.execute(plant_id)
        return jsonify(present_areas(areas))

    @api_bp.post("/plantas/<int:plant_id>/areas")
    def create_area(plant_id: int):
        payload = _require_json()
        _require_fields(payload, ["nombre"])

        plant = get_plant_use_case.execute(plant_id)
        if plant is None:
            raise NotFound("Planta no encontrada")

        created = create_area_use_case.execute(
            plant_id,
            name=payload["nombre"],
            status=payload.get("estado"),
        )
        if created is None:
            raise NotFound("No se pudo crear el área")

        return jsonify(present_area(created)), 201

    @api_bp.put("/areas/<int:area_id>")
    def update_area(area_id: int):
        payload = _require_json()
        update_data = {
            "name": payload.get("nombre"),
            "status": payload.get("estado"),
        }
        update_data = {key: value for key, value in update_data.items() if value is not None}
        if not update_data:
            raise BadRequest("No se enviaron campos para actualizar")

        updated = update_area_use_case.execute(area_id, **update_data)
        if updated is None:
            raise NotFound("Área no encontrada")

        return jsonify(present_area(updated))

    @api_bp.delete("/areas/<int:area_id>")
    def delete_area(area_id: int):
        deleted = delete_area_use_case.execute(area_id)
        if not deleted:
            raise NotFound("Área no encontrada")
        return ("", 204)

    @api_bp.get("/areas/<int:area_id>/equipos")
    def list_area_equipment(area_id: int):
        area = get_area_use_case.execute(area_id)
        if area is None:
            raise NotFound("Área no encontrada")

        equipment = list_area_equipment_use_case.execute(area_id)
        return jsonify(present_equipment_list(equipment))

    @api_bp.post("/areas/<int:area_id>/equipos")
    def create_equipment(area_id: int):
        payload = _require_json()
        _require_fields(payload, ["nombre"])

        area = get_area_use_case.execute(area_id)
        if area is None:
            raise NotFound("Área no encontrada")

        created = create_equipment_use_case.execute(
            area_id,
            name=payload["nombre"],
            status=payload.get("estado"),
        )
        if created is None:
            raise NotFound("No se pudo crear el equipo")

        return jsonify(present_equipment(created)), 201

    @api_bp.put("/equipos/<int:equipment_id>")
    def update_equipment(equipment_id: int):
        payload = _require_json()
        update_data = {
            "name": payload.get("nombre"),
            "status": payload.get("estado"),
        }
        update_data = {key: value for key, value in update_data.items() if value is not None}
        if not update_data:
            raise BadRequest("No se enviaron campos para actualizar")

        updated = update_equipment_use_case.execute(equipment_id, **update_data)
        if updated is None:
            raise NotFound("Equipo no encontrado")

        return jsonify(present_equipment(updated))

    @api_bp.delete("/equipos/<int:equipment_id>")
    def delete_equipment(equipment_id: int):
        deleted = delete_equipment_use_case.execute(equipment_id)
        if not deleted:
            raise NotFound("Equipo no encontrado")
        return ("", 204)

    @api_bp.get("/equipos/<int:equipment_id>/sistemas")
    def list_equipment_systems(equipment_id: int):
        equipment = get_equipment_use_case.execute(equipment_id)
        if equipment is None:
            raise NotFound("Equipo no encontrado")

        systems = list_equipment_systems_use_case.execute(equipment_id)
        return jsonify(present_systems(systems))

    @api_bp.post("/equipos/<int:equipment_id>/sistemas")
    def create_system(equipment_id: int):
        payload = _require_json()
        _require_fields(payload, ["nombre"])

        equipment = get_equipment_use_case.execute(equipment_id)
        if equipment is None:
            raise NotFound("Equipo no encontrado")

        created = create_system_use_case.execute(
            equipment_id,
            name=payload["nombre"],
            status=payload.get("estado"),
        )
        if created is None:
            raise NotFound("No se pudo crear el sistema")

        return jsonify(present_system(created)), 201

    @api_bp.put("/sistemas/<int:system_id>")
    def update_system(system_id: int):
        payload = _require_json()
        update_data = {
            "name": payload.get("nombre"),
            "status": payload.get("estado"),
        }
        update_data = {key: value for key, value in update_data.items() if value is not None}
        if not update_data:
            raise BadRequest("No se enviaron campos para actualizar")

        updated = update_system_use_case.execute(system_id, **update_data)
        if updated is None:
            raise NotFound("Sistema no encontrado")

        return jsonify(present_system(updated))

    @api_bp.delete("/sistemas/<int:system_id>")
    def delete_system(system_id: int):
        deleted = delete_system_use_case.execute(system_id)
        if not deleted:
            raise NotFound("Sistema no encontrado")
        return ("", 204)

    return api_bp
