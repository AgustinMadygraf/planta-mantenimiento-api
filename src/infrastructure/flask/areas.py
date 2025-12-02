"""Blueprint con rutas relacionadas a áreas y sus equipos."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

from src.infrastructure.flask.auth import AuthService, ScopeAuthorizer
from src.infrastructure.flask.helpers import _require_json, _validate_payload
from src.interface_adapters.presenters.area_presenter import present as present_area
from src.interface_adapters.presenters.equipment_presenter import (
    present as present_equipment,
    present_many as present_equipment_list,
)
from src.interface_adapters.schemas import AreaCreate, AreaUpdate, EquipmentCreate
from src.use_cases.create_equipment import CreateEquipmentUseCase
from src.use_cases.delete_area import DeleteAreaUseCase
from src.use_cases.get_area import GetAreaUseCase
from src.use_cases.list_area_equipment import ListAreaEquipmentUseCase
from src.use_cases.update_area import UpdateAreaUseCase


def build_areas_blueprint(
    get_area_use_case: GetAreaUseCase,
    update_area_use_case: UpdateAreaUseCase,
    delete_area_use_case: DeleteAreaUseCase,
    list_area_equipment_use_case: ListAreaEquipmentUseCase,
    create_equipment_use_case: CreateEquipmentUseCase,
    auth_service: AuthService,
    scope_authorizer: ScopeAuthorizer,
) -> Blueprint:
    """Crea un blueprint específico para las rutas de áreas."""

    areas_bp = Blueprint("areas", __name__, url_prefix="/areas")

    @areas_bp.put("/<int:area_id>")
    def update_area(area_id: int):
        claims = auth_service.require_claims(request)
        area = scope_authorizer.ensure_can_manage_area(claims, area_id)

        payload = _require_json()
        update_data = _validate_payload(payload, AreaUpdate)
        updated = update_area_use_case.execute(area.id, **update_data)
        if updated is None:
            raise NotFound("Área no encontrada")

        return jsonify(present_area(updated))

    @areas_bp.delete("/<int:area_id>")
    def delete_area(area_id: int):
        claims = auth_service.require_claims(request)
        area = scope_authorizer.ensure_can_manage_area(claims, area_id)

        deleted = delete_area_use_case.execute(area.id)
        if not deleted:
            raise NotFound("Área no encontrada")
        return ("", 204)

    @areas_bp.get("/<int:area_id>/equipos")
    def list_area_equipment(area_id: int):
        claims = auth_service.require_claims(request)
        area = get_area_use_case.execute(area_id)
        if area is None:
            raise NotFound("Área no encontrada")

        equipment = list_area_equipment_use_case.execute(area_id)
        scoped = scope_authorizer.filter_equipment(claims, area_id, equipment)
        return jsonify(present_equipment_list(scoped))

    @areas_bp.post("/<int:area_id>/equipos")
    def create_equipment(area_id: int):
        claims = auth_service.require_claims(request)
        scope_authorizer.ensure_can_create_equipment(claims, area_id)

        payload = _require_json()
        data = _validate_payload(payload, EquipmentCreate)

        area = get_area_use_case.execute(area_id)
        if area is None:
            raise NotFound("Área no encontrada")

        created = create_equipment_use_case.execute(area_id, **data)
        if created is None:
            raise NotFound("No se pudo crear el equipo")

        return jsonify(present_equipment(created)), 201

    return areas_bp
