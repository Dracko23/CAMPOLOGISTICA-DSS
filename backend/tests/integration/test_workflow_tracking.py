from tests.conftest import ApiClient
from tests.integration.test_operational_api import create_conductor, create_pedido, create_vehiculo

API = "/api/v1"


def test_driver_state_machine_requires_every_step(api_client: ApiClient) -> None:
    order = create_pedido(api_client, "PED-STATE-MACHINE", 100)
    driver = create_conductor(api_client, "STATE-LIC-01")
    vehicle = create_vehiculo(api_client, "STA-100", 500)
    created = api_client.post(f"{API}/asignaciones", json={"id_pedido": order["id_pedido"], "id_conductor": driver["id_conductor"], "id_vehiculo": vehicle["id_vehiculo"]})
    assert created.status_code == 201
    assignment_id = created.json()["id_asignacion"]
    invalid = api_client.patch(f"{API}/asignaciones/{assignment_id}", json={"estado": "entregada"})
    assert invalid.status_code == 409
    for state in ("aceptada", "en_camino", "llegue", "entregada"):
        response = api_client.patch(f"{API}/asignaciones/{assignment_id}", json={"estado": state})
        assert response.status_code == 200, response.text
        assert response.json()["estado"] == state
    result = response.json()
    assert result["fecha_aceptacion"]
    assert result["fecha_salida"]
    assert result["fecha_llegada"]
    assert result["fecha_entrega"]
