import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import Unauthorized
from werkzeug.security import check_password_hash, generate_password_hash

from src.infrastructure.flask.auth import AuthService, AuthUser
from src.infrastructure.sqlalchemy import Base
from src.infrastructure.sqlalchemy.user_repository import SqlAlchemyUserRepository


def _make_repo() -> SqlAlchemyUserRepository:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, future=True
    )
    return SqlAlchemyUserRepository(session_factory)


def test_user_repository_persists_hashed_passwords() -> None:
    repo = _make_repo()

    repo.upsert_user(
        AuthUser(
            username="alice",
            password_hash=generate_password_hash("s3cret"),
            role="administrador",
            areas=[1],
            equipos=[],
        )
    )

    stored = repo.get_user("alice")

    assert stored is not None
    assert stored.username == "alice"
    assert stored.password_hash != "s3cret"
    assert check_password_hash(stored.password_hash, "s3cret")


def test_auth_service_respects_expiration_with_persisted_users() -> None:
    repo = _make_repo()
    repo.bootstrap_demo_users()

    auth_service = AuthService(
        secret_key="test-secret",
        token_ttl_seconds=1,
        user_store=repo,
    )

    token = auth_service.issue_token("admin", "admin")
    claims = auth_service.decode_token(token)
    assert claims.username == "admin"

    time.sleep(2)
    with pytest.raises(Unauthorized):
        auth_service.decode_token(token)


def test_decode_token_refreshes_scope_from_database() -> None:
    repo = _make_repo()
    repo.upsert_user(
        AuthUser(
            username="bob",
            password_hash=generate_password_hash("pw"),
            role="administrador",
            areas=[101],
            equipos=[],
        )
    )

    auth_service = AuthService(
        secret_key="test-secret",
        token_ttl_seconds=60,
        user_store=repo,
    )

    token = auth_service.issue_token("bob", "pw")

    # Cambiamos el alcance en base de datos para reflejar el estado real
    repo.upsert_user(
        AuthUser(
            username="bob",
            password_hash=generate_password_hash("pw"),
            role="administrador",
            areas=[],
            equipos=[2001],
        )
    )

    claims = auth_service.decode_token(token)

    assert claims.areas == []
    assert claims.equipos == [2001]

