"""Blueprint con rutas relacionadas a plantas y sus áreas."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

from src.infrastructure.flask.auth import AuthService, ScopeAuthorizer
from src.infrastructure.flask.helpers import (
    _map_localized_fields,
    _require_fields,
    _require_json,
)
from src.interface_adapters.presenters.area_presenter import (
    present as present_area,
    present_many as present_areas,
)
from src.interface_adapters.presenters.plant_presenter import (
    present as present_plant,
    present_many as present_plants,
)
from src.use_cases.create_area import CreateAreaUseCase
from src.use_cases.create_plant import CreatePlantUseCase
from src.use_cases.get_plant import GetPlantUseCase
from src.use_cases.list_plant_areas import ListPlantAreasUseCase
from src.use_cases.list_plants import ListPlantsUseCase
from src.use_cases.update_plant import UpdatePlantUseCase
from src.use_cases.delete_plant import DeletePlantUseCase


def build_plants_blueprint(
    list_plants_use_case: ListPlantsUseCase,
    get_plant_use_case: GetPlantUseCase,
    create_plant_use_case: CreatePlantUseCase,
    update_plant_use_case: UpdatePlantUseCase,
    delete_plant_use_case: DeletePlantUseCase,
    list_plant_areas_use_case: ListPlantAreasUseCase,
    create_area_use_case: CreateAreaUseCase,
    auth_service: AuthService,
    scope_authorizer: ScopeAuthorizer,
) -> Blueprint:
    """Crea un blueprint específico para las rutas de plantas."""

    plants_bp = Blueprint("plants", __name__, url_prefix="/plantas")

    @plants_bp.get("")
    def list_plants():
        auth_service.require_claims(request)
        plants = list_plants_use_case.execute()
        return jsonify(present_plants(plants))

    @plants_bp.post("")
    def create_plant():
        claims = auth_service.require_claims(request)
        scope_authorizer.ensure_superadmin(claims)

        payload = _require_json()
        _require_fields(payload, ["nombre"])
        data = _map_localized_fields(payload)
        created = create_plant_use_case.execute(
            name=data["name"],
            location=data.get("location"),
            status=data.get("status"),
        )
        return jsonify(present_plant(created)), 201

    @plants_bp.get("/<int:plant_id>")
    def get_plant(plant_id: int):
        auth_service.require_claims(request)
        plant = get_plant_use_case.execute(plant_id)
        if plant is None:
            raise NotFound("Planta no encontrada")
        return jsonify(present_plant(plant))

    @plants_bp.put("/<int:plant_id>")
    def update_plant(plant_id: int):
        claims = auth_service.require_claims(request)
        scope_authorizer.ensure_superadmin(claims)

        payload = _require_json()
        update_data = _map_localized_fields(payload)
        if not update_data:
            raise BadRequest("No se enviaron campos para actualizar")

        updated = update_plant_use_case.execute(plant_id, **update_data)
        if updated is None:
            raise NotFound("Planta no encontrada")

        return jsonify(present_plant(updated))

    @plants_bp.delete("/<int:plant_id>")
    def delete_plant(plant_id: int):
        claims = auth_service.require_claims(request)
        scope_authorizer.ensure_superadmin(claims)

        deleted = delete_plant_use_case.execute(plant_id)
        if not deleted:
            raise NotFound("Planta no encontrada")
        return ("", 204)

    @plants_bp.get("/<int:plant_id>/areas")
    def list_plant_areas(plant_id: int):
        claims = auth_service.require_claims(request)
        plant = get_plant_use_case.execute(plant_id)
        if plant is None:
            raise NotFound("Planta no encontrada")

        areas = list_plant_areas_use_case.execute(plant_id)
        scoped = scope_authorizer.filter_areas(claims, plant_id, areas)
        return jsonify(present_areas(scoped))

    @plants_bp.post("/<int:plant_id>/areas")
    def create_area(plant_id: int):
        claims = auth_service.require_claims(request)
        scope_authorizer.ensure_can_create_area(claims, plant_id)

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

    return plants_bp
