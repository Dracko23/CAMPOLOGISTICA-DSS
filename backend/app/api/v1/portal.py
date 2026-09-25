from __future__ import annotations

import asyncio
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.v1.auth import require_role
from app.db.session import get_db
from app.models import Asignacion, Pedido, UbicacionVehiculo
from app.api.v1.auth import get_current_user
from app.schemas.operational import AsignacionRead, AsignacionUpdate, PedidoDetail
from app.services import OperationalService

router = APIRouter(tags=["portales"])


class PositionInput(BaseModel):
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    precision_m: float | None = Field(default=None, ge=0)


class DemoStep(BaseModel):
    progreso: int = Field(ge=0, le=100)


class TrackingRead(BaseModel):
    id_asignacion: int
    id_vehiculo: int
    latitud: float
    longitud: float
    destino_latitud: float
    destino_longitud: float
    progreso: int
    fuente: str
    fecha_hora: datetime


def _assignment_options():
    return (
        selectinload(Asignacion.pedido).selectinload(Pedido.ubicacion),
        selectinload(Asignacion.pedido).selectinload(Pedido.cliente),
        selectinload(Asignacion.conductor),
        selectinload(Asignacion.vehiculo),
    )


def _owned_assignment(session: Session, assignment_id: int, user) -> Asignacion:
    row = session.scalar(select(Asignacion).where(Asignacion.id_asignacion == assignment_id).options(*_assignment_options()))
    allowed = row and (user.rol == "admin" or (user.rol == "conductor" and row.id_conductor == user.id_conductor) or (user.rol == "cliente" and row.pedido.id_cliente == user.id_cliente))
    if not allowed:
        raise HTTPException(status_code=403, detail={"code": "acceso_denegado", "message": "No tienes permiso para acceder al seguimiento."})
    return row


def _tracking_read(row: Asignacion, position: UbicacionVehiculo) -> TrackingRead:
    destination = row.pedido.ubicacion
    start_lat, start_lng = float(destination.latitud) + .08, float(destination.longitud) - .08
    total = ((float(destination.latitud)-start_lat)**2 + (float(destination.longitud)-start_lng)**2) ** .5
    remaining = ((float(destination.latitud)-float(position.latitud))**2 + (float(destination.longitud)-float(position.longitud))**2) ** .5
    progress = max(0, min(100, round((1 - remaining / total) * 100))) if total else 100
    return TrackingRead(id_asignacion=row.id_asignacion, id_vehiculo=row.id_vehiculo, latitud=float(position.latitud), longitud=float(position.longitud), destino_latitud=float(destination.latitud), destino_longitud=float(destination.longitud), progreso=progress, fuente=position.fuente, fecha_hora=position.fecha_hora)


@router.get("/tracking/asignaciones/{assignment_id}", response_model=TrackingRead)
def tracking(assignment_id: int, user=Depends(get_current_user), session: Session = Depends(get_db)):
    row = _owned_assignment(session, assignment_id, user)
    position = session.scalar(select(UbicacionVehiculo).where(UbicacionVehiculo.id_asignacion == assignment_id).order_by(UbicacionVehiculo.fecha_hora.desc()))
    if not position:
        raise HTTPException(status_code=404, detail={"code": "ubicacion_no_disponible", "message": "Ubicación no disponible."})
    return _tracking_read(row, position)


@router.post("/driver/asignaciones/{assignment_id}/posicion", response_model=TrackingRead)
def publish_position(assignment_id: int, payload: PositionInput, user=Depends(require_role("conductor")), session: Session = Depends(get_db)):
    row = _owned_assignment(session, assignment_id, user)
    position = session.scalar(select(UbicacionVehiculo).where(UbicacionVehiculo.id_vehiculo == row.id_vehiculo).order_by(UbicacionVehiculo.fecha_hora.desc()))
    if not position:
        position = UbicacionVehiculo(id_vehiculo=row.id_vehiculo, id_conductor=row.id_conductor, id_asignacion=row.id_asignacion, fuente="gps")
        session.add(position)
    position.latitud, position.longitud, position.precision_m = payload.latitud, payload.longitud, payload.precision_m
    position.fecha_hora, position.fuente, position.id_asignacion = datetime.now(), "gps", row.id_asignacion
    session.commit()
    return _tracking_read(row, position)


@router.post("/admin/asignaciones/{assignment_id}/simulacion", response_model=TrackingRead)
def demo_position(assignment_id: int, payload: DemoStep, user=Depends(require_role("admin")), session: Session = Depends(get_db)):
    row = _owned_assignment(session, assignment_id, user)
    destination = row.pedido.ubicacion
    if destination.latitud is None or destination.longitud is None:
        raise HTTPException(status_code=409, detail={"code": "destino_sin_ubicacion", "message": "El destino no tiene ubicación confirmada."})
    fraction = payload.progreso / 100
    start_lat, start_lng = float(destination.latitud) + .08, float(destination.longitud) - .08
    lat = start_lat + (float(destination.latitud) - start_lat) * fraction
    lng = start_lng + (float(destination.longitud) - start_lng) * fraction
    position = session.scalar(select(UbicacionVehiculo).where(UbicacionVehiculo.id_vehiculo == row.id_vehiculo).order_by(UbicacionVehiculo.fecha_hora.desc()))
    if not position:
        position = UbicacionVehiculo(id_vehiculo=row.id_vehiculo, id_conductor=row.id_conductor, id_asignacion=row.id_asignacion, fuente="simulacion")
        session.add(position)
    position.latitud, position.longitud, position.fecha_hora = lat, lng, datetime.now()
    position.fuente, position.id_asignacion, position.id_conductor = "simulacion", row.id_asignacion, row.id_conductor
    session.commit()
    return _tracking_read(row, position)


@router.get("/tracking/asignaciones/{assignment_id}/stream")
async def tracking_stream(assignment_id: int, user=Depends(get_current_user), session: Session = Depends(get_db)):
    row = _owned_assignment(session, assignment_id, user)
    async def events():
        last = None
        for _ in range(120):
            session.expire_all()
            position = session.scalar(select(UbicacionVehiculo).where(UbicacionVehiculo.id_asignacion == assignment_id).order_by(UbicacionVehiculo.fecha_hora.desc()))
            if position and position.fecha_hora != last:
                last = position.fecha_hora
                yield f"data: {_tracking_read(row, position).model_dump_json()}\n\n"
            else:
                yield ": keep-alive\n\n"
            await asyncio.sleep(2)
    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/driver/asignaciones", response_model=list[AsignacionRead])
def driver_assignments(
    user=Depends(require_role("conductor")), session: Session = Depends(get_db)
):
    rows = session.scalars(
        select(Asignacion)
        .where(Asignacion.id_conductor == user.id_conductor)
        .options(*_assignment_options())
        .order_by(Asignacion.fecha_asignacion.desc())
    ).all()
    service = OperationalService(session)
    return [service._asignacion_read(row) for row in rows]


@router.get("/driver/asignaciones/{assignment_id}", response_model=AsignacionRead)
def driver_assignment(
    assignment_id: int,
    user=Depends(require_role("conductor")),
    session: Session = Depends(get_db),
):
    row = session.scalar(
        select(Asignacion)
        .where(Asignacion.id_asignacion == assignment_id, Asignacion.id_conductor == user.id_conductor)
        .options(*_assignment_options())
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "acceso_denegado", "message": "No tienes permiso para acceder a esta asignación."})
    return OperationalService(session)._asignacion_read(row)


@router.patch("/driver/asignaciones/{assignment_id}/estado", response_model=AsignacionRead)
def update_driver_assignment(
    assignment_id: int,
    payload: AsignacionUpdate,
    user=Depends(require_role("conductor")),
    session: Session = Depends(get_db),
):
    owned = session.scalar(select(Asignacion.id_asignacion).where(Asignacion.id_asignacion == assignment_id, Asignacion.id_conductor == user.id_conductor))
    if not owned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "acceso_denegado", "message": "No tienes permiso para modificar esta asignación."})
    return OperationalService(session).update_asignacion(assignment_id, payload)


@router.get("/client/pedidos", response_model=list[PedidoDetail])
def client_orders(user=Depends(require_role("cliente")), session: Session = Depends(get_db)):
    rows = session.scalars(
        select(Pedido)
        .where(Pedido.id_cliente == user.id_cliente)
        .options(
            selectinload(Pedido.cliente),
            selectinload(Pedido.ubicacion),
            selectinload(Pedido.asignaciones).selectinload(Asignacion.conductor),
            selectinload(Pedido.asignaciones).selectinload(Asignacion.vehiculo),
        )
        .order_by(Pedido.fecha_registro.desc())
    ).all()
    service = OperationalService(session)
    return [service._pedido_read(row, detail=True) for row in rows]


@router.get("/client/pedidos/{order_id}", response_model=PedidoDetail)
def client_order(
    order_id: int,
    user=Depends(require_role("cliente")),
    session: Session = Depends(get_db),
):
    row = session.scalar(
        select(Pedido)
        .where(Pedido.id_pedido == order_id, Pedido.id_cliente == user.id_cliente)
        .options(
            selectinload(Pedido.cliente),
            selectinload(Pedido.ubicacion),
            selectinload(Pedido.asignaciones).selectinload(Asignacion.conductor),
            selectinload(Pedido.asignaciones).selectinload(Asignacion.vehiculo),
        )
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "acceso_denegado", "message": "No tienes permiso para acceder a este pedido."})
    return OperationalService(session)._pedido_read(row, detail=True)
