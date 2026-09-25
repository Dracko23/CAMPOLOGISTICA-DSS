from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.v1 import auth as auth_router
from app.api.v1 import portal as portal_router
from app.db.session import get_db
from app.schemas.operational import (
    AsignacionCreate,
    AsignacionRead,
    AsignacionUpdate,
    ConductorCreate,
    ClienteRead,
    ConductorRead,
    ConductorUpdate,
    Page,
    PedidoCreate,
    PedidoDetail,
    PedidoEstado,
    PedidoRead,
    PedidoUpdate,
    ResumenOperacional,
    SortOrder,
    VehiculoCreate,
    VehiculoRead,
    VehiculoUpdate,
)
from app.services import OperationalService


router = APIRouter(prefix='/api/v1')
router.include_router(auth_router.router)
router.include_router(portal_router.router)


def service(
    session: Session = Depends(get_db),
    _user=Depends(auth_router.require_role('admin')),
) -> OperationalService:
    return OperationalService(session)


@router.get('/clientes', response_model=list[ClienteRead])
def list_clientes(
    q: str | None = Query(default=None, min_length=1, max_length=120),
    operations: OperationalService = Depends(service),
) -> list[ClienteRead]:
    return operations.list_clientes(q)


@router.post(
    '/pedidos',
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
)
def create_pedido(
    payload: PedidoCreate,
    operations: OperationalService = Depends(service),
) -> PedidoRead:
    return operations.create_pedido(payload)


@router.get('/pedidos', response_model=Page[PedidoRead])
def list_pedidos(
    q: str | None = Query(default=None, min_length=1, max_length=120),
    estado: PedidoEstado | None = None,
    urgencia: int | None = Query(default=None, ge=1, le=5),
    zona: str | None = Query(default=None, min_length=1, max_length=80),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        'id_pedido',
        'codigo',
        'fecha_registro',
        'fecha_limite',
        'peso_kg',
        'urgencia',
        'estado',
    ] = 'fecha_registro',
    sort_order: SortOrder = 'desc',
    operations: OperationalService = Depends(service),
) -> Page[PedidoRead]:
    return operations.list_pedidos(
        q=q,
        estado=estado,
        urgencia=urgencia,
        zona=zona,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get('/pedidos/{pedido_id}', response_model=PedidoDetail)
def get_pedido(
    pedido_id: int,
    operations: OperationalService = Depends(service),
) -> PedidoDetail:
    return operations.get_pedido(pedido_id)


@router.patch('/pedidos/{pedido_id}', response_model=PedidoRead)
def update_pedido(
    pedido_id: int,
    payload: PedidoUpdate,
    operations: OperationalService = Depends(service),
) -> PedidoRead:
    return operations.update_pedido(pedido_id, payload)


@router.delete(
    '/pedidos/{pedido_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_pedido(
    pedido_id: int,
    operations: OperationalService = Depends(service),
) -> Response:
    operations.delete_pedido(pedido_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    '/conductores',
    response_model=ConductorRead,
    status_code=status.HTTP_201_CREATED,
)
def create_conductor(
    payload: ConductorCreate,
    operations: OperationalService = Depends(service),
) -> ConductorRead:
    return operations.create_conductor(payload)


@router.get('/conductores', response_model=Page[ConductorRead])
def list_conductores(
    q: str | None = Query(default=None, min_length=1, max_length=120),
    disponible: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        'id_conductor', 'nombre', 'licencia', 'disponible'
    ] = 'nombre',
    sort_order: SortOrder = 'asc',
    operations: OperationalService = Depends(service),
) -> Page[ConductorRead]:
    return operations.list_conductores(
        q=q,
        disponible=disponible,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get('/conductores/{conductor_id}', response_model=ConductorRead)
def get_conductor(
    conductor_id: int,
    operations: OperationalService = Depends(service),
) -> ConductorRead:
    return operations.get_conductor(conductor_id)


@router.patch('/conductores/{conductor_id}', response_model=ConductorRead)
def update_conductor(
    conductor_id: int,
    payload: ConductorUpdate,
    operations: OperationalService = Depends(service),
) -> ConductorRead:
    return operations.update_conductor(conductor_id, payload)


@router.delete(
    '/conductores/{conductor_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_conductor(
    conductor_id: int,
    operations: OperationalService = Depends(service),
) -> Response:
    operations.delete_conductor(conductor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    '/vehiculos',
    response_model=VehiculoRead,
    status_code=status.HTTP_201_CREATED,
)
def create_vehiculo(
    payload: VehiculoCreate,
    operations: OperationalService = Depends(service),
) -> VehiculoRead:
    return operations.create_vehiculo(payload)


@router.get('/vehiculos', response_model=Page[VehiculoRead])
def list_vehiculos(
    q: str | None = Query(default=None, min_length=1, max_length=120),
    disponible: bool | None = None,
    capacidad_min: float | None = Query(default=None, gt=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        'id_vehiculo',
        'placa',
        'capacidad_kg',
        'rendimiento_km_l',
        'disponible',
    ] = 'placa',
    sort_order: SortOrder = 'asc',
    operations: OperationalService = Depends(service),
) -> Page[VehiculoRead]:
    return operations.list_vehiculos(
        q=q,
        disponible=disponible,
        capacidad_min=capacidad_min,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get('/vehiculos/{vehiculo_id}', response_model=VehiculoRead)
def get_vehiculo(
    vehiculo_id: int,
    operations: OperationalService = Depends(service),
) -> VehiculoRead:
    return operations.get_vehiculo(vehiculo_id)


@router.patch('/vehiculos/{vehiculo_id}', response_model=VehiculoRead)
def update_vehiculo(
    vehiculo_id: int,
    payload: VehiculoUpdate,
    operations: OperationalService = Depends(service),
) -> VehiculoRead:
    return operations.update_vehiculo(vehiculo_id, payload)


@router.delete(
    '/vehiculos/{vehiculo_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_vehiculo(
    vehiculo_id: int,
    operations: OperationalService = Depends(service),
) -> Response:
    operations.delete_vehiculo(vehiculo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    '/asignaciones',
    response_model=AsignacionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_asignacion(
    payload: AsignacionCreate,
    operations: OperationalService = Depends(service),
) -> AsignacionRead:
    return operations.create_asignacion(payload)


@router.get('/asignaciones', response_model=Page[AsignacionRead])
def list_asignaciones(
    q: str | None = Query(default=None, min_length=1, max_length=120),
    estado: Literal['asignada', 'aceptada', 'en_camino', 'llegue', 'entregada', 'cancelada'] | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: Literal[
        'id_asignacion',
        'fecha_asignacion',
        'fecha_salida',
        'fecha_entrega',
        'estado',
    ] = 'fecha_asignacion',
    sort_order: SortOrder = 'desc',
    operations: OperationalService = Depends(service),
) -> Page[AsignacionRead]:
    return operations.list_asignaciones(
        q=q,
        estado=estado,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get('/asignaciones/{asignacion_id}', response_model=AsignacionRead)
def get_asignacion(
    asignacion_id: int,
    operations: OperationalService = Depends(service),
) -> AsignacionRead:
    return operations.get_asignacion(asignacion_id)


@router.patch('/asignaciones/{asignacion_id}', response_model=AsignacionRead)
def update_asignacion(
    asignacion_id: int,
    payload: AsignacionUpdate,
    operations: OperationalService = Depends(service),
) -> AsignacionRead:
    return operations.update_asignacion(asignacion_id, payload)


@router.delete(
    '/asignaciones/{asignacion_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_asignacion(
    asignacion_id: int,
    operations: OperationalService = Depends(service),
) -> Response:
    operations.delete_asignacion(asignacion_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/operacion/resumen', response_model=ResumenOperacional)
def resumen_operacional(
    operations: OperationalService = Depends(service),
) -> ResumenOperacional:
    return operations.resumen()
