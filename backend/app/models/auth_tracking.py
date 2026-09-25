from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Usuario(Base):
    """Authentication + RBAC user record."""

    __tablename__ = "usuario"
    __table_args__ = (
        UniqueConstraint("email", name="uq_usuario_email"),
        CheckConstraint(
            "rol IN ('admin', 'conductor', 'cliente')",
            name="ck_usuario_rol_valido",
        ),
        Index("ix_usuario_email", "email"),
        Index("ix_usuario_id_conductor", "id_conductor"),
        Index("ix_usuario_id_cliente", "id_cliente"),
        {"schema": "oltp"},
    )

    id_usuario: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    id_conductor: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("oltp.conductor.id_conductor", name="fk_usuario_id_conductor", ondelete="SET NULL"),
        nullable=True,
    )
    id_cliente: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("oltp.cliente.id_cliente", name="fk_usuario_id_cliente", ondelete="SET NULL"),
        nullable=True,
    )
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )


class UbicacionVehiculo(Base):
    """GPS / demo tracking record for a vehicle during an assignment."""

    __tablename__ = "ubicacion_vehiculo"
    __table_args__ = (
        CheckConstraint(
            "fuente IN ('gps', 'simulacion', 'manual')",
            name="ck_ubicacion_vehiculo_fuente_valida",
        ),
        Index("ix_ubicacion_vehiculo_id_asignacion", "id_asignacion"),
        Index(
            "ix_ubicacion_vehiculo_id_vehiculo_fecha",
            "id_vehiculo",
            "fecha_hora",
        ),
        {"schema": "oltp"},
    )

    id_ubicacion_vehiculo: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    id_vehiculo: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "oltp.vehiculo.id_vehiculo",
            name="fk_ubicacion_vehiculo_id_vehiculo",
        ),
        nullable=False,
    )
    id_conductor: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "oltp.conductor.id_conductor",
            name="fk_ubicacion_vehiculo_id_conductor",
        ),
        nullable=True,
    )
    id_asignacion: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "oltp.asignacion.id_asignacion",
            name="fk_ubicacion_vehiculo_id_asignacion",
        ),
        nullable=True,
    )
    latitud: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitud: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    precision_m: Mapped[float | None] = mapped_column(Numeric(6, 1), nullable=True)
    velocidad_kmh: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    rumbo: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    fecha_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    fuente: Mapped[str] = mapped_column(String(20), nullable=False, default="simulacion")


class EvidenciaEntrega(Base):
    """Delivery evidence registered by the driver upon completion."""

    __tablename__ = "evidencia_entrega"
    __table_args__ = (
        UniqueConstraint("id_asignacion", name="uq_evidencia_entrega_id_asignacion"),
        Index("ix_evidencia_entrega_id_asignacion", "id_asignacion"),
        {"schema": "oltp"},
    )

    id_evidencia: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    id_asignacion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "oltp.asignacion.id_asignacion",
            name="fk_evidencia_entrega_id_asignacion",
        ),
        nullable=False,
    )
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    observacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmado_conductor: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    confirmado_cliente: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
