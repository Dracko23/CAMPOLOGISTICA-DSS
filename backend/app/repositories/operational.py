from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Asignacion, Cliente, Conductor, Pedido, Ubicacion, Vehiculo


class OperationalRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _paginate(statement: Select[Any], page: int, page_size: int) -> Select[Any]:
        return statement.offset((page - 1) * page_size).limit(page_size)

    def _count(self, statement: Select[Any]) -> int:
        count_statement = select(func.count()).select_from(
            statement.order_by(None).limit(None).offset(None).subquery()
        )
        return int(self.session.scalar(count_statement) or 0)

    def get_pedido(self, pedido_id: int, *, lock: bool = False) -> Pedido | None:
        statement = (
            select(Pedido)
            .where(Pedido.id_pedido == pedido_id)
            .options(
                selectinload(Pedido.cliente),
                selectinload(Pedido.ubicacion),
                selectinload(Pedido.asignaciones).selectinload(Asignacion.conductor),
                selectinload(Pedido.asignaciones).selectinload(Asignacion.vehiculo),
            )
        )
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def get_cliente(self, cliente_id: int) -> Cliente | None:
        return self.session.get(Cliente, cliente_id)

    def list_clientes(self, q: str | None = None) -> Sequence[Cliente]:
        statement = select(Cliente)
        if q:
            pattern = f'%{q}%'
            statement = statement.where(or_(Cliente.nombre.ilike(pattern), Cliente.telefono.ilike(pattern), Cliente.email.ilike(pattern)))
        return self.session.scalars(statement.order_by(Cliente.nombre).limit(100)).all()

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
    ) -> tuple[Sequence[Pedido], int]:
        statement = select(Pedido).join(Pedido.cliente).join(Pedido.ubicacion)
        if q:
            pattern = f'%{q}%'
            statement = statement.where(
                or_(
                    Pedido.codigo.ilike(pattern),
                    Cliente.nombre.ilike(pattern),
                    Ubicacion.direccion.ilike(pattern),
                    Ubicacion.zona.ilike(pattern),
                )
            )
        if estado:
            statement = statement.where(Pedido.estado == estado)
        if urgencia is not None:
            statement = statement.where(Pedido.urgencia == urgencia)
        if zona:
            statement = statement.where(Ubicacion.zona.ilike(zona))
        total = self._count(statement)
        sort_columns = {
            'id_pedido': Pedido.id_pedido,
            'codigo': Pedido.codigo,
            'fecha_registro': Pedido.fecha_registro,
            'fecha_limite': Pedido.fecha_limite,
            'peso_kg': Pedido.peso_kg,
            'urgencia': Pedido.urgencia,
            'estado': Pedido.estado,
        }
        column = sort_columns.get(sort_by, Pedido.fecha_registro)
        ordering = column.asc() if sort_order == 'asc' else column.desc()
        statement = (
            statement.order_by(ordering, Pedido.id_pedido.asc())
            .options(
                selectinload(Pedido.cliente),
                selectinload(Pedido.ubicacion),
                selectinload(Pedido.asignaciones).selectinload(Asignacion.conductor),
                selectinload(Pedido.asignaciones).selectinload(Asignacion.vehiculo),
            )
        )
        return self.session.scalars(
            self._paginate(statement, page, page_size)
        ).all(), total

    def get_conductor(
        self, conductor_id: int, *, lock: bool = False
    ) -> Conductor | None:
        statement = select(Conductor).where(Conductor.id_conductor == conductor_id)
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def list_conductores(
        self,
        *,
        q: str | None,
        disponible: bool | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> tuple[Sequence[Conductor], int]:
        statement = select(Conductor)
        if q:
            pattern = f'%{q}%'
            statement = statement.where(
                or_(Conductor.nombre.ilike(pattern), Conductor.licencia.ilike(pattern))
            )
        if disponible is not None:
            statement = statement.where(Conductor.disponible.is_(disponible))
        total = self._count(statement)
        sort_columns = {
            'id_conductor': Conductor.id_conductor,
            'nombre': Conductor.nombre,
            'licencia': Conductor.licencia,
            'disponible': Conductor.disponible,
        }
        column = sort_columns.get(sort_by, Conductor.nombre)
        ordering = column.asc() if sort_order == 'asc' else column.desc()
        statement = statement.order_by(ordering, Conductor.id_conductor.asc())
        return self.session.scalars(
            self._paginate(statement, page, page_size)
        ).all(), total

    def get_vehiculo(
        self, vehiculo_id: int, *, lock: bool = False
    ) -> Vehiculo | None:
        statement = select(Vehiculo).where(Vehiculo.id_vehiculo == vehiculo_id)
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

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
    ) -> tuple[Sequence[Vehiculo], int]:
        statement = select(Vehiculo)
        if q:
            statement = statement.where(Vehiculo.placa.ilike(f'%{q}%'))
        if disponible is not None:
            statement = statement.where(Vehiculo.disponible.is_(disponible))
        if capacidad_min is not None:
            statement = statement.where(Vehiculo.capacidad_kg >= capacidad_min)
        total = self._count(statement)
        sort_columns = {
            'id_vehiculo': Vehiculo.id_vehiculo,
            'placa': Vehiculo.placa,
            'capacidad_kg': Vehiculo.capacidad_kg,
            'rendimiento_km_l': Vehiculo.rendimiento_km_l,
            'disponible': Vehiculo.disponible,
        }
        column = sort_columns.get(sort_by, Vehiculo.placa)
        ordering = column.asc() if sort_order == 'asc' else column.desc()
        statement = statement.order_by(ordering, Vehiculo.id_vehiculo.asc())
        return self.session.scalars(
            self._paginate(statement, page, page_size)
        ).all(), total

    def get_asignacion(
        self, asignacion_id: int, *, lock: bool = False
    ) -> Asignacion | None:
        statement = (
            select(Asignacion)
            .where(Asignacion.id_asignacion == asignacion_id)
            .options(
                selectinload(Asignacion.pedido).selectinload(Pedido.ubicacion),
                selectinload(Asignacion.conductor),
                selectinload(Asignacion.vehiculo),
            )
        )
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def list_asignaciones(
        self,
        *,
        q: str | None,
        estado: str | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> tuple[Sequence[Asignacion], int]:
        statement = (
            select(Asignacion)
            .join(Asignacion.pedido)
            .join(Asignacion.conductor)
            .join(Asignacion.vehiculo)
        )
        if q:
            pattern = f'%{q}%'
            statement = statement.where(
                or_(
                    Pedido.codigo.ilike(pattern),
                    Conductor.nombre.ilike(pattern),
                    Conductor.licencia.ilike(pattern),
                    Vehiculo.placa.ilike(pattern),
                )
            )
        if estado:
            statement = statement.where(Asignacion.estado == estado)
        total = self._count(statement)
        sort_columns = {
            'id_asignacion': Asignacion.id_asignacion,
            'fecha_asignacion': Asignacion.fecha_asignacion,
            'fecha_salida': Asignacion.fecha_salida,
            'fecha_entrega': Asignacion.fecha_entrega,
            'estado': Asignacion.estado,
        }
        column = sort_columns.get(sort_by, Asignacion.fecha_asignacion)
        ordering = column.asc() if sort_order == 'asc' else column.desc()
        statement = (
            statement.order_by(ordering, Asignacion.id_asignacion.desc())
            .options(
                selectinload(Asignacion.pedido).selectinload(Pedido.ubicacion),
                selectinload(Asignacion.conductor),
                selectinload(Asignacion.vehiculo),
            )
        )
        return self.session.scalars(
            self._paginate(statement, page, page_size)
        ).all(), total

    def resource_has_assignments(self, model: type[Any], identifier: int) -> bool:
        if model is Pedido:
            predicate = Asignacion.id_pedido == identifier
        elif model is Conductor:
            predicate = Asignacion.id_conductor == identifier
        elif model is Vehiculo:
            predicate = Asignacion.id_vehiculo == identifier
        else:
            raise ValueError('Tipo de recurso no soportado.')
        return bool(
            self.session.scalar(
                select(func.count()).select_from(Asignacion).where(predicate)
            )
        )

    def resource_has_active_assignments(
        self, model: type[Any], identifier: int
    ) -> bool:
        if model is Conductor:
            predicate = Asignacion.id_conductor == identifier
        elif model is Vehiculo:
            predicate = Asignacion.id_vehiculo == identifier
        else:
            raise ValueError('Tipo de recurso no soportado.')
        return bool(
            self.session.scalar(
                select(func.count())
                .select_from(Asignacion)
                .where(
                    predicate,
                    Asignacion.estado.in_({'asignada', 'aceptada', 'en_camino', 'llegue'}),
                )
            )
        )

    def count_pedidos(self, estado: str | None = None) -> int:
        statement = select(func.count()).select_from(Pedido)
        if estado:
            statement = statement.where(Pedido.estado == estado)
        return int(self.session.scalar(statement) or 0)

    def count_conductores_disponibles(self) -> int:
        return int(
            self.session.scalar(
                select(func.count())
                .select_from(Conductor)
                .where(Conductor.disponible.is_(True))
            )
            or 0
        )

    def count_vehiculos_disponibles(self) -> int:
        return int(
            self.session.scalar(
                select(func.count())
                .select_from(Vehiculo)
                .where(Vehiculo.disponible.is_(True))
            )
            or 0
        )

    def recent_pedidos(self, limit: int = 8) -> Sequence[Pedido]:
        statement = (
            select(Pedido)
            .order_by(Pedido.fecha_registro.desc(), Pedido.id_pedido.desc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()

    def recent_asignaciones(self, limit: int = 8) -> Sequence[Asignacion]:
        statement = (
            select(Asignacion)
            .options(selectinload(Asignacion.pedido))
            .order_by(Asignacion.fecha_asignacion.desc(), Asignacion.id_asignacion.desc())
            .limit(limit)
        )
        return self.session.scalars(statement).all()
