from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
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
from tests.factories import (
    BASE_TIME,
    persist_alternativa,
    persist_asignacion,
    persist_cliente,
    persist_conductor,
    persist_evaluacion,
    persist_pedido,
    persist_ubicacion,
    persist_vehiculo,
)


def assert_integrity_error(
    session: Session,
    *,
    sqlstate: str,
    constraint_name: str,
) -> None:
    with pytest.raises(IntegrityError) as captured:
        session.flush()
    assert captured.value.orig.sqlstate == sqlstate
    assert captured.value.orig.diag.constraint_name == constraint_name
    session.rollback()


def test_01_cliente_valido_persiste(db_session: Session) -> None:
    entity = persist_cliente(db_session, "01")
    entity_id = entity.id_cliente
    db_session.expunge_all()
    assert db_session.get(Cliente, entity_id).nombre == "Cliente 01"


def test_02_ubicacion_valida_persiste(db_session: Session) -> None:
    entity = persist_ubicacion(db_session, "02")
    entity_id = entity.id_ubicacion
    db_session.expunge_all()
    assert db_session.get(Ubicacion, entity_id).zona == "Tarija Centro"


def test_03_pedido_valido_persiste(db_session: Session) -> None:
    entity = persist_pedido(db_session, "03")
    entity_id = entity.id_pedido
    db_session.expunge_all()
    persisted = db_session.get(Pedido, entity_id)
    assert persisted.codigo == "PED-03"
    assert persisted.cliente.nombre == "Cliente 03"
    assert persisted.ubicacion.zona == "Tarija Centro"


def test_04_conductor_valido_persiste(db_session: Session) -> None:
    entity = persist_conductor(db_session, "04")
    entity_id = entity.id_conductor
    db_session.expunge_all()
    assert db_session.get(Conductor, entity_id).licencia == "LIC-04"


def test_05_vehiculo_valido_persiste(db_session: Session) -> None:
    entity = persist_vehiculo(db_session, "05")
    entity_id = entity.id_vehiculo
    db_session.expunge_all()
    assert db_session.get(Vehiculo, entity_id).placa == "TJA-05"


def test_06_asignacion_valida_persiste(db_session: Session) -> None:
    entity = persist_asignacion(db_session, "06")
    entity_id = entity.id_asignacion
    db_session.expunge_all()
    persisted = db_session.get(Asignacion, entity_id)
    assert persisted.pedido.codigo == "PED-06"
    assert persisted.conductor.licencia == "LIC-06"
    assert persisted.vehiculo.placa == "TJA-06"


def test_07_evaluacion_dss_persiste(db_session: Session) -> None:
    entity = persist_evaluacion(db_session, "07")
    entity_id = entity.id_evaluacion
    db_session.expunge_all()
    persisted = db_session.get(EvaluacionDSS, entity_id)
    assert persisted.indice_prioridad == Decimal("72.50")
    assert persisted.pedido.codigo == "PED-07"


def test_08_alternativa_persiste_y_conserva_trazabilidad(
    db_session: Session,
) -> None:
    entity = persist_alternativa(db_session, "08")
    evaluation_id = entity.id_evaluacion
    db_session.expunge_all()
    evaluation = db_session.get(EvaluacionDSS, evaluation_id)
    assert evaluation.pedido.codigo == "PED-08"
    assert len(evaluation.alternativas) == 1
    assert evaluation.alternativas[0].conductor.licencia == "LIC-08"
    assert evaluation.alternativas[0].vehiculo.placa == "TJA-08"


def test_09_peso_cero_rechazado(db_session: Session) -> None:
    cliente = persist_cliente(db_session, "09")
    ubicacion = persist_ubicacion(db_session, "09")
    db_session.add(
        Pedido(
            id_cliente=cliente.id_cliente,
            id_ubicacion=ubicacion.id_ubicacion,
            codigo="PED-09",
            fecha_registro=BASE_TIME,
            fecha_limite=BASE_TIME,
            peso_kg=Decimal("0"),
            urgencia=3,
            estado="registrado",
        )
    )
    assert_integrity_error(
        db_session,
        sqlstate="23514",
        constraint_name="ck_pedido_peso_kg_positivo",
    )


def test_10_peso_negativo_rechazado(db_session: Session) -> None:
    cliente = persist_cliente(db_session, "10")
    ubicacion = persist_ubicacion(db_session, "10")
    db_session.add(
        Pedido(
            id_cliente=cliente.id_cliente,
            id_ubicacion=ubicacion.id_ubicacion,
            codigo="PED-10",
            fecha_registro=BASE_TIME,
            fecha_limite=BASE_TIME,
            peso_kg=Decimal("-0.01"),
            urgencia=3,
            estado="registrado",
        )
    )
    assert_integrity_error(
        db_session,
        sqlstate="23514",
        constraint_name="ck_pedido_peso_kg_positivo",
    )


def test_11_urgencia_cero_rechazada(db_session: Session) -> None:
    cliente = persist_cliente(db_session, "11")
    ubicacion = persist_ubicacion(db_session, "11")
    db_session.add(
        Pedido(
            id_cliente=cliente.id_cliente,
            id_ubicacion=ubicacion.id_ubicacion,
            codigo="PED-11",
            fecha_registro=BASE_TIME,
            fecha_limite=BASE_TIME,
            peso_kg=Decimal("1"),
            urgencia=0,
            estado="registrado",
        )
    )
    assert_integrity_error(
        db_session,
        sqlstate="23514",
        constraint_name="ck_pedido_urgencia_rango",
    )


def test_12_urgencia_seis_rechazada(db_session: Session) -> None:
    cliente = persist_cliente(db_session, "12")
    ubicacion = persist_ubicacion(db_session, "12")
    db_session.add(
        Pedido(
            id_cliente=cliente.id_cliente,
            id_ubicacion=ubicacion.id_ubicacion,
            codigo="PED-12",
            fecha_registro=BASE_TIME,
            fecha_limite=BASE_TIME,
            peso_kg=Decimal("1"),
            urgencia=6,
            estado="registrado",
        )
    )
    assert_integrity_error(
        db_session,
        sqlstate="23514",
        constraint_name="ck_pedido_urgencia_rango",
    )


def test_13_codigo_pedido_duplicado_rechazado(db_session: Session) -> None:
    first = persist_pedido(db_session, "13")
    db_session.add(
        Pedido(
            id_cliente=first.id_cliente,
            id_ubicacion=first.id_ubicacion,
            codigo=first.codigo,
            fecha_registro=BASE_TIME,
            fecha_limite=BASE_TIME,
            peso_kg=Decimal("2"),
            urgencia=2,
            estado="registrado",
        )
    )
    assert_integrity_error(
        db_session, sqlstate="23505", constraint_name="uq_pedido_codigo"
    )


def test_14_licencia_duplicada_rechazada(db_session: Session) -> None:
    first = persist_conductor(db_session, "14")
    db_session.add(
        Conductor(nombre="Otro conductor", licencia=first.licencia, disponible=True)
    )
    assert_integrity_error(
        db_session, sqlstate="23505", constraint_name="uq_conductor_licencia"
    )


def test_15_placa_duplicada_rechazada(db_session: Session) -> None:
    first = persist_vehiculo(db_session, "15")
    db_session.add(
        Vehiculo(
            placa=first.placa,
            capacidad_kg=Decimal("800"),
            rendimiento_km_l=Decimal("9"),
            disponible=True,
        )
    )
    assert_integrity_error(
        db_session, sqlstate="23505", constraint_name="uq_vehiculo_placa"
    )


def test_16_capacidad_no_positiva_rechazada(db_session: Session) -> None:
    for index, value in enumerate((Decimal("0"), Decimal("-1"))):
        db_session.add(
            Vehiculo(
                placa=f"CAP-{index}",
                capacidad_kg=value,
                rendimiento_km_l=Decimal("10"),
                disponible=True,
            )
        )
        assert_integrity_error(
            db_session,
            sqlstate="23514",
            constraint_name="ck_vehiculo_capacidad_kg_positiva",
        )


def test_17_rendimiento_no_positivo_rechazado(db_session: Session) -> None:
    for index, value in enumerate((Decimal("0"), Decimal("-1"))):
        db_session.add(
            Vehiculo(
                placa=f"REN-{index}",
                capacidad_kg=Decimal("100"),
                rendimiento_km_l=value,
                disponible=True,
            )
        )
        assert_integrity_error(
            db_session,
            sqlstate="23514",
            constraint_name="ck_vehiculo_rendimiento_km_l_positivo",
        )


def test_18_fk_pedido_inexistente_rechazada(db_session: Session) -> None:
    conductor = persist_conductor(db_session, "18")
    vehiculo = persist_vehiculo(db_session, "18")
    db_session.add(
        Asignacion(
            id_pedido=9_999_991,
            id_conductor=conductor.id_conductor,
            id_vehiculo=vehiculo.id_vehiculo,
            fecha_asignacion=BASE_TIME,
            estado="asignada",
        )
    )
    assert_integrity_error(
        db_session,
        sqlstate="23503",
        constraint_name="fk_asignacion_id_pedido",
    )


def test_19_fk_conductor_inexistente_rechazada(db_session: Session) -> None:
    pedido = persist_pedido(db_session, "19")
    vehiculo = persist_vehiculo(db_session, "19")
    db_session.add(
        Asignacion(
            id_pedido=pedido.id_pedido,
            id_conductor=9_999_992,
            id_vehiculo=vehiculo.id_vehiculo,
            fecha_asignacion=BASE_TIME,
            estado="asignada",
        )
    )
    assert_integrity_error(
        db_session,
        sqlstate="23503",
        constraint_name="fk_asignacion_id_conductor",
    )


def test_20_fk_vehiculo_inexistente_rechazada(db_session: Session) -> None:
    pedido = persist_pedido(db_session, "20")
    conductor = persist_conductor(db_session, "20")
    db_session.add(
        Asignacion(
            id_pedido=pedido.id_pedido,
            id_conductor=conductor.id_conductor,
            id_vehiculo=9_999_993,
            fecha_asignacion=BASE_TIME,
            estado="asignada",
        )
    )
    assert_integrity_error(
        db_session,
        sqlstate="23503",
        constraint_name="fk_asignacion_id_vehiculo",
    )


@pytest.mark.parametrize(
    ("field", "constraint_name", "suffix"),
    [
        ("distancia_km", "ck_asignacion_distancia_km_no_negativa", "21d"),
        (
            "combustible_litros",
            "ck_asignacion_combustible_litros_no_negativo",
            "21l",
        ),
        (
            "costo_combustible",
            "ck_asignacion_costo_combustible_no_negativo",
            "21c",
        ),
    ],
)
def test_21_metricas_negativas_de_asignacion_rechazadas(
    db_session: Session,
    field: str,
    constraint_name: str,
    suffix: str,
) -> None:
    asignacion = persist_asignacion(db_session, suffix)
    setattr(asignacion, field, Decimal("-0.01"))
    assert_integrity_error(
        db_session,
        sqlstate="23514",
        constraint_name=constraint_name,
    )


@pytest.mark.parametrize(
    ("value", "suffix"),
    [(Decimal("-0.01"), "22low"), (Decimal("100.01"), "22high")],
)
def test_22_indice_prioridad_fuera_de_rango_rechazado(
    db_session: Session,
    value: Decimal,
    suffix: str,
) -> None:
    pedido = persist_pedido(db_session, suffix)
    db_session.add(
        EvaluacionDSS(
            id_pedido=pedido.id_pedido,
            fecha_evaluacion=BASE_TIME,
            indice_prioridad=value,
        )
    )
    assert_integrity_error(
        db_session,
        sqlstate="23514",
        constraint_name="ck_evaluacion_dss_indice_prioridad_rango",
    )
