"""Add assignment acceptance and arrival timestamps.

Revision ID: 0003_assignment_timeline
Revises: 0002_add_auth_tracking_evidence
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_assignment_timeline"
down_revision = "0002_add_auth_tracking_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("asignacion", sa.Column("fecha_aceptacion", sa.DateTime(), nullable=True), schema="oltp")
    op.add_column("asignacion", sa.Column("fecha_llegada", sa.DateTime(), nullable=True), schema="oltp")


def downgrade() -> None:
    op.drop_column("asignacion", "fecha_llegada", schema="oltp")
    op.drop_column("asignacion", "fecha_aceptacion", schema="oltp")
