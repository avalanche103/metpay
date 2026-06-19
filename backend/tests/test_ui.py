from fastapi.testclient import TestClient


def test_payments_ui_loads(client: TestClient) -> None:
    response = client.get("/payments-ui")

    assert response.status_code == 200
    assert "Поступившие платежи" in response.text
    assert "/api/payments" in response.text


def test_index_redirects_to_payments_ui(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code in {307, 308}
    assert response.headers["location"] == "/payments-ui"
