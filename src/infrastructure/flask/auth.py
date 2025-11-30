"""
Path: src/infrastructure/flask/auth.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from flask import Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.exceptions import Forbidden, Unauthorized
from werkzeug.security import check_password_hash

from src.entities.area import Area
from src.entities.equipment import Equipment
from src.entities.system import System
from src.shared.config import get_env, get_superadmin_credentials
from src.shared.logger import get_logger
from src.infrastructure.user_repository import (
    InMemoryUserRepository,
    UserRepository,
    User,
)


logger = get_logger(__name__)


ALLOWED_ROLES = {
    "superadministrador",
    "administrador",
    "maquinista",
    "invitado",
}


def mask_authorization_header(auth_header: str) -> str:
    """Devuelve una versión segura del header Authorization para logging."""

    scheme, _, token = auth_header.partition(" ")
    token = token.strip()

    if not token:
        return scheme or "<sin esquema>"

    if len(token) <= 8:
        masked = f"{token[:2]}...{token[-2:]}"
    else:
        masked = f"{token[:4]}...{token[-4:]}"

    return f"{scheme} {masked}".strip()


@dataclass(slots=True)
class AuthClaims:
    "Claims de autorización extraídos de un token."

    username: str
    role: str
    areas: list[int]
    equipos: list[int]


@dataclass(slots=True)
class AuthUser(AuthClaims):
    "Usuario autenticable con credenciales."

    password: str


def _default_users() -> dict[str, AuthUser]:
    "Usuarios de demostración acordes a los roles del frontend."

    superadmin_username, superadmin_password = get_superadmin_credentials()

    return {
        superadmin_username: AuthUser(
            username=superadmin_username,
            password=superadmin_password,
            role="superadministrador",
            areas=[],
            equipos=[],
        ),
        "admin": AuthUser(
            username="admin",
            password="admin",
            role="administrador",
            areas=[101, 201],
            equipos=[],
        ),
        "maquinista": AuthUser(
            username="maquinista",
            password="maquinista",
            role="maquinista",
            areas=[],
            equipos=[1001],
        ),
        "invitado": AuthUser(
            username="invitado",
            password="invitado",
            role="invitado",
            areas=[],
            equipos=[],
        ),
    }


class AuthService:
    """Emite y valida tokens firmados con claims de autorización."""

    def __init__(
        self,
        *,
        secret_key: str | None = None,
        token_ttl_seconds: int | None = None,
        user_repository: UserRepository | None = None,
    ) -> None:
        self._secret_key = secret_key or get_env("AUTH_SECRET_KEY", "dev-secret-key")
        self._token_ttl = token_ttl_seconds or int(
            get_env("AUTH_TOKEN_TTL_SECONDS", "3600")
        )
        self._user_repository = (
            user_repository or InMemoryUserRepository.with_defaults()
        )
        self._serializer = URLSafeTimedSerializer(self._secret_key, salt="auth")

    def issue_token(self, username: str, password: str) -> str:
        "Emite un token JWT si las credenciales son válidas."
        user = self._user_repository.get_by_username(username)
        if user is None or not check_password_hash(user.password_hash, password):
            logger.warning(
                "Intento de login con credenciales inválidas",
                extra={"username": username},
            )
            raise Unauthorized("Credenciales inválidas")

        logger.info("Login exitoso", extra={"username": username})
        payload = self._claims_from_user(user)
        return self._serializer.dumps(payload)

    def _claims_from_user(self, user: User) -> dict[str, object]:
        return {
            "username": user.username,
            "role": user.role,
            "areas": list(user.areas),
            "equipos": list(user.equipos),
        }

    def decode_token(self, token: str) -> AuthClaims:
        "Decodifica y valida un token, devolviendo sus claims."
        try:
            data = self._serializer.loads(token, max_age=self._token_ttl)
        except (
            SignatureExpired
        ) as exc:  # pragma: no cover - paths cubiertos por BadSignature
            logger.warning("Token expirado")
            raise Unauthorized("Token expirado") from exc
        except BadSignature as exc:
            logger.warning("Token inválido")
            raise Unauthorized("Token inválido") from exc

        role = data.get("role")
        if role not in ALLOWED_ROLES:
            logger.error("Token con rol no permitido", extra={"role": role})
            raise Unauthorized("Rol inválido en el token")

        logger.debug(
            "Token decodificado correctamente",
            extra={"username": data.get("username", ""), "role": role},
        )
        return AuthClaims(
            username=data.get("username", ""),
            role=role,
            areas=list(data.get("areas", []) or []),
            equipos=list(data.get("equipos", []) or []),
        )

    def require_claims(self, request: Request) -> AuthClaims:
        "Extrae y valida los claims de autorización del header Authorization."
        auth_header = request.headers.get("Authorization", "").strip()
        if not auth_header:
            logger.warning(
                "Solicitud sin header Authorization",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "headers_presentes": sorted(request.headers.keys()),
                },
            )
            raise Unauthorized("Falta token de autenticación")

        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer":
            logger.warning(
                "Esquema de autorización inválido",
                extra={
                    "scheme": scheme,
                    "auth_header": mask_authorization_header(auth_header),
                },
            )
            raise Unauthorized("Falta token de autenticación")

        token = token.strip()
        if not token:
            logger.warning(
                "Token vacío en header Authorization",
                extra={"auth_header": mask_authorization_header(auth_header)},
            )
            raise Unauthorized("Token incompleto")

        logger.debug(
            "Token recibido, procediendo a validación",
            extra={"auth_header": mask_authorization_header(auth_header)},
        )
        return self.decode_token(token)


class ScopeAuthorizer:
    "Valida permisos por rol y alcance sobre entidades jerárquicas."

    def __init__(
        self,
        *,
        get_area: Callable[[int], Area | None],
        get_equipment: Callable[[int], Equipment | None],
        get_system: Callable[[int], System | None],
    ) -> None:
        self._get_area = get_area
        self._get_equipment = get_equipment
        self._get_system = get_system

    def ensure_superadmin(self, claims: AuthClaims) -> None:
        "Verifica que el usuario tenga rol de superadministrador."
        if claims.role != "superadministrador":
            raise Forbidden("Se requiere rol superadministrador")

    def ensure_can_manage_area(self, claims: AuthClaims, area_id: int) -> Area:
        "Verifica si el usuario puede administrar el área dada."
        area = self._get_area(area_id)
        if area is None:
            raise Forbidden("Área fuera de alcance")

        if claims.role == "superadministrador":
            return area
        if claims.role == "administrador" and area.id in set(claims.areas):
            return area

        raise Forbidden("El usuario no puede administrar esta área")

    def ensure_can_create_area(self, claims: AuthClaims, plant_id: int) -> None:
        "Verifica si el usuario puede crear un área en la planta dada."
        if claims.role == "superadministrador":
            return

        if claims.role != "administrador":
            raise Forbidden("Solo administradores pueden crear áreas")

        scoped_plants = {
            area.plant_id
            for area in self._areas_from_ids(claims.areas)
            if area is not None
        }
        if plant_id not in scoped_plants:
            raise Forbidden("El área a crear no está en el alcance del administrador")

    def ensure_can_manage_equipment(
        self, claims: AuthClaims, equipment_id: int
    ) -> Equipment:
        "Verifica si el usuario puede administrar el equipo dado."
        equipment = self._get_equipment(equipment_id)
        if equipment is None:
            raise Forbidden("Equipo fuera de alcance")

        if claims.role == "superadministrador":
            return equipment

        if claims.role == "administrador" and equipment.area_id in set(claims.areas):
            return equipment

        if claims.role == "maquinista" and equipment.id in set(claims.equipos):
            return equipment

        raise Forbidden("El usuario no puede administrar este equipo")

    def ensure_can_create_equipment(self, claims: AuthClaims, area_id: int) -> None:
        "Verifica si el usuario puede crear un equipo en el área dada."
        if claims.role == "superadministrador":
            return

        if claims.role != "administrador":
            raise Forbidden("Solo administradores pueden crear equipos")

        if area_id not in set(claims.areas):
            raise Forbidden(
                "El área del equipo no está en el alcance del administrador"
            )

    def ensure_can_manage_system(self, claims: AuthClaims, system_id: int) -> System:
        "Verifica si el usuario puede administrar el sistema dado."
        system = self._get_system(system_id)
        if system is None:
            raise Forbidden("Sistema fuera de alcance")

        equipment = self.ensure_can_manage_equipment(claims, system.equipment_id)
        if equipment is None:  # pragma: no cover - defensive
            raise Forbidden("Equipo no asociado al sistema")

        return system

    def ensure_can_create_system(self, claims: AuthClaims, equipment_id: int) -> None:
        "Verifica si el usuario puede crear un sistema en el equipo dado."
        self.ensure_can_manage_equipment(claims, equipment_id)

    def filter_areas(
        self, claims: AuthClaims, plant_id: int, areas: Sequence[Area]
    ) -> list[Area]:
        "Filtra áreas según los claims del usuario y el plant_id solicitado."
        if claims.role in {"superadministrador", "invitado"}:
            return list(areas)

        allowed_area_ids = set(claims.areas)
        if claims.role == "administrador":
            return [area for area in areas if area.id in allowed_area_ids]

        if claims.role == "maquinista":
            allowed_equipment = {
                eq.id: eq
                for eq in self._equipment_from_ids(claims.equipos)
                if eq is not None
            }
            return [
                area
                for area in areas
                if any(eq.area_id == area.id for eq in allowed_equipment.values())
            ]

        return []

    def filter_equipment(
        self, claims: AuthClaims, area_id: int, equipment: Sequence[Equipment]
    ) -> list[Equipment]:
        "Filtra equipos según los claims del usuario."
        if claims.role in {"superadministrador", "invitado"}:
            return list(equipment)

        if claims.role == "administrador":
            if area_id not in set(claims.areas):
                return []
            return list(equipment)

        if claims.role == "maquinista":
            allowed = set(claims.equipos)
            return [eq for eq in equipment if eq.id in allowed]

        return []

    def filter_systems(
        self, claims: AuthClaims, equipment_id: int, systems: Sequence[System]
    ) -> list[System]:
        "Filtra sistemas según los claims del usuario."
        try:
            self.ensure_can_manage_equipment(claims, equipment_id)
        except Forbidden:
            return []

        return list(systems)

    def _areas_from_ids(self, area_ids: Iterable[int]) -> list[Area | None]:
        return [self._get_area(area_id) for area_id in area_ids]

    def _equipment_from_ids(
        self, equipment_ids: Iterable[int]
    ) -> list[Equipment | None]:
        return [
            self._get_equipment(eq_id) for eq_id in equipment_ids if eq_id is not None
        ]
