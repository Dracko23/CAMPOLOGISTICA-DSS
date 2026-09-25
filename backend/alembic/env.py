from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app import models  # noqa: F401 - register all ORM mappings on Base.metadata
from app.core.config import get_settings
from app.db.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

EXPECTED_TABLE_KEYS = frozenset(
    {
        "oltp.cliente",
        "oltp.ubicacion",
        "oltp.pedido",
        "oltp.conductor",
        "oltp.vehiculo",
        "oltp.asignacion",
        "oltp.evaluacion_dss",
        "oltp.alternativa",
        "oltp.usuario",
        "oltp.ubicacion_vehiculo",
        "oltp.evidencia_entrega",
    }
)


def validate_target_metadata() -> None:
    actual_table_keys = frozenset(target_metadata.tables)
    if actual_table_keys != EXPECTED_TABLE_KEYS:
        missing = sorted(EXPECTED_TABLE_KEYS - actual_table_keys)
        unexpected = sorted(actual_table_keys - EXPECTED_TABLE_KEYS)
        raise RuntimeError(
            "Alembic target metadata must match the migrated OLTP tables; "
            f"missing={missing}, unexpected={unexpected}"
        )


def run_migrations_offline() -> None:
    validate_target_metadata()
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    validate_target_metadata()
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_offline() if context.is_offline_mode() else run_migrations_online()
