from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Asignacion, Cliente, Conductor, Pedido, Ubicacion, Vehiculo
from tests.conftest import ApiClient


API = '/api/v1'


def pedido_payload(code: str = 'PED-API-001', weight: float = 125.5) -> dict:
    return {
        'cliente': {
            'nombre': 'Cliente Demo Tarija',
            'telefono': '72900001',
            'email': 'demo.tarija@example.test',
        },
        'ubicacion': {
            'direccion': 'Av. La Paz 455',
            'zona': 'San Roque',
            'latitud': -21.5312,
            'longitud': -64.7312,
        },
        'pedido': {
            'codigo': code,
            'fecha_limite': (datetime.now() + timedelta(days=2)).isoformat(),
            'peso_kg': weight,
            'urgencia': 4,
            'estado': 'pendiente',
        },
    }


def create_pedido(client: ApiClient, code: str, weight: float = 125.5) -> dict:
    response = client.post(f'{API}/pedidos', json=pedido_payload(code, weight))
    assert response.status_code == 201, response.text
    return response.json()


def create_conductor(
    client: ApiClient, license_code: str, available: bool = True
) -> dict:
    response = client.post(
        f'{API}/conductores',
        json={
            'nombre': 'Carlos Mendoza',
            'licencia': license_code,
            'disponible': available,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_vehiculo(
    client: ApiClient,
    plate: str,
    capacity: float = 1000,
    available: bool = True,
) -> dict:
    response = client.post(
        f'{API}/vehiculos',
        json={
            'placa': plate,
            'capacidad_kg': capacity,
            'rendimiento_km_l': 11.5,
            'disponible': available,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_pedido_compuesto_crud_busqueda_y_detalle(api_client: ApiClient) -> None:
    created = create_pedido(api_client, 'PED-API-001')
    pedido_id = created['id_pedido']
    assert created['cliente']['nombre'] == 'Cliente Demo Tarija'
    assert created['ubicacion']['zona'] == 'San Roque'
    assert created['asignacion_actual'] is None

    listing = api_client.get(
        f'{API}/pedidos',
        params={'q': 'API-001', 'zona': 'San Roque', 'page': 1, 'page_size': 10},
    )
    assert listing.status_code == 200
    assert listing.json()['total'] == 1

    detail = api_client.get(f'{API}/pedidos/{pedido_id}')
    assert detail.status_code == 200
    assert detail.json()['asignaciones'] == []

    invalid_email = api_client.patch(
        f'{API}/pedidos/{pedido_id}',
        json={'cliente': {'email': 'correo-sin-arroba'}},
    )
    assert invalid_email.status_code == 422

    updated = api_client.patch(
        f'{API}/pedidos/{pedido_id}',
        json={
            'cliente': {'telefono': '72999999'},
            'ubicacion': {'zona': 'El Molino'},
            'pedido': {'urgencia': 5},
        },
    )
    assert updated.status_code == 200
    assert updated.json()['cliente']['telefono'] == '72999999'
    assert updated.json()['ubicacion']['zona'] == 'El Molino'
    assert updated.json()['urgencia'] == 5

    deleted = api_client.delete(f'{API}/pedidos/{pedido_id}')
    assert deleted.status_code == 204
    assert api_client.get(f'{API}/pedidos/{pedido_id}').status_code == 404


def test_pedidos_paginan_filtran_y_ordenan(api_client: ApiClient) -> None:
    for index in range(3):
        payload = pedido_payload(f'PED-PAGE-{index}')
        payload['pedido']['urgencia'] = index + 1
        assert api_client.post(f'{API}/pedidos', json=payload).status_code == 201

    response = api_client.get(
        f'{API}/pedidos',
        params={
            'estado': 'pendiente',
            'page': 2,
            'page_size': 2,
            'sort_by': 'codigo',
            'sort_order': 'asc',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert (body['page'], body['page_size'], body['total'], body['total_pages']) == (2, 2, 3, 2)
    assert body['items'][0]['codigo'] == 'PED-PAGE-2'


def test_pedido_duplicado_revierte_cliente_y_ubicacion(
    api_client: ApiClient, db_session: Session
) -> None:
    create_pedido(api_client, 'PED-DUPLICADO')
    before = (
        db_session.scalar(select(func.count()).select_from(Cliente)),
        db_session.scalar(select(func.count()).select_from(Ubicacion)),
        db_session.scalar(select(func.count()).select_from(Pedido)),
    )
    response = api_client.post(f'{API}/pedidos', json=pedido_payload('PED-DUPLICADO'))
    assert response.status_code == 409
    assert response.json()['detail']['code'] == 'pedido_codigo_duplicado'
    assert 'SQLSTATE' not in response.text
    after = (
        db_session.scalar(select(func.count()).select_from(Cliente)),
        db_session.scalar(select(func.count()).select_from(Ubicacion)),
        db_session.scalar(select(func.count()).select_from(Pedido)),
    )
    assert after == before


def test_conductores_crud_filtros_y_duplicado(api_client: ApiClient) -> None:
    created = create_conductor(api_client, 'TJA-LIC-001')
    conductor_id = created['id_conductor']
    listing = api_client.get(
        f'{API}/conductores', params={'q': 'Mendoza', 'disponible': True}
    )
    assert listing.status_code == 200
    assert listing.json()['total'] == 1
    updated = api_client.patch(
        f'{API}/conductores/{conductor_id}',
        json={'nombre': 'Carlos A. Mendoza', 'disponible': False},
    )
    assert updated.status_code == 200
    assert updated.json()['disponible'] is False
    duplicate = api_client.post(
        f'{API}/conductores',
        json={'nombre': 'Otro', 'licencia': 'TJA-LIC-001', 'disponible': True},
    )
    assert duplicate.status_code == 409
    assert 'IntegrityError' not in duplicate.text
    assert api_client.delete(
        f'{API}/conductores/{conductor_id}'
    ).status_code == 204


def test_vehiculos_crud_filtros_duplicado_y_validacion(api_client: ApiClient) -> None:
    created = create_vehiculo(api_client, 'TJA-1001')
    vehiculo_id = created['id_vehiculo']
    listing = api_client.get(
        f'{API}/vehiculos', params={'q': 'TJA', 'capacidad_min': 900}
    )
    assert listing.status_code == 200
    assert listing.json()['total'] == 1
    updated = api_client.patch(
        f'{API}/vehiculos/{vehiculo_id}',
        json={'capacidad_kg': 1200, 'disponible': False},
    )
    assert updated.status_code == 200
    assert float(updated.json()['capacidad_kg']) == 1200
    invalid = api_client.post(
        f'{API}/vehiculos',
        json={
            'placa': 'TJA-BAD',
            'capacidad_kg': 0,
            'rendimiento_km_l': 10,
            'disponible': True,
        },
    )
    assert invalid.status_code == 422
    duplicate = api_client.post(
        f'{API}/vehiculos',
        json={
            'placa': 'TJA-1001',
            'capacidad_kg': 900,
            'rendimiento_km_l': 9,
            'disponible': True,
        },
    )
    assert duplicate.status_code == 409
    assert 'SQLSTATE' not in duplicate.text


def test_asignacion_valida_actualiza_recursos_y_es_consultable(
    api_client: ApiClient, db_session: Session
) -> None:
    pedido = create_pedido(api_client, 'PED-ASIGNAR', 250)
    conductor = create_conductor(api_client, 'LIC-ASIGNAR')
    vehiculo = create_vehiculo(api_client, 'TJA-ASG', 500)
    response = api_client.post(
        f'{API}/asignaciones',
        json={
            'id_pedido': pedido['id_pedido'],
            'id_conductor': conductor['id_conductor'],
            'id_vehiculo': vehiculo['id_vehiculo'],
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    asignacion_id = body['id_asignacion']
    assert body['estado'] == 'asignada'
    assert body['pedido']['codigo'] == 'PED-ASIGNAR'
    db_session.expire_all()
    assert db_session.get(Pedido, pedido['id_pedido']).estado == 'asignado'
    assert db_session.get(Conductor, conductor['id_conductor']).disponible is False
    assert db_session.get(Vehiculo, vehiculo['id_vehiculo']).disponible is False
    assert api_client.get(f'{API}/asignaciones', params={'q': 'PED-ASIGNAR'}).json()['total'] == 1
    assert api_client.get(
        f'{API}/asignaciones/{asignacion_id}'
    ).status_code == 200


@pytest.mark.parametrize('unavailable', ['conductor', 'vehiculo'])
def test_asignacion_rechaza_recursos_no_disponibles(
    api_client: ApiClient, unavailable: str
) -> None:
    pedido = create_pedido(api_client, f'PED-NO-{unavailable}')
    conductor = create_conductor(
        api_client, f'LIC-{unavailable}', unavailable != 'conductor'
    )
    vehiculo = create_vehiculo(
        api_client, f'PL-{unavailable}', 1000, unavailable != 'vehiculo'
    )
    response = api_client.post(
        f'{API}/asignaciones',
        json={
            'id_pedido': pedido['id_pedido'],
            'id_conductor': conductor['id_conductor'],
            'id_vehiculo': vehiculo['id_vehiculo'],
        },
    )
    assert response.status_code == 409
    assert 'disponible' in response.json()['detail']['message'].lower()


def test_asignacion_rechaza_capacidad_sin_efectos_parciales(
    api_client: ApiClient, db_session: Session
) -> None:
    pedido = create_pedido(api_client, 'PED-PESADO', 900)
    conductor = create_conductor(api_client, 'LIC-PESADO')
    vehiculo = create_vehiculo(api_client, 'PL-PESADO', 200)
    response = api_client.post(
        f'{API}/asignaciones',
        json={
            'id_pedido': pedido['id_pedido'],
            'id_conductor': conductor['id_conductor'],
            'id_vehiculo': vehiculo['id_vehiculo'],
        },
    )
    assert response.status_code == 409
    assert response.json()['detail']['code'] == 'capacidad_insuficiente'
    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(Asignacion)) == 0
    assert db_session.get(Pedido, pedido['id_pedido']).estado == 'pendiente'
    assert db_session.get(Conductor, conductor['id_conductor']).disponible is True


def test_cancelar_asignacion_libera_recursos(api_client: ApiClient) -> None:
    pedido = create_pedido(api_client, 'PED-CANCELAR')
    conductor = create_conductor(api_client, 'LIC-CANCELAR')
    vehiculo = create_vehiculo(api_client, 'PL-CANCELAR')
    assigned = api_client.post(
        f'{API}/asignaciones',
        json={
            'id_pedido': pedido['id_pedido'],
            'id_conductor': conductor['id_conductor'],
            'id_vehiculo': vehiculo['id_vehiculo'],
        },
    ).json()
    asignacion_id = assigned['id_asignacion']
    conductor_id = conductor['id_conductor']
    vehiculo_id = vehiculo['id_vehiculo']
    pedido_id = pedido['id_pedido']
    response = api_client.patch(
        f'{API}/asignaciones/{asignacion_id}',
        json={'estado': 'cancelada'},
    )
    assert response.status_code == 200
    assert api_client.get(
        f'{API}/conductores/{conductor_id}'
    ).json()['disponible'] is True
    assert api_client.get(
        f'{API}/vehiculos/{vehiculo_id}'
    ).json()['disponible'] is True
    assert api_client.get(f'{API}/pedidos/{pedido_id}').json()['estado'] == 'pendiente'


def test_asignacion_cancelada_puede_eliminarse_y_limpia_recursos(
    api_client: ApiClient,
) -> None:
    pedido = create_pedido(api_client, 'PED-ELIMINAR-ASG')
    conductor = create_conductor(api_client, 'LIC-ELIMINAR-ASG')
    vehiculo = create_vehiculo(api_client, 'PL-ELIMINAR-ASG')
    assigned = api_client.post(
        f'{API}/asignaciones',
        json={
            'id_pedido': pedido['id_pedido'],
            'id_conductor': conductor['id_conductor'],
            'id_vehiculo': vehiculo['id_vehiculo'],
        },
    ).json()
    asignacion_id = assigned['id_asignacion']
    pedido_id = pedido['id_pedido']
    conductor_id = conductor['id_conductor']
    vehiculo_id = vehiculo['id_vehiculo']
    endpoint = f'{API}/asignaciones/{asignacion_id}'

    active_delete = api_client.delete(endpoint)
    assert active_delete.status_code == 409
    assert active_delete.json()['detail']['code'] == 'asignacion_no_eliminable'
    assert api_client.patch(endpoint, json={'estado': 'cancelada'}).status_code == 200
    assert api_client.delete(endpoint).status_code == 204
    assert api_client.get(endpoint).status_code == 404

    assert api_client.delete(f'{API}/pedidos/{pedido_id}').status_code == 204
    assert api_client.delete(
        f'{API}/conductores/{conductor_id}'
    ).status_code == 204
    assert api_client.delete(f'{API}/vehiculos/{vehiculo_id}').status_code == 204


def test_resumen_operacional_procede_de_postgresql(api_client: ApiClient) -> None:
    create_pedido(api_client, 'PED-RESUMEN')
    create_conductor(api_client, 'LIC-RESUMEN')
    create_vehiculo(api_client, 'PL-RESUMEN')
    response = api_client.get(f'{API}/operacion/resumen')
    assert response.status_code == 200
    body = response.json()
    assert body['pedidos_registrados'] == 1
    assert body['pedidos_pendientes'] == 1
    assert body['conductores_disponibles'] == 1
    assert body['vehiculos_disponibles'] == 1
    assert body['actividad_reciente'][0]['titulo'] == 'PED-RESUMEN'


def test_recursos_inexistentes_devuelven_404(api_client: ApiClient) -> None:
    assert api_client.get(f'{API}/pedidos/999999').status_code == 404
    assert api_client.get(f'{API}/conductores/999999').status_code == 404
    assert api_client.get(f'{API}/vehiculos/999999').status_code == 404
    assert api_client.get(f'{API}/asignaciones/999999').status_code == 404
