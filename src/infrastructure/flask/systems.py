"""Blueprint con rutas relacionadas a sistemas."""

from __future__ import annotations

from flask import Blueprint, jsonify
from werkzeug.exceptions import BadRequest, NotFound

from src.infrastructure.flask.helpers import _require_json
from src.interface_adapters.presenters.system_presenter import present as present_system
from src.use_cases.delete_system import DeleteSystemUseCase
from src.use_cases.update_system import UpdateSystemUseCase


def build_systems_blueprint(
    update_system_use_case: UpdateSystemUseCase,
    delete_system_use_case: DeleteSystemUseCase,
) -> Blueprint:
    """Crea un blueprint específico para las rutas de sistemas."""

    systems_bp = Blueprint("systems", __name__, url_prefix="/sistemas")

    @systems_bp.put("/<int:system_id>")
    def update_system(system_id: int):
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

        updated = update_system_use_case.execute(system_id, **update_data)
        if updated is None:
            raise NotFound("Sistema no encontrado")

        return jsonify(present_system(updated))

    @systems_bp.delete("/<int:system_id>")
    def delete_system(system_id: int):
        deleted = delete_system_use_case.execute(system_id)
        if not deleted:
            raise NotFound("Sistema no encontrado")
        return ("", 204)

    return systems_bp
