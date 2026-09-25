"""Add auth, tracking and evidence tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-24

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '0002_add_auth_tracking_evidence'
down_revision: Union[str, None] = '0001_create_oltp_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. Extend oltp.ubicacion with ciudad / departamento (nullable)      #
    # ------------------------------------------------------------------ #
    op.add_column(
        'ubicacion',
        sa.Column('ciudad', sa.String(100), nullable=True),
        schema='oltp',
    )
    op.add_column(
        'ubicacion',
        sa.Column('departamento', sa.String(100), nullable=True),
        schema='oltp',
    )

    # ------------------------------------------------------------------ #
    # 2. oltp.usuario — authentication & RBAC                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        'usuario',
        sa.Column(
            'id_usuario',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column('email', sa.String(150), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        # rol: 'admin' | 'conductor' | 'cliente'
        sa.Column('rol', sa.String(30), nullable=False),
        sa.Column('nombre', sa.String(120), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        # optional links to domain entities
        sa.Column(
            'id_conductor',
            sa.BigInteger(),
            sa.ForeignKey(
                'oltp.conductor.id_conductor',
                name='fk_usuario_id_conductor',
                ondelete='SET NULL',
            ),
            nullable=True,
        ),
        sa.Column(
            'id_cliente',
            sa.BigInteger(),
            sa.ForeignKey(
                'oltp.cliente.id_cliente',
                name='fk_usuario_id_cliente',
                ondelete='SET NULL',
            ),
            nullable=True,
        ),
        sa.Column(
            'fecha_creacion',
            sa.DateTime(timezone=False),
            nullable=False,
        ),
        sa.UniqueConstraint('email', name='uq_usuario_email'),
        sa.CheckConstraint(
            "rol IN ('admin', 'conductor', 'cliente')",
            name='ck_usuario_rol_valido',
        ),
        schema='oltp',
    )
    op.create_index('ix_usuario_email', 'usuario', ['email'], schema='oltp')
    op.create_index('ix_usuario_id_conductor', 'usuario', ['id_conductor'], schema='oltp')
    op.create_index('ix_usuario_id_cliente', 'usuario', ['id_cliente'], schema='oltp')

    # ------------------------------------------------------------------ #
    # 3. oltp.ubicacion_vehiculo — GPS / demo tracking                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        'ubicacion_vehiculo',
        sa.Column(
            'id_ubicacion_vehiculo',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            'id_vehiculo',
            sa.BigInteger(),
            sa.ForeignKey(
                'oltp.vehiculo.id_vehiculo',
                name='fk_ubicacion_vehiculo_id_vehiculo',
            ),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            'id_conductor',
            sa.BigInteger(),
            sa.ForeignKey(
                'oltp.conductor.id_conductor',
                name='fk_ubicacion_vehiculo_id_conductor',
            ),
            nullable=True,
        ),
        sa.Column(
            'id_asignacion',
            sa.BigInteger(),
            sa.ForeignKey(
                'oltp.asignacion.id_asignacion',
                name='fk_ubicacion_vehiculo_id_asignacion',
            ),
            nullable=True,
        ),
        sa.Column('latitud', sa.Numeric(9, 6), nullable=False),
        sa.Column('longitud', sa.Numeric(9, 6), nullable=False),
        sa.Column('precision_m', sa.Numeric(6, 1), nullable=True),
        sa.Column('velocidad_kmh', sa.Numeric(5, 1), nullable=True),
        sa.Column('rumbo', sa.Numeric(5, 1), nullable=True),
        sa.Column('fecha_hora', sa.DateTime(timezone=False), nullable=False),
        # fuente: 'gps' | 'simulacion' | 'manual'
        sa.Column('fuente', sa.String(20), nullable=False, server_default='simulacion'),
        sa.CheckConstraint(
            "fuente IN ('gps', 'simulacion', 'manual')",
            name='ck_ubicacion_vehiculo_fuente_valida',
        ),
        schema='oltp',
    )
    op.create_index(
        'ix_ubicacion_vehiculo_id_asignacion',
        'ubicacion_vehiculo',
        ['id_asignacion'],
        schema='oltp',
    )
    op.create_index(
        'ix_ubicacion_vehiculo_id_vehiculo_fecha',
        'ubicacion_vehiculo',
        ['id_vehiculo', 'fecha_hora'],
        schema='oltp',
    )

    # ------------------------------------------------------------------ #
    # 4. oltp.evidencia_entrega — delivery evidence                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        'evidencia_entrega',
        sa.Column(
            'id_evidencia',
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            'id_asignacion',
            sa.BigInteger(),
            sa.ForeignKey(
                'oltp.asignacion.id_asignacion',
                name='fk_evidencia_entrega_id_asignacion',
            ),
            nullable=False,
        ),
        sa.Column('fecha_registro', sa.DateTime(timezone=False), nullable=False),
        sa.Column('observacion', sa.Text(), nullable=True),
        sa.Column(
            'confirmado_conductor',
            sa.Boolean(),
            nullable=False,
            server_default='false',
        ),
        sa.Column('confirmado_cliente', sa.Boolean(), nullable=True),
        schema='oltp',
    )
    op.create_index(
        'ix_evidencia_entrega_id_asignacion',
        'evidencia_entrega',
        ['id_asignacion'],
        schema='oltp',
    )


def downgrade() -> None:
    # reverse order
    op.drop_table('evidencia_entrega', schema='oltp')
    op.drop_table('ubicacion_vehiculo', schema='oltp')
    op.drop_index('ix_usuario_id_cliente', table_name='usuario', schema='oltp')
    op.drop_index('ix_usuario_id_conductor', table_name='usuario', schema='oltp')
    op.drop_index('ix_usuario_email', table_name='usuario', schema='oltp')
    op.drop_table('usuario', schema='oltp')
    op.drop_column('ubicacion', 'departamento', schema='oltp')
    op.drop_column('ubicacion', 'ciudad', schema='oltp')
