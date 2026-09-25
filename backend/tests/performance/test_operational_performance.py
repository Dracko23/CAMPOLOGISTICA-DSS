from __future__ import annotations

import math
from datetime import datetime, timedelta
from decimal import Decimal
from time import perf_counter

from sqlalchemy.orm import Session

from app.models import Cliente, Pedido, Ubicacion
from tests.conftest import ApiClient


API = '/api/v1'
SAMPLE_COUNT = 20
P95_LIMIT_SECONDS = 2.0


def _seed_one_thousand_orders(session: Session) -> None:
    cliente = Cliente(
        nombre='Cliente Performance PostgreSQL',
        telefono='72901000',
        email='performance@example.test',
    )
    ubicacion = Ubicacion(
        direccion='Av. Las Americas 1000',
        zona='Tarija Centro',
        latitud=Decimal('-21.535500'),
        longitud=Decimal('-64.729600'),
    )
    session.add_all([cliente, ubicacion])
    session.flush()

    base_time = datetime(2026, 9, 23, 8, 0)
    session.add_all(
        [
            Pedido(
                id_cliente=cliente.id_cliente,
                id_ubicacion=ubicacion.id_ubicacion,
                codigo=f'PERF-{index:04d}',
                fecha_registro=base_time + timedelta(seconds=index),
                fecha_limite=base_time + timedelta(days=1, seconds=index),
                peso_kg=Decimal('25.50'),
                urgencia=(index % 5) + 1,
                estado='pendiente',
            )
            for index in range(1000)
        ]
    )
    session.flush()


def _percentile_95(samples: list[float]) -> float:
    ordered = sorted(samples)
    return ordered[math.ceil(len(ordered) * 0.95) - 1]


def test_listado_paginado_con_mil_pedidos_cumple_p95(
    api_client: ApiClient,
    db_session: Session,
) -> None:
    _seed_one_thousand_orders(db_session)
    params = {
        'q': 'PERF-',
        'estado': 'pendiente',
        'page': 5,
        'page_size': 100,
        'sort_by': 'codigo',
        'sort_order': 'asc',
    }

    warmup = api_client.get(f'{API}/pedidos', params=params)
    assert warmup.status_code == 200, warmup.text
    assert warmup.json()['total'] == 1000

    elapsed_samples: list[float] = []
    for _ in range(SAMPLE_COUNT):
        started_at = perf_counter()
        response = api_client.get(f'{API}/pedidos', params=params)
        elapsed_samples.append(perf_counter() - started_at)
        assert response.status_code == 200, response.text
        body = response.json()
        assert len(body['items']) == 100
        assert body['total'] == 1000
        assert body['page'] == 5
        assert body['total_pages'] == 10

    p95_seconds = _percentile_95(elapsed_samples)
    print(
        f'operational_list_1000 p95={p95_seconds:.4f}s '
        f'samples={SAMPLE_COUNT} database=postgresql'
    )
    assert p95_seconds < P95_LIMIT_SECONDS, (
        f'El p95 del listado fue {p95_seconds:.4f}s; '
        f'el limite es {P95_LIMIT_SECONDS:.1f}s.'
    )
