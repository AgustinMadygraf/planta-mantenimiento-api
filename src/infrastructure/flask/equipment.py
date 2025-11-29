"""Blueprint con rutas relacionadas a equipos y sus sistemas."""

from __future__ import annotations

from flask import Blueprint, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from src.infrastructure.flask.helpers import _require_fields, _require_json
from src.interface_adapters.presenters.equipment_presenter import present as present_equipment
from src.interface_adapters.presenters.system_presenter import (
    present as present_system,
    present_many as present_systems,
)
from src.use_cases.create_system import CreateSystemUseCase
from src.use_cases.delete_equipment import DeleteEquipmentUseCase
from src.use_cases.get_equipment import GetEquipmentUseCase
from src.use_cases.list_equipment_systems import ListEquipmentSystemsUseCase
from src.use_cases.update_equipment import UpdateEquipmentUseCase


def build_equipment_blueprint(
    get_equipment_use_case: GetEquipmentUseCase,
    update_equipment_use_case: UpdateEquipmentUseCase,
    delete_equipment_use_case: DeleteEquipmentUseCase,
    list_equipment_systems_use_case: ListEquipmentSystemsUseCase,
    create_system_use_case: CreateSystemUseCase,
) -> Blueprint:
    """Crea un blueprint específico para las rutas de equipos."""

    equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipos")

    @equipment_bp.put("/<int:equipment_id>")
    def update_equipment(equipment_id: int):
        payload = _require_json()
        update_data = {
            "name": payload.get("nombre"),
            "status": payload.get("estado"),
        }
        update_data = {
            key: value for key, value in update_data.items() if value is not None
        }
        if not update_data:
            raise BadRequest("No se enviaron campos para actualizar")

        updated = update_equipment_use_case.execute(equipment_id, **update_data)
        if updated is None:
            raise NotFound("Equipo no encontrado")

        return jsonify(present_equipment(updated))

    @equipment_bp.delete("/<int:equipment_id>")
    def delete_equipment(equipment_id: int):
        deleted = delete_equipment_use_case.execute(equipment_id)
        if not deleted:
            raise NotFound("Equipo no encontrado")
        return ("", 204)

    @equipment_bp.get("/<int:equipment_id>/sistemas")
    def list_equipment_systems(equipment_id: int):
        equipment = get_equipment_use_case.execute(equipment_id)
        if equipment is None:
            raise NotFound("Equipo no encontrado")

        systems = list_equipment_systems_use_case.execute(equipment_id)
        return jsonify(present_systems(systems))

    @equipment_bp.post("/<int:equipment_id>/sistemas")
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

    return equipment_bp
