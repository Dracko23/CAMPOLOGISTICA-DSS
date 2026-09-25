from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PedidoEstado = Literal['pendiente', 'asignado', 'en_camino', 'entregado', 'cancelado']
AsignacionEstado = Literal['asignada', 'aceptada', 'en_camino', 'llegue', 'entregada', 'cancelada']
SortOrder = Literal['asc', 'desc']
T = TypeVar('T')


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class Page(ApiModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int


class ClienteCreate(ApiModel):
    nombre: str = Field(min_length=1, max_length=120)
    telefono: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=150)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value and ('@' not in value or value.startswith('@') or value.endswith('@')):
            raise ValueError('El correo electrónico no es válido.')
        return value or None


class ClienteUpdate(ApiModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    telefono: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=150)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value and ('@' not in value or value.startswith('@') or value.endswith('@')):
            raise ValueError('El correo electrónico no es válido.')
        return value or None


class ClienteRead(ApiModel):
    id_cliente: int
    nombre: str
    telefono: str | None
    email: str | None


class UbicacionCreate(ApiModel):
    direccion: str = Field(min_length=1, max_length=200)
    zona: str = Field(min_length=1, max_length=80)
    ciudad: str | None = Field(default=None, max_length=100)
    departamento: str | None = Field(default=None, max_length=100)
    latitud: Decimal | None = Field(default=None, ge=-90, le=90)
    longitud: Decimal | None = Field(default=None, ge=-180, le=180)


class UbicacionUpdate(ApiModel):
    direccion: str | None = Field(default=None, min_length=1, max_length=200)
    zona: str | None = Field(default=None, min_length=1, max_length=80)
    ciudad: str | None = Field(default=None, max_length=100)
    departamento: str | None = Field(default=None, max_length=100)
    latitud: Decimal | None = Field(default=None, ge=-90, le=90)
    longitud: Decimal | None = Field(default=None, ge=-180, le=180)


class UbicacionRead(ApiModel):
    id_ubicacion: int
    direccion: str
    zona: str
    ciudad: str | None = None
    departamento: str | None = None
    latitud: Decimal | None
    longitud: Decimal | None


class PedidoCoreCreate(ApiModel):
    codigo: str = Field(min_length=1, max_length=30)
    fecha_limite: datetime
    peso_kg: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    urgencia: int = Field(ge=1, le=5)
    estado: Literal['pendiente'] = 'pendiente'

    @field_validator('fecha_limite')
    @classmethod
    def validate_future_deadline(cls, value: datetime) -> datetime:
        if value <= datetime.now(value.tzinfo):
            raise ValueError('Selecciona una fecha y hora futuras.')
        return value


class PedidoCoreUpdate(ApiModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=30)
    fecha_limite: datetime | None = None
    peso_kg: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    urgencia: int | None = Field(default=None, ge=1, le=5)

    @field_validator('fecha_limite')
    @classmethod
    def validate_future_deadline(cls, value: datetime | None) -> datetime | None:
        if value is not None and value <= datetime.now(value.tzinfo):
            raise ValueError('Selecciona una fecha y hora futuras.')
        return value


class PedidoCreate(ApiModel):
    cliente: ClienteCreate | None = None
    id_cliente: int | None = Field(default=None, gt=0)
    ubicacion: UbicacionCreate
    pedido: PedidoCoreCreate

    @model_validator(mode='after')
    def ensure_client(self) -> PedidoCreate:
        if (self.cliente is None) == (self.id_cliente is None):
            raise ValueError('Selecciona un cliente existente o registra uno nuevo.')
        return self


class PedidoUpdate(ApiModel):
    cliente: ClienteUpdate | None = None
    ubicacion: UbicacionUpdate | None = None
    pedido: PedidoCoreUpdate | None = None

    @model_validator(mode='after')
    def ensure_changes(self) -> PedidoUpdate:
        if not any((self.cliente, self.ubicacion, self.pedido)):
            raise ValueError('Debe enviar al menos un cambio.')
        return self


class ConductorCreate(ApiModel):
    nombre: str = Field(min_length=1, max_length=120)
    licencia: str = Field(min_length=1, max_length=40)
    disponible: bool = True


class ConductorUpdate(ApiModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    licencia: str | None = Field(default=None, min_length=1, max_length=40)
    disponible: bool | None = None


class ConductorRead(ApiModel):
    id_conductor: int
    nombre: str
    licencia: str | None
    disponible: bool


class VehiculoCreate(ApiModel):
    placa: str = Field(min_length=1, max_length=20)
    capacidad_kg: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    rendimiento_km_l: Decimal = Field(gt=0, max_digits=8, decimal_places=2)
    disponible: bool = True


class VehiculoUpdate(ApiModel):
    placa: str | None = Field(default=None, min_length=1, max_length=20)
    capacidad_kg: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    rendimiento_km_l: Decimal | None = Field(default=None, gt=0, max_digits=8, decimal_places=2)
    disponible: bool | None = None


class VehiculoRead(ApiModel):
    id_vehiculo: int
    placa: str | None
    capacidad_kg: Decimal | None
    rendimiento_km_l: Decimal | None
    disponible: bool


class AsignacionBrief(ApiModel):
    id_asignacion: int
    fecha_asignacion: datetime
    fecha_salida: datetime | None
    fecha_aceptacion: datetime | None = None
    fecha_llegada: datetime | None = None
    fecha_entrega: datetime | None
    estado: str
    conductor: ConductorRead
    vehiculo: VehiculoRead


class PedidoRead(ApiModel):
    id_pedido: int
    codigo: str | None
    fecha_registro: datetime
    fecha_limite: datetime
    peso_kg: Decimal | None
    urgencia: int | None
    estado: str
    cliente: ClienteRead
    ubicacion: UbicacionRead
    asignacion_actual: AsignacionBrief | None = None


class PedidoDetail(PedidoRead):
    asignaciones: list[AsignacionBrief]


class AsignacionCreate(ApiModel):
    id_pedido: int = Field(gt=0)
    id_conductor: int = Field(gt=0)
    id_vehiculo: int = Field(gt=0)


class AsignacionUpdate(ApiModel):
    estado: AsignacionEstado


class PedidoAssignmentRead(ApiModel):
    id_pedido: int
    codigo: str | None
    peso_kg: Decimal | None
    urgencia: int | None
    estado: str
    ubicacion: UbicacionRead


class AsignacionRead(ApiModel):
    id_asignacion: int
    fecha_asignacion: datetime
    fecha_salida: datetime | None
    fecha_aceptacion: datetime | None = None
    fecha_llegada: datetime | None = None
    fecha_entrega: datetime | None
    distancia_km: Decimal | None
    combustible_litros: Decimal | None
    costo_combustible: Decimal | None
    estado: str
    pedido: PedidoAssignmentRead
    conductor: ConductorRead
    vehiculo: VehiculoRead


class ActividadRead(ApiModel):
    tipo: Literal['pedido', 'asignacion']
    id: int
    titulo: str
    detalle: str
    fecha: datetime


class ResumenOperacional(ApiModel):
    pedidos_registrados: int
    pedidos_pendientes: int
    pedidos_asignados: int
    conductores_disponibles: int
    vehiculos_disponibles: int
    actividad_reciente: list[ActividadRead]
