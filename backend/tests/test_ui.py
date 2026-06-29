from fastapi.testclient import TestClient


def test_payments_ui_loads(client: TestClient) -> None:
    response = client.get("/payments-ui")

    assert response.status_code == 200
    assert "Поступившие платежи" in response.text
    assert "/api/payments" in response.text
    assert "Группа" in response.text
    assert "Изменить" in response.text
    assert "/groups-ui" in response.text
    assert "Оплата" in response.text
    assert 'data-sort="student"' in response.text
    assert 'class="sortable"' in response.text
    assert "/students-ui/" in response.text


def test_student_payments_ui_loads(client: TestClient) -> None:
    student = client.post("/api/students", json={"full_name": "Ссылочный Ученик"}).json()
    response = client.get(f"/students-ui/{student['id']}")

    assert response.status_code == 200
    assert "Оплата" in response.text
    assert "/api/payments/payment-for-options" in response.text
    assert "/api/students/" in response.text


def test_groups_ui_loads(client: TestClient) -> None:
    response = client.get("/groups-ui")

    assert response.status_code == 200
    assert "Группы" in response.text
    assert "/api/groups" in response.text
    assert "/students-ui/" in response.text
    assert "student-link" in response.text
    assert "/payments-ui" in response.text


def test_index_redirects_to_payments_ui(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)

    assert response.status_code in {307, 308}
    assert response.headers["location"] == "/payments-ui"
