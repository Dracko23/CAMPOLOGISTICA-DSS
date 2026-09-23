from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    Alternativa,
    Asignacion,
    Cliente,
    Conductor,
    EvaluacionDSS,
    Pedido,
    Ubicacion,
    Vehiculo,
)


BASE_TIME = datetime(2026, 1, 15, 8, 30)


def persist_cliente(session: Session, suffix: str = "base") -> Cliente:
    entity = Cliente(
        nombre=f"Cliente {suffix}",
        telefono="72900000",
        email=f"{suffix}@example.test",
    )
    session.add(entity)
    session.flush()
    return entity


def persist_ubicacion(session: Session, suffix: str = "base") -> Ubicacion:
    entity = Ubicacion(
        direccion=f"Av. Las Américas {suffix}",
        zona="Tarija Centro",
        latitud=Decimal("-21.535500"),
        longitud=Decimal("-64.729600"),
    )
    session.add(entity)
    session.flush()
    return entity


def persist_pedido(
    session: Session,
    suffix: str = "base",
    *,
    cliente: Cliente | None = None,
    ubicacion: Ubicacion | None = None,
    peso_kg: Decimal = Decimal("25.50"),
    urgencia: int = 3,
) -> Pedido:
    cliente = cliente or persist_cliente(session, suffix)
    ubicacion = ubicacion or persist_ubicacion(session, suffix)
    entity = Pedido(
        id_cliente=cliente.id_cliente,
        id_ubicacion=ubicacion.id_ubicacion,
        codigo=f"PED-{suffix}",
        fecha_registro=BASE_TIME,
        fecha_limite=BASE_TIME + timedelta(hours=8),
        peso_kg=peso_kg,
        urgencia=urgencia,
        estado="registrado",
    )
    session.add(entity)
    session.flush()
    return entity


def persist_conductor(session: Session, suffix: str = "base") -> Conductor:
    entity = Conductor(
        nombre=f"Conductor {suffix}",
        licencia=f"LIC-{suffix}",
        disponible=True,
    )
    session.add(entity)
    session.flush()
    return entity


def persist_vehiculo(session: Session, suffix: str = "base") -> Vehiculo:
    entity = Vehiculo(
        placa=f"TJA-{suffix}",
        capacidad_kg=Decimal("1200.00"),
        rendimiento_km_l=Decimal("10.50"),
        disponible=True,
    )
    session.add(entity)
    session.flush()
    return entity


def persist_asignacion(
    session: Session,
    suffix: str = "base",
    *,
    pedido: Pedido | None = None,
    conductor: Conductor | None = None,
    vehiculo: Vehiculo | None = None,
) -> Asignacion:
    pedido = pedido or persist_pedido(session, suffix)
    conductor = conductor or persist_conductor(session, suffix)
    vehiculo = vehiculo or persist_vehiculo(session, suffix)
    entity = Asignacion(
        id_pedido=pedido.id_pedido,
        id_conductor=conductor.id_conductor,
        id_vehiculo=vehiculo.id_vehiculo,
        fecha_asignacion=BASE_TIME,
        distancia_km=Decimal("12.75"),
        combustible_litros=Decimal("1.30"),
        costo_combustible=Decimal("5.20"),
        estado="asignada",
    )
    session.add(entity)
    session.flush()
    return entity


def persist_evaluacion(
    session: Session,
    suffix: str = "base",
    *,
    pedido: Pedido | None = None,
) -> EvaluacionDSS:
    pedido = pedido or persist_pedido(session, suffix)
    entity = EvaluacionDSS(
        id_pedido=pedido.id_pedido,
        fecha_evaluacion=BASE_TIME,
        indice_prioridad=Decimal("72.50"),
    )
    session.add(entity)
    session.flush()
    return entity


def persist_alternativa(
    session: Session,
    suffix: str = "base",
    *,
    evaluacion: EvaluacionDSS | None = None,
    conductor: Conductor | None = None,
    vehiculo: Vehiculo | None = None,
) -> Alternativa:
    evaluacion = evaluacion or persist_evaluacion(session, suffix)
    conductor = conductor or persist_conductor(session, suffix)
    vehiculo = vehiculo or persist_vehiculo(session, suffix)
    entity = Alternativa(
        id_evaluacion=evaluacion.id_evaluacion,
        id_conductor=conductor.id_conductor,
        id_vehiculo=vehiculo.id_vehiculo,
        distancia_estimada_km=Decimal("11.80"),
        combustible_estimado_l=Decimal("1.15"),
        riesgo_retraso=Decimal("18.00"),
        puntuacion=Decimal("81.25"),
        valida=True,
        recomendada=True,
    )
    session.add(entity)
    session.flush()
    return entity
