from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
import uvicorn
from alembic import command
from alembic.config import Config
from psycopg import sql
from sqlalchemy.engine import URL, make_url

from app.core.config import get_settings


BACKEND_DIR = Path(__file__).resolve().parents[1]
E2E_DATABASE_NAME = 'campo_logistica_e2e'
DEFAULT_ADMIN_URL = (
    'postgresql+psycopg://campo_logistica:'
    'change_me_for_local_development@127.0.0.1:55432/postgres'
)


def _admin_url() -> URL:
    raw_url = (
        os.environ.get('E2E_DATABASE_ADMIN_URL')
        or os.environ.get('TEST_DATABASE_ADMIN_URL')
        or DEFAULT_ADMIN_URL
    )
    url = make_url(raw_url)
    if url.drivername != 'postgresql+psycopg':
        raise RuntimeError('E2E requiere postgresql+psycopg.')
    if url.host != '127.0.0.1' or url.port != 55432:
        raise RuntimeError('E2E solo admite PostgreSQL Docker en 127.0.0.1:55432.')
    if url.database != 'postgres':
        raise RuntimeError('La URL administrativa E2E debe apuntar a postgres.')
    if not url.username or url.password is None:
        raise RuntimeError('La URL administrativa E2E requiere credenciales.')
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


def drop_database() -> None:
    admin_url = _admin_url()
    with _connect_admin(admin_url) as connection:
        exists = connection.execute(
            'SELECT 1 FROM pg_database WHERE datname = %s',
            (E2E_DATABASE_NAME,),
        ).fetchone()
        if not exists:
            return
        connection.execute(
            '''
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
            ''',
            (E2E_DATABASE_NAME,),
        )
        connection.execute(
            sql.SQL('DROP DATABASE {}').format(
                sql.Identifier(E2E_DATABASE_NAME),
            )
        )


def reset_database() -> str:
    drop_database()
    admin_url = _admin_url()
    with _connect_admin(admin_url) as connection:
        connection.execute(
            sql.SQL('CREATE DATABASE {}').format(
                sql.Identifier(E2E_DATABASE_NAME),
            )
        )

    database_url = admin_url.set(database=E2E_DATABASE_NAME).render_as_string(
        hide_password=False
    )
    os.environ['DATABASE_URL'] = database_url
    get_settings.cache_clear()
    alembic_config = Config(str(BACKEND_DIR / 'alembic.ini'))
    alembic_config.set_main_option(
        'script_location',
        str(BACKEND_DIR / 'alembic'),
    )
    command.upgrade(alembic_config, 'head')
    return database_url


def serve() -> None:
    reset_database()
    try:
        uvicorn.run(
            'app.main:app',
            host='127.0.0.1',
            port=8000,
            log_level='warning',
        )
    finally:
        drop_database()


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else 'serve'
    if action == 'serve':
        serve()
    elif action == 'drop':
        drop_database()
    else:
        raise SystemExit(f'Accion E2E desconocida: {action}')
