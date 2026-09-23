"""Create the OLTP persistence schema.

Revision ID: 0001_create_oltp_schema
Revises:
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_oltp_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA oltp")

    op.create_table(
        "cliente",
        sa.Column("id_cliente", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("telefono", sa.String(length=30), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.PrimaryKeyConstraint("id_cliente", name="pk_cliente"),
        schema="oltp",
    )
    op.create_table(
        "ubicacion",
        sa.Column("id_ubicacion", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("direccion", sa.String(length=200), nullable=False),
        sa.Column("zona", sa.String(length=80), nullable=False),
        sa.Column("latitud", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitud", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.PrimaryKeyConstraint("id_ubicacion", name="pk_ubicacion"),
        schema="oltp",
    )
    op.create_table(
        "conductor",
        sa.Column("id_conductor", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("licencia", sa.String(length=40), nullable=True),
        sa.Column("disponible", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id_conductor", name="pk_conductor"),
        sa.UniqueConstraint("licencia", name="uq_conductor_licencia"),
        schema="oltp",
    )
    op.create_table(
        "vehiculo",
        sa.Column("id_vehiculo", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("placa", sa.String(length=20), nullable=True),
        sa.Column("capacidad_kg", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("rendimiento_km_l", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("disponible", sa.Boolean(), nullable=False),
        sa.CheckConstraint("capacidad_kg > 0", name="ck_vehiculo_capacidad_kg_positiva"),
        sa.CheckConstraint("rendimiento_km_l > 0", name="ck_vehiculo_rendimiento_km_l_positivo"),
        sa.PrimaryKeyConstraint("id_vehiculo", name="pk_vehiculo"),
        sa.UniqueConstraint("placa", name="uq_vehiculo_placa"),
        schema="oltp",
    )
    op.create_table(
        "pedido",
        sa.Column("id_pedido", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_cliente", sa.BigInteger(), nullable=True),
        sa.Column("id_ubicacion", sa.BigInteger(), nullable=True),
        sa.Column("codigo", sa.String(length=30), nullable=True),
        sa.Column("fecha_registro", sa.DateTime(), nullable=False),
        sa.Column("fecha_limite", sa.DateTime(), nullable=False),
        sa.Column("peso_kg", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("urgencia", sa.SmallInteger(), nullable=True),
        sa.Column("estado", sa.String(length=30), nullable=False),
        sa.CheckConstraint("peso_kg > 0", name="ck_pedido_peso_kg_positivo"),
        sa.CheckConstraint("urgencia BETWEEN 1 AND 5", name="ck_pedido_urgencia_rango"),
        sa.ForeignKeyConstraint(
            ["id_cliente"],
            ["oltp.cliente.id_cliente"],
            name="fk_pedido_id_cliente",
        ),
        sa.ForeignKeyConstraint(
            ["id_ubicacion"],
            ["oltp.ubicacion.id_ubicacion"],
            name="fk_pedido_id_ubicacion",
        ),
        sa.PrimaryKeyConstraint("id_pedido", name="pk_pedido"),
        sa.UniqueConstraint("codigo", name="uq_pedido_codigo"),
        schema="oltp",
    )
    op.create_table(
        "asignacion",
        sa.Column("id_asignacion", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_pedido", sa.BigInteger(), nullable=True),
        sa.Column("id_conductor", sa.BigInteger(), nullable=True),
        sa.Column("id_vehiculo", sa.BigInteger(), nullable=True),
        sa.Column("fecha_asignacion", sa.DateTime(), nullable=False),
        sa.Column("fecha_salida", sa.DateTime(), nullable=True),
        sa.Column("fecha_entrega", sa.DateTime(), nullable=True),
        sa.Column("distancia_km", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("combustible_litros", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("costo_combustible", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("estado", sa.String(length=30), nullable=False),
        sa.CheckConstraint("distancia_km >= 0", name="ck_asignacion_distancia_km_no_negativa"),
        sa.CheckConstraint(
            "combustible_litros >= 0",
            name="ck_asignacion_combustible_litros_no_negativo",
        ),
        sa.CheckConstraint(
            "costo_combustible >= 0",
            name="ck_asignacion_costo_combustible_no_negativo",
        ),
        sa.ForeignKeyConstraint(
            ["id_pedido"],
            ["oltp.pedido.id_pedido"],
            name="fk_asignacion_id_pedido",
        ),
        sa.ForeignKeyConstraint(
            ["id_conductor"],
            ["oltp.conductor.id_conductor"],
            name="fk_asignacion_id_conductor",
        ),
        sa.ForeignKeyConstraint(
            ["id_vehiculo"],
            ["oltp.vehiculo.id_vehiculo"],
            name="fk_asignacion_id_vehiculo",
        ),
        sa.PrimaryKeyConstraint("id_asignacion", name="pk_asignacion"),
        schema="oltp",
    )
    op.create_table(
        "evaluacion_dss",
        sa.Column("id_evaluacion", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_pedido", sa.BigInteger(), nullable=True),
        sa.Column("fecha_evaluacion", sa.DateTime(), nullable=False),
        sa.Column("indice_prioridad", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.CheckConstraint(
            "indice_prioridad BETWEEN 0 AND 100",
            name="ck_evaluacion_dss_indice_prioridad_rango",
        ),
        sa.ForeignKeyConstraint(
            ["id_pedido"],
            ["oltp.pedido.id_pedido"],
            name="fk_evaluacion_dss_id_pedido",
        ),
        sa.PrimaryKeyConstraint("id_evaluacion", name="pk_evaluacion_dss"),
        schema="oltp",
    )
    op.create_table(
        "alternativa",
        sa.Column("id_alternativa", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("id_evaluacion", sa.BigInteger(), nullable=True),
        sa.Column("id_conductor", sa.BigInteger(), nullable=True),
        sa.Column("id_vehiculo", sa.BigInteger(), nullable=True),
        sa.Column("distancia_estimada_km", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("combustible_estimado_l", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("riesgo_retraso", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("puntuacion", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("valida", sa.Boolean(), nullable=True),
        sa.Column("recomendada", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["id_evaluacion"],
            ["oltp.evaluacion_dss.id_evaluacion"],
            name="fk_alternativa_id_evaluacion",
        ),
        sa.ForeignKeyConstraint(
            ["id_conductor"],
            ["oltp.conductor.id_conductor"],
            name="fk_alternativa_id_conductor",
        ),
        sa.ForeignKeyConstraint(
            ["id_vehiculo"],
            ["oltp.vehiculo.id_vehiculo"],
            name="fk_alternativa_id_vehiculo",
        ),
        sa.PrimaryKeyConstraint("id_alternativa", name="pk_alternativa"),
        schema="oltp",
    )

    op.create_index("ix_pedido_id_cliente", "pedido", ["id_cliente"], schema="oltp")
    op.create_index("ix_pedido_id_ubicacion", "pedido", ["id_ubicacion"], schema="oltp")
    op.create_index("ix_asignacion_id_pedido", "asignacion", ["id_pedido"], schema="oltp")
    op.create_index("ix_asignacion_id_conductor", "asignacion", ["id_conductor"], schema="oltp")
    op.create_index("ix_asignacion_id_vehiculo", "asignacion", ["id_vehiculo"], schema="oltp")
    op.create_index("ix_evaluacion_dss_id_pedido", "evaluacion_dss", ["id_pedido"], schema="oltp")
    op.create_index("ix_alternativa_id_evaluacion", "alternativa", ["id_evaluacion"], schema="oltp")
    op.create_index("ix_alternativa_id_conductor", "alternativa", ["id_conductor"], schema="oltp")
    op.create_index("ix_alternativa_id_vehiculo", "alternativa", ["id_vehiculo"], schema="oltp")


def downgrade() -> None:
    op.drop_index("ix_alternativa_id_vehiculo", table_name="alternativa", schema="oltp")
    op.drop_index("ix_alternativa_id_conductor", table_name="alternativa", schema="oltp")
    op.drop_index("ix_alternativa_id_evaluacion", table_name="alternativa", schema="oltp")
    op.drop_index("ix_evaluacion_dss_id_pedido", table_name="evaluacion_dss", schema="oltp")
    op.drop_index("ix_asignacion_id_vehiculo", table_name="asignacion", schema="oltp")
    op.drop_index("ix_asignacion_id_conductor", table_name="asignacion", schema="oltp")
    op.drop_index("ix_asignacion_id_pedido", table_name="asignacion", schema="oltp")
    op.drop_index("ix_pedido_id_ubicacion", table_name="pedido", schema="oltp")
    op.drop_index("ix_pedido_id_cliente", table_name="pedido", schema="oltp")

    op.drop_table("alternativa", schema="oltp")
    op.drop_table("evaluacion_dss", schema="oltp")
    op.drop_table("asignacion", schema="oltp")
    op.drop_table("pedido", schema="oltp")
    op.drop_table("vehiculo", schema="oltp")
    op.drop_table("conductor", schema="oltp")
    op.drop_table("ubicacion", schema="oltp")
    op.drop_table("cliente", schema="oltp")

    op.execute("DROP SCHEMA oltp")
