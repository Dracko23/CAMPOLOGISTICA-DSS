from __future__ import annotations

import asyncio
import os
import re
from types import SimpleNamespace
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import httpx
import psycopg
import pytest
from alembic import command
from alembic.config import Config
from psycopg import sql
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


BACKEND_DIR = Path(__file__).resolve().parents[1]
SAFE_DATABASE_NAME = re.compile(r"^campo_logistica_test_[0-9a-f]{32}$")


class ApiClient:
    def __init__(self, app: object) -> None:
        self.app = app

    def request(self, method: str, url: str, **kwargs: object) -> httpx.Response:
        async def send() -> httpx.Response:
            transport = httpx.ASGITransport(app=self.app)  # type: ignore[arg-type]
            async with httpx.AsyncClient(
                transport=transport, base_url='http://testserver'
            ) as client:
                return await client.request(method, url, **kwargs)

        return asyncio.run(send())

    def get(self, url: str, **kwargs: object) -> httpx.Response:
        return self.request('GET', url, **kwargs)

    def post(self, url: str, **kwargs: object) -> httpx.Response:
        return self.request('POST', url, **kwargs)

    def patch(self, url: str, **kwargs: object) -> httpx.Response:
        return self.request('PATCH', url, **kwargs)

    def delete(self, url: str, **kwargs: object) -> httpx.Response:
        return self.request('DELETE', url, **kwargs)


def _validated_admin_url() -> URL:
    raw_url = os.environ.get("TEST_DATABASE_ADMIN_URL")
    if not raw_url:
        pytest.fail(
            "TEST_DATABASE_ADMIN_URL es obligatorio; las pruebas no usan SQLite.",
            pytrace=False,
        )

    url = make_url(raw_url)
    if url.drivername != "postgresql+psycopg":
        pytest.fail("Las pruebas requieren postgresql+psycopg.", pytrace=False)
    if url.host != "127.0.0.1":
        pytest.fail("La base de pruebas debe usar 127.0.0.1.", pytrace=False)
    if url.port != 55432:
        pytest.fail("La base de pruebas debe usar el puerto Docker 55432.", pytrace=False)
    if url.database != "postgres":
        pytest.fail("TEST_DATABASE_ADMIN_URL debe apuntar a la base postgres.", pytrace=False)
    if not url.username or url.password is None:
        pytest.fail("La URL administrativa debe incluir credenciales.", pytrace=False)
    return url


def _connect_admin(url: URL) -> psycopg.Connection:
    return psycopg.connect(
        host=url.host,
        port=url.port,
        dbname=url.database,
        user=url.username,
        password=url.password,
        autocommit=True,
    )


@pytest.fixture(scope="session")
def postgres_test_url() -> Iterator[str]:
    admin_url = _validated_admin_url()
    database_name = f"campo_logistica_test_{uuid4().hex}"
    assert SAFE_DATABASE_NAME.fullmatch(database_name)

    with _connect_admin(admin_url) as connection:
        connection.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
        )

    test_url = admin_url.set(database=database_name)
    try:
        yield test_url.render_as_string(hide_password=False)
    finally:
        if not SAFE_DATABASE_NAME.fullmatch(database_name):
            raise RuntimeError("Se rechazó eliminar una base con nombre no seguro.")
        with _connect_admin(admin_url) as connection:
            connection.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
                """,
                (database_name,),
            )
            connection.execute(
                sql.SQL("DROP DATABASE {}").format(sql.Identifier(database_name))
            )


@pytest.fixture(scope="session")
def migrated_database(postgres_test_url: str) -> Iterator[None]:
    previous_database_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = postgres_test_url
    get_settings.cache_clear()

    alembic_config = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    try:
        command.upgrade(alembic_config, "head")
        yield
    finally:
        get_settings.cache_clear()
        if previous_database_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_database_url


@pytest.fixture(scope="session")
def pg_engine(postgres_test_url: str, migrated_database: None) -> Iterator[Engine]:
    engine = create_engine(postgres_test_url, poolclass=NullPool)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session(pg_engine: Engine) -> Iterator[Session]:
    connection = pg_engine.connect()
    outer_transaction = connection.begin()
    session = Session(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        session.close()
        if outer_transaction.is_active:
            outer_transaction.rollback()
        connection.close()


@pytest.fixture
def api_client(db_session: Session) -> Iterator[ApiClient]:
    from app.db.session import get_db
    from app.api.v1.auth import get_current_user
    from app.main import app

    def override_database() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_database
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id_usuario=1, rol="admin", activo=True, id_conductor=None, id_cliente=None
    )
    try:
        yield ApiClient(app)
    finally:
        app.dependency_overrides.clear()
