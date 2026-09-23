from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Cliente(Base):
    __tablename__ = "cliente"
    __table_args__ = {"schema": "oltp"}

    id_cliente: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)

    pedidos: Mapped[list[Pedido]] = relationship(back_populates="cliente")


class Ubicacion(Base):
    __tablename__ = "ubicacion"
    __table_args__ = {"schema": "oltp"}

    id_ubicacion: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    direccion: Mapped[str] = mapped_column(String(200), nullable=False)
    zona: Mapped[str] = mapped_column(String(80), nullable=False)
    latitud: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitud: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)

    pedidos: Mapped[list[Pedido]] = relationship(back_populates="ubicacion")


class Pedido(Base):
    __tablename__ = "pedido"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_pedido_codigo"),
        CheckConstraint("peso_kg > 0", name="ck_pedido_peso_kg_positivo"),
        CheckConstraint("urgencia BETWEEN 1 AND 5", name="ck_pedido_urgencia_rango"),
        Index("ix_pedido_id_cliente", "id_cliente"),
        Index("ix_pedido_id_ubicacion", "id_ubicacion"),
        {"schema": "oltp"},
    )

    id_pedido: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    id_cliente: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("oltp.cliente.id_cliente", name="fk_pedido_id_cliente"),
        nullable=True,
    )
    id_ubicacion: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("oltp.ubicacion.id_ubicacion", name="fk_pedido_id_ubicacion"),
        nullable=True,
    )
    codigo: Mapped[str | None] = mapped_column(String(30), nullable=True)
    fecha_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    fecha_limite: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    peso_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    urgencia: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False)

    cliente: Mapped[Cliente | None] = relationship(back_populates="pedidos")
    ubicacion: Mapped[Ubicacion | None] = relationship(back_populates="pedidos")
    asignaciones: Mapped[list[Asignacion]] = relationship(back_populates="pedido")
    evaluaciones_dss: Mapped[list[EvaluacionDSS]] = relationship(
        back_populates="pedido"
    )


class Conductor(Base):
    __tablename__ = "conductor"
    __table_args__ = (
        UniqueConstraint("licencia", name="uq_conductor_licencia"),
        {"schema": "oltp"},
    )

    id_conductor: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    licencia: Mapped[str | None] = mapped_column(String(40), nullable=True)
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False)

    asignaciones: Mapped[list[Asignacion]] = relationship(back_populates="conductor")
    alternativas: Mapped[list[Alternativa]] = relationship(back_populates="conductor")


class Vehiculo(Base):
    __tablename__ = "vehiculo"
    __table_args__ = (
        UniqueConstraint("placa", name="uq_vehiculo_placa"),
        CheckConstraint(
            "capacidad_kg > 0", name="ck_vehiculo_capacidad_kg_positiva"
        ),
        CheckConstraint(
            "rendimiento_km_l > 0",
            name="ck_vehiculo_rendimiento_km_l_positivo",
        ),
        {"schema": "oltp"},
    )

    id_vehiculo: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    placa: Mapped[str | None] = mapped_column(String(20), nullable=True)
    capacidad_kg: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    rendimiento_km_l: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    disponible: Mapped[bool] = mapped_column(Boolean, nullable=False)

    asignaciones: Mapped[list[Asignacion]] = relationship(back_populates="vehiculo")
    alternativas: Mapped[list[Alternativa]] = relationship(back_populates="vehiculo")


class Asignacion(Base):
    __tablename__ = "asignacion"
    __table_args__ = (
        CheckConstraint(
            "distancia_km >= 0", name="ck_asignacion_distancia_km_no_negativa"
        ),
        CheckConstraint(
            "combustible_litros >= 0",
            name="ck_asignacion_combustible_litros_no_negativo",
        ),
        CheckConstraint(
            "costo_combustible >= 0",
            name="ck_asignacion_costo_combustible_no_negativo",
        ),
        Index("ix_asignacion_id_pedido", "id_pedido"),
        Index("ix_asignacion_id_conductor", "id_conductor"),
        Index("ix_asignacion_id_vehiculo", "id_vehiculo"),
        {"schema": "oltp"},
    )

    id_asignacion: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    id_pedido: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("oltp.pedido.id_pedido", name="fk_asignacion_id_pedido"),
        nullable=True,
    )
    id_conductor: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "oltp.conductor.id_conductor", name="fk_asignacion_id_conductor"
        ),
        nullable=True,
    )
    id_vehiculo: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("oltp.vehiculo.id_vehiculo", name="fk_asignacion_id_vehiculo"),
        nullable=True,
    )
    fecha_asignacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    fecha_salida: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    fecha_entrega: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    distancia_km: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    combustible_litros: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    costo_combustible: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    estado: Mapped[str] = mapped_column(String(30), nullable=False)

    pedido: Mapped[Pedido | None] = relationship(back_populates="asignaciones")
    conductor: Mapped[Conductor | None] = relationship(back_populates="asignaciones")
    vehiculo: Mapped[Vehiculo | None] = relationship(back_populates="asignaciones")


class EvaluacionDSS(Base):
    __tablename__ = "evaluacion_dss"
    __table_args__ = (
        CheckConstraint(
            "indice_prioridad BETWEEN 0 AND 100",
            name="ck_evaluacion_dss_indice_prioridad_rango",
        ),
        Index("ix_evaluacion_dss_id_pedido", "id_pedido"),
        {"schema": "oltp"},
    )

    id_evaluacion: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    id_pedido: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("oltp.pedido.id_pedido", name="fk_evaluacion_dss_id_pedido"),
        nullable=True,
    )
    fecha_evaluacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    indice_prioridad: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )

    pedido: Mapped[Pedido | None] = relationship(back_populates="evaluaciones_dss")
    alternativas: Mapped[list[Alternativa]] = relationship(
        back_populates="evaluacion"
    )


class Alternativa(Base):
    __tablename__ = "alternativa"
    __table_args__ = (
        Index("ix_alternativa_id_evaluacion", "id_evaluacion"),
        Index("ix_alternativa_id_conductor", "id_conductor"),
        Index("ix_alternativa_id_vehiculo", "id_vehiculo"),
        {"schema": "oltp"},
    )

    id_alternativa: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, nullable=False
    )
    id_evaluacion: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "oltp.evaluacion_dss.id_evaluacion",
            name="fk_alternativa_id_evaluacion",
        ),
        nullable=True,
    )
    id_conductor: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "oltp.conductor.id_conductor", name="fk_alternativa_id_conductor"
        ),
        nullable=True,
    )
    id_vehiculo: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("oltp.vehiculo.id_vehiculo", name="fk_alternativa_id_vehiculo"),
        nullable=True,
    )
    distancia_estimada_km: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    combustible_estimado_l: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    riesgo_retraso: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    puntuacion: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    valida: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    recomendada: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    evaluacion: Mapped[EvaluacionDSS | None] = relationship(
        back_populates="alternativas"
    )
    conductor: Mapped[Conductor | None] = relationship(back_populates="alternativas")
    vehiculo: Mapped[Vehiculo | None] = relationship(back_populates="alternativas")
