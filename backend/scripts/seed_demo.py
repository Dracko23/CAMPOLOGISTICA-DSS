"""Carga datos ficticios de demostracion de forma idempotente.

Uso: python scripts/seed_demo.py [--reset]
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models import Usuario  # noqa: E402
from app.models.oltp import Asignacion, Cliente, Conductor, Pedido, Ubicacion, Vehiculo  # noqa: E402


CITIES = [
    ("Tarija", "Tarija", "Av. Las Americas 145", "San Geronimo", -21.5355, -64.7296),
    ("Sucre", "Chuquisaca", "Calle Destacamento 317", "Central", -19.0477, -65.2592),
    ("La Paz", "La Paz", "Av. Arce 2280", "Sopocachi", -16.5000, -68.1350),
    ("Santa Cruz", "Santa Cruz", "Av. Beni 3020", "Norte", -17.7539, -63.1812),
    ("Cochabamba", "Cochabamba", "Av. America Oeste 760", "Queru Queru", -17.3740, -66.1591),
]


def reset_demo(session) -> None:
    demo_ids = list(session.scalars(select(Pedido.id_pedido).where(Pedido.codigo.like("DEMO-%"))))
    client_ids = list(session.scalars(select(Pedido.id_cliente).where(Pedido.id_pedido.in_(demo_ids)))) if demo_ids else []
    location_ids = list(session.scalars(select(Pedido.id_ubicacion).where(Pedido.id_pedido.in_(demo_ids)))) if demo_ids else []
    if demo_ids:
        session.execute(delete(Asignacion).where(Asignacion.id_pedido.in_(demo_ids)))
        session.execute(delete(Pedido).where(Pedido.id_pedido.in_(demo_ids)))
    # Also delete any pedidos that reference the client_ids (to avoid FK violation)
    if client_ids:
        session.execute(delete(Pedido).where(Pedido.id_cliente.in_(client_ids)))
        session.execute(delete(Cliente).where(Cliente.id_cliente.in_(client_ids)))
    if location_ids:
        session.execute(delete(Ubicacion).where(Ubicacion.id_ubicacion.in_(location_ids)))
    session.execute(delete(Conductor).where(Conductor.licencia.like("DEMO-%")))
    session.execute(delete(Vehiculo).where(Vehiculo.placa.like("DMO-%")))
    session.execute(delete(Usuario).where(Usuario.email.like("%demo@campologistica.bo")))
    session.commit()


def seed_demo(reset: bool = False) -> None:
    with SessionLocal() as session:
        if reset:
            reset_demo(session)
        if session.scalar(select(Pedido.id_pedido).where(Pedido.codigo == "DEMO-001")):
            print("Seed DEMO ya estaba cargado; no se duplicaron datos.")
            return

        clients = [Cliente(nombre=f"Cliente DEMO {name}", telefono=f"+591 70000{i:03d}", email=f"demo{i}@campo.test") for i, (name, *_rest) in enumerate(CITIES, 1)]
        drivers = [Conductor(nombre=name, licencia=f"DEMO-LIC-{i:02d}", disponible=i > 2) for i, name in enumerate(["Ana Flores DEMO", "Luis Rojas DEMO", "Maria Vega DEMO", "Carlos Paz DEMO"], 1)]
        vehicles = [Vehiculo(placa=f"DMO-{i}00", capacidad_kg=Decimal(capacity), rendimiento_km_l=Decimal(efficiency), disponible=i > 2) for i, (capacity, efficiency) in enumerate([(3500, 8.5), (1800, 10.2), (900, 12.4), (5000, 7.8)], 1)]
        session.add_all([*clients, *drivers, *vehicles])
        session.flush()

        # Create demo users
        demo_password = "Demo1234!"
        # Admin
        if not session.scalar(select(Usuario).where(Usuario.email == "admin.demo@campologistica.bo")):
            admin_user = Usuario(
                email="admin.demo@campologistica.bo",
                password_hash=hash_password(demo_password),
                rol="admin",
                nombre="Administrador DEMO",
                activo=True,
                id_conductor=None,
                id_cliente=None,
                fecha_creacion=datetime.now(),
            )
            session.add(admin_user)
        # Conductor users linked to drivers
        for i, driver in enumerate(drivers, 1):
            email = f"conductor{i}.demo@campologistica.bo"
            if not session.scalar(select(Usuario).where(Usuario.email == email)):
                conductor_user = Usuario(
                    email=email,
                    password_hash=hash_password(demo_password),
                    rol="conductor",
                    nombre=driver.nombre,
                    activo=True,
                    id_conductor=driver.id_conductor,
                    id_cliente=None,
                    fecha_creacion=datetime.now(),
                )
                session.add(conductor_user)
        # Client users linked to clients
        for i, client in enumerate(clients, 1):
            email = f"cliente{i}.demo@campologistica.bo"
            if not session.scalar(select(Usuario).where(Usuario.email == email)):
                client_user = Usuario(
                    email=email,
                    password_hash=hash_password(demo_password),
                    rol="cliente",
                    nombre=client.nombre,
                    activo=True,
                    id_conductor=None,
                    id_cliente=client.id_cliente,
                    fecha_creacion=datetime.now(),
                )
                session.add(client_user)
        session.flush()

        now = datetime.now()
        orders = []
        statuses = ["pendiente", "pendiente", "pendiente", "pendiente", "pendiente", "asignado", "pendiente", "en_camino", "entregado", "entregado"]
        weights = [120, 480, 750, 95, 1400, 260, 900, 1100, 300, 2100]
        for index in range(10):
            city, department, address, zone, lat, lon = CITIES[index % len(CITIES)]
            location = Ubicacion(direccion=f"{address} (DEMO)", zona=zone, ciudad=city, departamento=department, latitud=Decimal(str(lat)), longitud=Decimal(str(lon)))
            order = Pedido(id_cliente=clients[index % 5].id_cliente, ubicacion=location, codigo=f"DEMO-{index + 1:03d}", fecha_registro=now - timedelta(hours=10 - index), fecha_limite=now + timedelta(days=1 + index), peso_kg=Decimal(weights[index]), urgencia=(index % 5) + 1, estado=statuses[index])
            orders.append(order)
        session.add_all(orders)
        session.flush()

        assignments = [
            Asignacion(pedido=orders[5], conductor=drivers[0], vehiculo=vehicles[0], fecha_asignacion=now - timedelta(hours=3), estado="asignada"),
            Asignacion(pedido=orders[7], conductor=drivers[1], vehiculo=vehicles[1], fecha_asignacion=now - timedelta(hours=5), fecha_salida=now - timedelta(hours=2), estado="en_camino"),
            Asignacion(pedido=orders[8], conductor=drivers[2], vehiculo=vehicles[2], fecha_asignacion=now - timedelta(days=2), fecha_salida=now - timedelta(days=1, hours=4), fecha_entrega=now - timedelta(days=1), estado="entregada"),
            Asignacion(pedido=orders[9], conductor=drivers[3], vehiculo=vehicles[3], fecha_asignacion=now - timedelta(days=3), fecha_salida=now - timedelta(days=2, hours=3), fecha_entrega=now - timedelta(days=2), estado="entregada"),
        ]
        session.add_all(assignments)
        session.commit()
        print("Seed DEMO listo: 5 clientes, 4 conductores, 4 vehiculos, 10 pedidos y 4 asignaciones.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reemplaza solamente los datos DEMO")
    seed_demo(parser.parse_args().reset)
