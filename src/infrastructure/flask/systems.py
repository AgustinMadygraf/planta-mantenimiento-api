"""Blueprint con rutas relacionadas a sistemas."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

from src.infrastructure.flask.auth import AuthService, ScopeAuthorizer
from src.infrastructure.flask.helpers import _require_json, _validate_payload
from src.interface_adapters.presenters.system_presenter import present as present_system
from src.interface_adapters.schemas import SystemUpdate
from src.use_cases.get_system import GetSystemUseCase
from src.use_cases.delete_system import DeleteSystemUseCase
from src.use_cases.update_system import UpdateSystemUseCase


def build_systems_blueprint(
    get_system_use_case: GetSystemUseCase,
    update_system_use_case: UpdateSystemUseCase,
    delete_system_use_case: DeleteSystemUseCase,
    auth_service: AuthService,
    scope_authorizer: ScopeAuthorizer,
) -> Blueprint:
    """Crea un blueprint específico para las rutas de sistemas."""

    systems_bp = Blueprint("systems", __name__, url_prefix="/sistemas")

    @systems_bp.put("/<int:system_id>")
    def update_system(system_id: int):
        claims = auth_service.require_claims(request)
        system = scope_authorizer.ensure_can_manage_system(claims, system_id)

        payload = _require_json()
        update_data = _validate_payload(payload, SystemUpdate)

        updated = update_system_use_case.execute(system.id, **update_data)
        if updated is None:
            raise NotFound("Sistema no encontrado")

        return jsonify(present_system(updated))

    @systems_bp.delete("/<int:system_id>")
    def delete_system(system_id: int):
        claims = auth_service.require_claims(request)
        system = scope_authorizer.ensure_can_manage_system(claims, system_id)

        deleted = delete_system_use_case.execute(system.id)
        if not deleted:
            raise NotFound("Sistema no encontrado")
        return ("", 204)

    return systems_bp
