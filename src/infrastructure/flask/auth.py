"""Utilidades de autenticación y autorización para Flask."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Protocol, Sequence

from flask import Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.exceptions import Forbidden, Unauthorized
from werkzeug.security import check_password_hash, generate_password_hash

from src.entities.area import Area
from src.entities.equipment import Equipment
from src.entities.system import System
from src.shared.config import get_env


ALLOWED_ROLES = {
    "superadministrador",
    "administrador",
    "maquinista",
    "invitado",
}


@dataclass(slots=True)
class AuthClaims:
    username: str
    role: str
    areas: list[int]
    equipos: list[int]


@dataclass(slots=True)
class AuthUser(AuthClaims):
    password_hash: str


class UserStore(Protocol):
    """Contrato mínimo para leer y persistir usuarios autenticables."""

    def get_user(self, username: str) -> AuthUser | None: ...

    def upsert_user(self, user: AuthUser) -> AuthUser: ...


class InMemoryUserStore(UserStore):
    """Almacén de usuarios que persiste mientras el proceso está vivo."""

    def __init__(self, seed: Mapping[str, AuthUser] | None = None) -> None:
        self._users = dict(seed or {})

    def get_user(self, username: str) -> AuthUser | None:
        return self._users.get(username)

    def upsert_user(self, user: AuthUser) -> AuthUser:
        self._users[user.username] = user
        return user


def _default_users() -> dict[str, AuthUser]:
    """Usuarios de demostración acordes a los roles del frontend."""

    return {
        "superadmin": AuthUser(
            username="superadmin",
            password_hash=generate_password_hash("superadmin"),
            role="superadministrador",
            areas=[],
            equipos=[],
        ),
        "admin": AuthUser(
            username="admin",
            password_hash=generate_password_hash("admin"),
            role="administrador",
            areas=[101, 201],
            equipos=[],
        ),
        "maquinista": AuthUser(
            username="maquinista",
            password_hash=generate_password_hash("maquinista"),
            role="maquinista",
            areas=[],
            equipos=[1001],
        ),
        "invitado": AuthUser(
            username="invitado",
            password_hash=generate_password_hash("invitado"),
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
        users: Mapping[str, AuthUser] | None = None,
        user_store: UserStore | None = None,
        bootstrap_demo_users: bool = False,
    ) -> None:
        self._secret_key = secret_key or get_env("AUTH_SECRET_KEY", "dev-secret-key")
        self._token_ttl = token_ttl_seconds or int(
            get_env("AUTH_TOKEN_TTL_SECONDS", "3600")
        )
        if user_store is not None:
            self._user_store = user_store
            if bootstrap_demo_users:
                for user in _default_users().values():
                    self._user_store.upsert_user(user)
        else:
            self._user_store = InMemoryUserStore(users or _default_users())
        self._serializer = URLSafeTimedSerializer(self._secret_key, salt="auth")

    def issue_token(self, username: str, password: str) -> str:
        user = self._user_store.get_user(username)
        if user is None or not check_password_hash(user.password_hash, password):
            raise Unauthorized("Credenciales inválidas")

        payload = {
            "username": user.username,
            "role": user.role,
            "areas": user.areas,
            "equipos": user.equipos,
        }
        return self._serializer.dumps(payload)

    def decode_token(self, token: str) -> AuthClaims:
        try:
            data = self._serializer.loads(token, max_age=self._token_ttl)
        except SignatureExpired as exc:  # pragma: no cover - paths cubiertos por BadSignature
            raise Unauthorized("Token expirado") from exc
        except BadSignature as exc:
            raise Unauthorized("Token inválido") from exc

        username = data.get("username")
        user = self._user_store.get_user(username)
        if user is None:
            raise Unauthorized("Usuario no encontrado o eliminado")

        role = user.role
        if role not in ALLOWED_ROLES:
            raise Unauthorized("Rol inválido en el token")

        return AuthClaims(
            username=user.username,
            role=role,
            areas=list(user.areas or []),
            equipos=list(user.equipos or []),
        )

    @property
    def token_ttl_seconds(self) -> int:
        return self._token_ttl

    def require_claims(self, request: Request) -> AuthClaims:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise Unauthorized("Falta token de autenticación")

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            raise Unauthorized("Token incompleto")

        return self.decode_token(token)


class ScopeAuthorizer:
    """Valida permisos por rol y alcance sobre entidades jerárquicas."""

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
        if claims.role != "superadministrador":
            raise Forbidden("Se requiere rol superadministrador")

    def ensure_can_manage_area(self, claims: AuthClaims, area_id: int) -> Area:
        area = self._get_area(area_id)
        if area is None:
            raise Forbidden("Área fuera de alcance")

        if claims.role == "superadministrador":
            return area
        if claims.role == "administrador" and area.id in set(claims.areas):
            return area

        raise Forbidden("El usuario no puede administrar esta área")

    def ensure_can_create_area(self, claims: AuthClaims, plant_id: int) -> None:
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
        if claims.role == "superadministrador":
            return

        if claims.role != "administrador":
            raise Forbidden("Solo administradores pueden crear equipos")

        if area_id not in set(claims.areas):
            raise Forbidden("El área del equipo no está en el alcance del administrador")

    def ensure_can_manage_system(self, claims: AuthClaims, system_id: int) -> System:
        system = self._get_system(system_id)
        if system is None:
            raise Forbidden("Sistema fuera de alcance")

        equipment = self.ensure_can_manage_equipment(claims, system.equipment_id)
        if equipment is None:  # pragma: no cover - defensive
            raise Forbidden("Equipo no asociado al sistema")

        return system

    def ensure_can_create_system(
        self, claims: AuthClaims, equipment_id: int
    ) -> None:
        self.ensure_can_manage_equipment(claims, equipment_id)

    def filter_areas(
        self, claims: AuthClaims, plant_id: int, areas: Sequence[Area]
    ) -> list[Area]:
        if claims.role in {"superadministrador", "invitado"}:
            return list(areas)

        allowed_area_ids = set(claims.areas)
        if claims.role == "administrador":
            return [area for area in areas if area.id in allowed_area_ids]

        if claims.role == "maquinista":
            allowed_equipment = {
                eq.id: eq for eq in self._equipment_from_ids(claims.equipos)
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
        try:
            self.ensure_can_manage_equipment(claims, equipment_id)
        except Forbidden:
            return []

        return list(systems)

    def _areas_from_ids(self, area_ids: Iterable[int]) -> list[Area | None]:
        return [self._get_area(area_id) for area_id in area_ids]

    def _equipment_from_ids(self, equipment_ids: Iterable[int]) -> list[Equipment | None]:
        return [self._get_equipment(eq_id) for eq_id in equipment_ids if eq_id is not None]
