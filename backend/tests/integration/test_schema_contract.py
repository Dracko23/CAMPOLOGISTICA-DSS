from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Engine,
    Numeric,
    SmallInteger,
    String,
    inspect,
)

from app.db.base import Base
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


TABLES = {
    "cliente",
    "ubicacion",
    "pedido",
    "conductor",
    "vehiculo",
    "asignacion",
    "evaluacion_dss",
    "alternativa",
}
PRIMARY_KEYS = {f"pk_{table}" for table in TABLES}
FOREIGN_KEYS = {
    "fk_pedido_id_cliente",
    "fk_pedido_id_ubicacion",
    "fk_asignacion_id_pedido",
    "fk_asignacion_id_conductor",
    "fk_asignacion_id_vehiculo",
    "fk_evaluacion_dss_id_pedido",
    "fk_alternativa_id_evaluacion",
    "fk_alternativa_id_conductor",
    "fk_alternativa_id_vehiculo",
}
UNIQUE_CONSTRAINTS = {
    "uq_pedido_codigo",
    "uq_conductor_licencia",
    "uq_vehiculo_placa",
}
CHECK_CONSTRAINTS = {
    "ck_pedido_peso_kg_positivo",
    "ck_pedido_urgencia_rango",
    "ck_vehiculo_capacidad_kg_positiva",
    "ck_vehiculo_rendimiento_km_l_positivo",
    "ck_asignacion_distancia_km_no_negativa",
    "ck_asignacion_combustible_litros_no_negativo",
    "ck_asignacion_costo_combustible_no_negativo",
    "ck_evaluacion_dss_indice_prioridad_rango",
}
FOREIGN_KEY_TARGETS = {
    "fk_pedido_id_cliente": (("id_cliente",), "cliente", ("id_cliente",)),
    "fk_pedido_id_ubicacion": (("id_ubicacion",), "ubicacion", ("id_ubicacion",)),
    "fk_asignacion_id_pedido": (("id_pedido",), "pedido", ("id_pedido",)),
    "fk_asignacion_id_conductor": (
        ("id_conductor",),
        "conductor",
        ("id_conductor",),
    ),
    "fk_asignacion_id_vehiculo": (("id_vehiculo",), "vehiculo", ("id_vehiculo",)),
    "fk_evaluacion_dss_id_pedido": (("id_pedido",), "pedido", ("id_pedido",)),
    "fk_alternativa_id_evaluacion": (
        ("id_evaluacion",),
        "evaluacion_dss",
        ("id_evaluacion",),
    ),
    "fk_alternativa_id_conductor": (
        ("id_conductor",),
        "conductor",
        ("id_conductor",),
    ),
    "fk_alternativa_id_vehiculo": (
        ("id_vehiculo",),
        "vehiculo",
        ("id_vehiculo",),
    ),
}
EXPECTED_COLUMNS = {
    "cliente": {"id_cliente", "nombre", "telefono", "email"},
    "ubicacion": {"id_ubicacion", "direccion", "zona", "latitud", "longitud"},
    "pedido": {
        "id_pedido",
        "id_cliente",
        "id_ubicacion",
        "codigo",
        "fecha_registro",
        "fecha_limite",
        "peso_kg",
        "urgencia",
        "estado",
    },
    "conductor": {"id_conductor", "nombre", "licencia", "disponible"},
    "vehiculo": {
        "id_vehiculo",
        "placa",
        "capacidad_kg",
        "rendimiento_km_l",
        "disponible",
    },
    "asignacion": {
        "id_asignacion",
        "id_pedido",
        "id_conductor",
        "id_vehiculo",
        "fecha_asignacion",
        "fecha_salida",
        "fecha_entrega",
        "distancia_km",
        "combustible_litros",
        "costo_combustible",
        "estado",
    },
    "evaluacion_dss": {
        "id_evaluacion",
        "id_pedido",
        "fecha_evaluacion",
        "indice_prioridad",
    },
    "alternativa": {
        "id_alternativa",
        "id_evaluacion",
        "id_conductor",
        "id_vehiculo",
        "distancia_estimada_km",
        "combustible_estimado_l",
        "riesgo_retraso",
        "puntuacion",
        "valida",
        "recomendada",
    },
}
NOT_NULL_COLUMNS = {
    "cliente": {"id_cliente", "nombre"},
    "ubicacion": {"id_ubicacion", "direccion", "zona"},
    "pedido": {"id_pedido", "fecha_registro", "fecha_limite", "estado"},
    "conductor": {"id_conductor", "nombre", "disponible"},
    "vehiculo": {"id_vehiculo", "disponible"},
    "asignacion": {"id_asignacion", "fecha_asignacion", "estado"},
    "evaluacion_dss": {"id_evaluacion", "fecha_evaluacion"},
    "alternativa": {"id_alternativa"},
}
STRING_LENGTHS = {
    ("cliente", "nombre"): 120,
    ("cliente", "telefono"): 30,
    ("cliente", "email"): 150,
    ("ubicacion", "direccion"): 200,
    ("ubicacion", "zona"): 80,
    ("pedido", "codigo"): 30,
    ("pedido", "estado"): 30,
    ("conductor", "nombre"): 120,
    ("conductor", "licencia"): 40,
    ("vehiculo", "placa"): 20,
    ("asignacion", "estado"): 30,
}
NUMERIC_SPECS = {
    ("ubicacion", "latitud"): (9, 6),
    ("ubicacion", "longitud"): (9, 6),
    ("pedido", "peso_kg"): (10, 2),
    ("vehiculo", "capacidad_kg"): (10, 2),
    ("vehiculo", "rendimiento_km_l"): (8, 2),
    ("asignacion", "distancia_km"): (10, 2),
    ("asignacion", "combustible_litros"): (10, 2),
    ("asignacion", "costo_combustible"): (12, 2),
    ("evaluacion_dss", "indice_prioridad"): (5, 2),
    ("alternativa", "distancia_estimada_km"): (10, 2),
    ("alternativa", "combustible_estimado_l"): (10, 2),
    ("alternativa", "riesgo_retraso"): (5, 2),
    ("alternativa", "puntuacion"): (5, 2),
}
DATETIME_COLUMNS = {
    ("pedido", "fecha_registro"),
    ("pedido", "fecha_limite"),
    ("asignacion", "fecha_asignacion"),
    ("asignacion", "fecha_salida"),
    ("asignacion", "fecha_entrega"),
    ("evaluacion_dss", "fecha_evaluacion"),
}
BOOLEAN_COLUMNS = {
    ("conductor", "disponible"),
    ("vehiculo", "disponible"),
    ("alternativa", "valida"),
    ("alternativa", "recomendada"),
}


def test_metadata_contiene_modelo_oltp_y_relaciones() -> None:
    assert set(Base.metadata.tables) == {f"oltp.{table}" for table in TABLES}
    expected_relationships = {
        Cliente: {"pedidos"},
        Ubicacion: {"pedidos"},
        Pedido: {"cliente", "ubicacion", "asignaciones", "evaluaciones_dss"},
        Conductor: {"asignaciones", "alternativas"},
        Vehiculo: {"asignaciones", "alternativas"},
        Asignacion: {"pedido", "conductor", "vehiculo"},
        EvaluacionDSS: {"pedido", "alternativas"},
        Alternativa: {"evaluacion", "conductor", "vehiculo"},
    }
    for model, relationships in expected_relationships.items():
        assert set(inspect(model).relationships.keys()) == relationships


def test_postgresql_contiene_constraints_e_indices_reales(pg_engine: Engine) -> None:
    inspector = inspect(pg_engine)
    assert "oltp" in inspector.get_schema_names()
    assert set(inspector.get_table_names(schema="oltp")) == TABLES

    primary_keys = set()
    foreign_keys = {}
    unique_constraints = set()
    check_constraints = set()
    indexes = set()
    for table in TABLES:
        primary_keys.add(inspector.get_pk_constraint(table, schema="oltp")["name"])
        for constraint in inspector.get_foreign_keys(table, schema="oltp"):
            foreign_keys[constraint["name"]] = (
                tuple(constraint["constrained_columns"]),
                constraint["referred_table"],
                tuple(constraint["referred_columns"]),
            )
        unique_constraints.update(
            constraint["name"]
            for constraint in inspector.get_unique_constraints(table, schema="oltp")
        )
        check_constraints.update(
            constraint["name"]
            for constraint in inspector.get_check_constraints(table, schema="oltp")
        )
        indexes.update(
            (index["name"], tuple(index["column_names"]))
            for index in inspector.get_indexes(table, schema="oltp")
        )

    assert primary_keys == PRIMARY_KEYS
    assert set(foreign_keys) == FOREIGN_KEYS
    assert foreign_keys == FOREIGN_KEY_TARGETS
    assert unique_constraints == UNIQUE_CONSTRAINTS
    assert check_constraints == CHECK_CONSTRAINTS
    assert {
        (name.replace("fk_", "ix_", 1), columns)
        for name, (columns, _, _) in FOREIGN_KEY_TARGETS.items()
    } <= indexes


def test_postgresql_respeta_columnas_tipos_y_nullability(pg_engine: Engine) -> None:
    inspector = inspect(pg_engine)
    primary_key_columns = {
        "cliente": {"id_cliente"},
        "ubicacion": {"id_ubicacion"},
        "pedido": {"id_pedido"},
        "conductor": {"id_conductor"},
        "vehiculo": {"id_vehiculo"},
        "asignacion": {"id_asignacion"},
        "evaluacion_dss": {"id_evaluacion"},
        "alternativa": {"id_alternativa"},
    }
    foreign_key_columns = {
        "pedido": {"id_cliente", "id_ubicacion"},
        "asignacion": {"id_pedido", "id_conductor", "id_vehiculo"},
        "evaluacion_dss": {"id_pedido"},
        "alternativa": {"id_evaluacion", "id_conductor", "id_vehiculo"},
    }

    for table in TABLES:
        columns = {
            column["name"]: column
            for column in inspector.get_columns(table, schema="oltp")
        }
        assert set(columns) == EXPECTED_COLUMNS[table]
        assert {
            name for name, column in columns.items() if not column["nullable"]
        } == NOT_NULL_COLUMNS[table]
        for column_name in primary_key_columns[table]:
            assert isinstance(columns[column_name]["type"], BigInteger)
            default = columns[column_name]["default"]
            assert (
                isinstance(default, str) and default.startswith("nextval(")
            ) or columns[column_name].get("identity") is not None
        for column_name in foreign_key_columns.get(table, set()):
            assert isinstance(columns[column_name]["type"], BigInteger)

    for (table, column_name), length in STRING_LENGTHS.items():
        column_type = {
            column["name"]: column["type"]
            for column in inspector.get_columns(table, schema="oltp")
        }[column_name]
        assert isinstance(column_type, String)
        assert column_type.length == length

    for (table, column_name), (precision, scale) in NUMERIC_SPECS.items():
        column_type = {
            column["name"]: column["type"]
            for column in inspector.get_columns(table, schema="oltp")
        }[column_name]
        assert isinstance(column_type, Numeric)
        assert (column_type.precision, column_type.scale) == (precision, scale)

    for table, column_name in DATETIME_COLUMNS:
        column_type = {
            column["name"]: column["type"]
            for column in inspector.get_columns(table, schema="oltp")
        }[column_name]
        assert isinstance(column_type, DateTime)
        assert column_type.timezone is False

    for table, column_name in BOOLEAN_COLUMNS:
        column_type = {
            column["name"]: column["type"]
            for column in inspector.get_columns(table, schema="oltp")
        }[column_name]
        assert isinstance(column_type, Boolean)

    urgency_type = {
        column["name"]: column["type"]
        for column in inspector.get_columns("pedido", schema="oltp")
    }["urgencia"]
    assert isinstance(urgency_type, SmallInteger)
