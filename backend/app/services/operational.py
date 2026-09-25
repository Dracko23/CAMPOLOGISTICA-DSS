from __future__ import annotations

from datetime import datetime
from math import ceil
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import Asignacion, Cliente, Conductor, Pedido, Ubicacion, Vehiculo
from app.repositories import OperationalRepository
from app.schemas.operational import (
    ActividadRead,
    AsignacionBrief,
    AsignacionCreate,
    AsignacionRead,
    AsignacionUpdate,
    ConductorCreate,
    ConductorRead,
    ConductorUpdate,
    ClienteRead,
    Page,
    PedidoCreate,
    PedidoDetail,
    PedidoRead,
    PedidoUpdate,
    ResumenOperacional,
    VehiculoCreate,
    VehiculoRead,
    VehiculoUpdate,
)


class OperationalService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = OperationalRepository(session)

    @staticmethod
    def _total_pages(total: int, page_size: int) -> int:
        return ceil(total / page_size) if total else 0

    @staticmethod
    def _constraint_name(error: IntegrityError) -> str | None:
        diagnostic = getattr(error.orig, 'diag', None)
        return getattr(diagnostic, 'constraint_name', None)

    def _raise_integrity_error(self, error: IntegrityError) -> None:
        constraint = self._constraint_name(error)
        mappings = {
            'uq_pedido_codigo': (
                'pedido_codigo_duplicado',
                'Ya existe un pedido con ese código.',
                'codigo',
            ),
            'uq_conductor_licencia': (
                'conductor_licencia_duplicada',
                'Ya existe un conductor con esa licencia.',
                'licencia',
            ),
            'uq_vehiculo_placa': (
                'vehiculo_placa_duplicada',
                'Ya existe un vehículo con esa placa.',
                'placa',
            ),
        }
        code, message, field = mappings.get(
            constraint,
            (
                'conflicto_integridad',
                'La operación entra en conflicto con datos existentes.',
                None,
            ),
        )
        raise ConflictError(code, message, field) from None

    def _commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            self._raise_integrity_error(error)

    @staticmethod
    def _asignacion_brief(asignacion: Asignacion) -> AsignacionBrief:
        return AsignacionBrief(
            id_asignacion=asignacion.id_asignacion,
            fecha_asignacion=asignacion.fecha_asignacion,
            fecha_salida=asignacion.fecha_salida,
            fecha_aceptacion=asignacion.fecha_aceptacion,
            fecha_llegada=asignacion.fecha_llegada,
            fecha_entrega=asignacion.fecha_entrega,
            estado=asignacion.estado,
            conductor=asignacion.conductor,
            vehiculo=asignacion.vehiculo,
        )

    def _pedido_read(
        self, pedido: Pedido, *, detail: bool = False
    ) -> PedidoRead | PedidoDetail:
        assignments = sorted(
            pedido.asignaciones,
            key=lambda item: (item.fecha_asignacion, item.id_asignacion),
            reverse=True,
        )
        active = next(
            (
                item
                for item in assignments
                if item.estado in {'asignada', 'aceptada', 'en_camino', 'llegue'}
            ),
            None,
        )
        values: dict[str, Any] = {
            'id_pedido': pedido.id_pedido,
            'codigo': pedido.codigo,
            'fecha_registro': pedido.fecha_registro,
            'fecha_limite': pedido.fecha_limite,
            'peso_kg': pedido.peso_kg,
            'urgencia': pedido.urgencia,
            'estado': pedido.estado,
            'cliente': pedido.cliente,
            'ubicacion': pedido.ubicacion,
            'asignacion_actual': self._asignacion_brief(active) if active else None,
        }
        if detail:
            values['asignaciones'] = [
                self._asignacion_brief(item) for item in assignments
            ]
            return PedidoDetail.model_validate(values)
        return PedidoRead.model_validate(values)

    @staticmethod
    def _asignacion_read(asignacion: Asignacion) -> AsignacionRead:
        return AsignacionRead.model_validate(
            {
                'id_asignacion': asignacion.id_asignacion,
                'fecha_asignacion': asignacion.fecha_asignacion,
                'fecha_salida': asignacion.fecha_salida,
                'fecha_aceptacion': asignacion.fecha_aceptacion,
                'fecha_llegada': asignacion.fecha_llegada,
                'fecha_entrega': asignacion.fecha_entrega,
                'distancia_km': asignacion.distancia_km,
                'combustible_litros': asignacion.combustible_litros,
                'costo_combustible': asignacion.costo_combustible,
                'estado': asignacion.estado,
                'pedido': {
                    'id_pedido': asignacion.pedido.id_pedido,
                    'codigo': asignacion.pedido.codigo,
                    'peso_kg': asignacion.pedido.peso_kg,
                    'urgencia': asignacion.pedido.urgencia,
                    'estado': asignacion.pedido.estado,
                    'ubicacion': asignacion.pedido.ubicacion,
                },
                'conductor': asignacion.conductor,
                'vehiculo': asignacion.vehiculo,
            }
        )

    def create_pedido(self, payload: PedidoCreate) -> PedidoRead:
        if payload.id_cliente is not None:
            cliente = self.repository.get_cliente(payload.id_cliente)
            if not cliente:
                raise NotFoundError('cliente_no_encontrado', 'El cliente no existe.')
        else:
            assert payload.cliente is not None
            cliente = Cliente(**payload.cliente.model_dump())
        ubicacion = Ubicacion(**payload.ubicacion.model_dump())
        pedido = Pedido(
            **payload.pedido.model_dump(),
            fecha_registro=datetime.now(),
            cliente=cliente,
            ubicacion=ubicacion,
        )
        self.session.add(pedido)
        self._commit()
        return self._pedido_read(pedido)

    def list_clientes(self, q: str | None = None) -> list[ClienteRead]:
        return [ClienteRead.model_validate(item) for item in self.repository.list_clientes(q)]

    def list_pedidos(
        self,
        *,
        q: str | None,
        estado: str | None,
        urgencia: int | None,
        zona: str | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> Page[PedidoRead]:
        items, total = self.repository.list_pedidos(
            q=q,
            estado=estado,
            urgencia=urgencia,
            zona=zona,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return Page[PedidoRead](
            items=[self._pedido_read(item) for item in items],
            page=page,
            page_size=page_size,
            total=total,
            total_pages=self._total_pages(total, page_size),
        )

    def get_pedido(self, pedido_id: int) -> PedidoDetail:
        pedido = self.repository.get_pedido(pedido_id)
        if not pedido:
            raise NotFoundError('pedido_no_encontrado', 'El pedido no existe.')
        result = self._pedido_read(pedido, detail=True)
        assert isinstance(result, PedidoDetail)
        return result

    def update_pedido(self, pedido_id: int, payload: PedidoUpdate) -> PedidoRead:
        pedido = self.repository.get_pedido(pedido_id, lock=True)
        if not pedido:
            raise NotFoundError('pedido_no_encontrado', 'El pedido no existe.')
        if payload.cliente:
            for field, value in payload.cliente.model_dump(exclude_unset=True).items():
                setattr(pedido.cliente, field, value)
        if payload.ubicacion:
            for field, value in payload.ubicacion.model_dump(exclude_unset=True).items():
                setattr(pedido.ubicacion, field, value)
        if payload.pedido:
            changes = payload.pedido.model_dump(exclude_unset=True)
            new_weight = changes.get('peso_kg')
            active = next(
                (
                    item
                    for item in pedido.asignaciones
                if item.estado in {'asignada', 'aceptada', 'en_camino', 'llegue'}
                ),
                None,
            )
            if (
                new_weight is not None
                and active is not None
                and active.vehiculo.capacidad_kg is not None
                and new_weight > active.vehiculo.capacidad_kg
            ):
                raise ConflictError(
                    'capacidad_insuficiente',
                    'El peso supera la capacidad del vehículo asignado.',
                    'peso_kg',
                )
            for field, value in changes.items():
                setattr(pedido, field, value)
        self._commit()
        return self._pedido_read(pedido)

    def delete_pedido(self, pedido_id: int) -> None:
        pedido = self.repository.get_pedido(pedido_id, lock=True)
        if not pedido:
            raise NotFoundError('pedido_no_encontrado', 'El pedido no existe.')
        if self.repository.resource_has_assignments(Pedido, pedido_id):
            raise ConflictError(
                'pedido_con_asignaciones',
                'No se puede eliminar un pedido que tiene asignaciones.',
            )
        cliente = pedido.cliente
        ubicacion = pedido.ubicacion
        self.session.delete(pedido)
        self.session.flush()
        if cliente:
            self.session.delete(cliente)
        if ubicacion:
            self.session.delete(ubicacion)
        self._commit()

    def create_conductor(self, payload: ConductorCreate) -> ConductorRead:
        conductor = Conductor(**payload.model_dump())
        self.session.add(conductor)
        self._commit()
        return ConductorRead.model_validate(conductor)

    def list_conductores(
        self,
        *,
        q: str | None,
        disponible: bool | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> Page[ConductorRead]:
        items, total = self.repository.list_conductores(
            q=q,
            disponible=disponible,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return Page[ConductorRead](
            items=[ConductorRead.model_validate(item) for item in items],
            page=page,
            page_size=page_size,
            total=total,
            total_pages=self._total_pages(total, page_size),
        )

    def get_conductor(self, conductor_id: int) -> ConductorRead:
        conductor = self.repository.get_conductor(conductor_id)
        if not conductor:
            raise NotFoundError('conductor_no_encontrado', 'El conductor no existe.')
        return ConductorRead.model_validate(conductor)

    def update_conductor(
        self, conductor_id: int, payload: ConductorUpdate
    ) -> ConductorRead:
        conductor = self.repository.get_conductor(conductor_id, lock=True)
        if not conductor:
            raise NotFoundError('conductor_no_encontrado', 'El conductor no existe.')
        changes = payload.model_dump(exclude_unset=True)
        if changes.get('disponible') is True and self.repository.resource_has_active_assignments(
            Conductor, conductor_id
        ):
            raise ConflictError(
                'conductor_con_asignacion_activa',
                'El conductor tiene una asignación activa y no puede marcarse disponible.',
                'disponible',
            )
        for field, value in changes.items():
            setattr(conductor, field, value)
        self._commit()
        return ConductorRead.model_validate(conductor)

    def delete_conductor(self, conductor_id: int) -> None:
        conductor = self.repository.get_conductor(conductor_id, lock=True)
        if not conductor:
            raise NotFoundError('conductor_no_encontrado', 'El conductor no existe.')
        if self.repository.resource_has_assignments(Conductor, conductor_id):
            raise ConflictError(
                'conductor_con_asignaciones',
                'No se puede eliminar un conductor que tiene asignaciones.',
            )
        self.session.delete(conductor)
        self._commit()

    def create_vehiculo(self, payload: VehiculoCreate) -> VehiculoRead:
        vehiculo = Vehiculo(**payload.model_dump())
        self.session.add(vehiculo)
        self._commit()
        return VehiculoRead.model_validate(vehiculo)

    def list_vehiculos(
        self,
        *,
        q: str | None,
        disponible: bool | None,
        capacidad_min: float | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> Page[VehiculoRead]:
        items, total = self.repository.list_vehiculos(
            q=q,
            disponible=disponible,
            capacidad_min=capacidad_min,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return Page[VehiculoRead](
            items=[VehiculoRead.model_validate(item) for item in items],
            page=page,
            page_size=page_size,
            total=total,
            total_pages=self._total_pages(total, page_size),
        )

    def get_vehiculo(self, vehiculo_id: int) -> VehiculoRead:
        vehiculo = self.repository.get_vehiculo(vehiculo_id)
        if not vehiculo:
            raise NotFoundError('vehiculo_no_encontrado', 'El vehículo no existe.')
        return VehiculoRead.model_validate(vehiculo)

    def update_vehiculo(
        self, vehiculo_id: int, payload: VehiculoUpdate
    ) -> VehiculoRead:
        vehiculo = self.repository.get_vehiculo(vehiculo_id, lock=True)
        if not vehiculo:
            raise NotFoundError('vehiculo_no_encontrado', 'El vehículo no existe.')
        changes = payload.model_dump(exclude_unset=True)
        if changes.get('disponible') is True and self.repository.resource_has_active_assignments(
            Vehiculo, vehiculo_id
        ):
            raise ConflictError(
                'vehiculo_con_asignacion_activa',
                'El vehículo tiene una asignación activa y no puede marcarse disponible.',
                'disponible',
            )
        for field, value in changes.items():
            setattr(vehiculo, field, value)
        self._commit()
        return VehiculoRead.model_validate(vehiculo)

    def delete_vehiculo(self, vehiculo_id: int) -> None:
        vehiculo = self.repository.get_vehiculo(vehiculo_id, lock=True)
        if not vehiculo:
            raise NotFoundError('vehiculo_no_encontrado', 'El vehículo no existe.')
        if self.repository.resource_has_assignments(Vehiculo, vehiculo_id):
            raise ConflictError(
                'vehiculo_con_asignaciones',
                'No se puede eliminar un vehículo que tiene asignaciones.',
            )
        self.session.delete(vehiculo)
        self._commit()

    def create_asignacion(self, payload: AsignacionCreate) -> AsignacionRead:
        pedido = self.repository.get_pedido(payload.id_pedido, lock=True)
        if not pedido:
            raise NotFoundError('pedido_no_encontrado', 'El pedido no existe.')
        conductor = self.repository.get_conductor(payload.id_conductor, lock=True)
        if not conductor:
            raise NotFoundError('conductor_no_encontrado', 'El conductor no existe.')
        vehiculo = self.repository.get_vehiculo(payload.id_vehiculo, lock=True)
        if not vehiculo:
            raise NotFoundError('vehiculo_no_encontrado', 'El vehículo no existe.')
        if pedido.estado != 'pendiente':
            raise ConflictError(
                'pedido_no_asignable',
                'El pedido ya no está pendiente de asignación.',
            )
        if not conductor.disponible:
            raise ConflictError(
                'conductor_no_disponible',
                'El conductor no está disponible.',
            )
        if not vehiculo.disponible:
            raise ConflictError(
                'vehiculo_no_disponible',
                'El vehículo no está disponible.',
            )
        if vehiculo.capacidad_kg is None or pedido.peso_kg is None:
            raise ConflictError(
                'capacidad_no_verificable',
                'No se pudo verificar la capacidad del vehículo.',
            )
        if vehiculo.capacidad_kg < pedido.peso_kg:
            raise ConflictError(
                'capacidad_insuficiente',
                'La capacidad del vehículo es insuficiente para el pedido.',
            )
        asignacion = Asignacion(
            pedido=pedido,
            conductor=conductor,
            vehiculo=vehiculo,
            fecha_asignacion=datetime.now(),
            fecha_salida=None,
            fecha_entrega=None,
            distancia_km=None,
            combustible_litros=None,
            costo_combustible=None,
            estado='asignada',
        )
        pedido.estado = 'asignado'
        conductor.disponible = False
        vehiculo.disponible = False
        self.session.add(asignacion)
        self._commit()
        return self._asignacion_read(asignacion)

    def list_asignaciones(
        self,
        *,
        q: str | None,
        estado: str | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> Page[AsignacionRead]:
        items, total = self.repository.list_asignaciones(
            q=q,
            estado=estado,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return Page[AsignacionRead](
            items=[self._asignacion_read(item) for item in items],
            page=page,
            page_size=page_size,
            total=total,
            total_pages=self._total_pages(total, page_size),
        )

    def get_asignacion(self, asignacion_id: int) -> AsignacionRead:
        asignacion = self.repository.get_asignacion(asignacion_id)
        if not asignacion:
            raise NotFoundError(
                'asignacion_no_encontrada', 'La asignación no existe.'
            )
        return self._asignacion_read(asignacion)

    def update_asignacion(
        self, asignacion_id: int, payload: AsignacionUpdate
    ) -> AsignacionRead:
        asignacion = self.repository.get_asignacion(asignacion_id, lock=True)
        if not asignacion:
            raise NotFoundError(
                'asignacion_no_encontrada', 'La asignación no existe.'
            )
        current = asignacion.estado
        target = payload.estado
        if current == target:
            return self._asignacion_read(asignacion)
        transitions = {
            'asignada': {'aceptada', 'cancelada'},
            'aceptada': {'en_camino', 'cancelada'},
            'en_camino': {'llegue', 'cancelada'},
            'llegue': {'entregada', 'cancelada'},
            'entregada': set(),
            'cancelada': set(),
        }
        if target not in transitions.get(current, set()):
            raise ConflictError(
                'transicion_asignacion_invalida',
                f'No se puede cambiar una asignación de {current} a {target}.',
            )
        now = datetime.now()
        if target == 'aceptada':
            asignacion.fecha_aceptacion = now
        elif target == 'en_camino':
            asignacion.fecha_salida = now
            asignacion.pedido.estado = 'en_camino'
        elif target == 'llegue':
            asignacion.fecha_llegada = now
        elif target == 'entregada':
            asignacion.fecha_salida = asignacion.fecha_salida or now
            asignacion.fecha_entrega = now
            asignacion.pedido.estado = 'entregado'
            asignacion.conductor.disponible = True
            asignacion.vehiculo.disponible = True
        elif target == 'cancelada':
            asignacion.pedido.estado = 'pendiente'
            asignacion.conductor.disponible = True
            asignacion.vehiculo.disponible = True
        asignacion.estado = target
        self._commit()
        return self._asignacion_read(asignacion)

    def delete_asignacion(self, asignacion_id: int) -> None:
        asignacion = self.repository.get_asignacion(asignacion_id, lock=True)
        if not asignacion:
            raise NotFoundError(
                'asignacion_no_encontrada', 'La asignación no existe.'
            )
        if asignacion.estado != 'cancelada':
            raise ConflictError(
                'asignacion_no_eliminable',
                'Solo se puede eliminar una asignación cancelada.',
            )
        self.session.delete(asignacion)
        self._commit()

    def resumen(self) -> ResumenOperacional:
        activities: list[ActividadRead] = []
        for pedido in self.repository.recent_pedidos():
            activities.append(
                ActividadRead(
                    tipo='pedido',
                    id=pedido.id_pedido,
                    titulo=pedido.codigo or f'Pedido {pedido.id_pedido}',
                    detalle=f'Pedido registrado · Estado: {pedido.estado}',
                    fecha=pedido.fecha_registro,
                )
            )
        for asignacion in self.repository.recent_asignaciones():
            activities.append(
                ActividadRead(
                    tipo='asignacion',
                    id=asignacion.id_asignacion,
                    titulo=asignacion.pedido.codigo
                    or f'Pedido {asignacion.id_pedido}',
                    detalle=f'Asignación {asignacion.estado}',
                    fecha=asignacion.fecha_asignacion,
                )
            )
        activities.sort(key=lambda item: item.fecha, reverse=True)
        return ResumenOperacional(
            pedidos_registrados=self.repository.count_pedidos(),
            pedidos_pendientes=self.repository.count_pedidos('pendiente'),
            pedidos_asignados=self.repository.count_pedidos('asignado'),
            conductores_disponibles=self.repository.count_conductores_disponibles(),
            vehiculos_disponibles=self.repository.count_vehiculos_disponibles(),
            actividad_reciente=activities[:8],
        )
