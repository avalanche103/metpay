from decimal import Decimal

from fastapi.testclient import TestClient


def _create_group(client: TestClient, name: str = "2016", fee: str = "120.00") -> dict:
    response = client.post(
        "/api/groups",
        json={"name": name, "monthly_fee": fee},
    )
    assert response.status_code == 201
    return response.json()


def test_no_legacy_default_groups(client: TestClient) -> None:
    response = client.get("/api/groups")

    assert response.status_code == 200
    names = {group["name"] for group in response.json()}
    assert "2012" not in names
    assert "2013" not in names
    assert "2014+" not in names


def test_group_can_be_updated(client: TestClient) -> None:
    group = _create_group(client, name="2017", fee="120.00")

    response = client.patch(
        f"/api/groups/{group['id']}",
        json={"name": "2017-2018", "monthly_fee": "130.00", "active": False},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "2017-2018"
    assert Decimal(payload["monthly_fee"]) == Decimal("130.00")
    assert payload["active"] is False


def test_group_update_rejects_duplicate_name(client: TestClient) -> None:
    first = _create_group(client, name="Группа А")
    second = _create_group(client, name="Группа Б")

    response = client.patch(
        f"/api/groups/{second['id']}",
        json={"name": first["name"]},
    )

    assert response.status_code == 409


def test_group_can_be_created(client: TestClient) -> None:
    response = client.post(
        "/api/groups",
        json={"name": "2016", "monthly_fee": "125.00"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "2016"
    assert Decimal(response.json()["monthly_fee"]) == Decimal("125.00")


def test_student_group_can_be_assigned_from_api(client: TestClient) -> None:
    group = _create_group(client, name="2018")

    student = client.post(
        "/api/students",
        json={"full_name": "Тестов Ученик Тестович"},
    ).json()

    response = client.patch(
        f"/api/students/{student['id']}",
        json={"group_id": group["id"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["group_id"] == group["id"]
    assert payload["group_name"] == "2018"


def test_student_full_name_can_be_updated(client: TestClient) -> None:
    student = client.post(
        "/api/students",
        json={"full_name": "иванов иван иванович"},
    ).json()

    response = client.patch(
        f"/api/students/{student['id']}",
        json={"full_name": "иванов иван петрович"},
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Иванов Иван Петрович"


def test_students_can_be_merged(client: TestClient) -> None:
    source = client.post("/api/students", json={"full_name": "Дубль Один"}).json()
    target = client.post("/api/students", json={"full_name": "Основной Ученик"}).json()

    webhook = client.post(
        "/api/webhooks/artpay",
        json={
            "ap_amount": "120.00",
            "ap_currency": "BYN",
            "ap_erip_trn_id": "merge-test-1",
            "ap_erip_trn_state": "Paid",
            "up_student_fio": "Дубль Один",
        },
    )
    assert webhook.status_code == 200
    payment_id = webhook.json()["payment_id"]
    payment = client.get(f"/api/payments/{payment_id}").json()
    assert payment["student_id"] == source["id"]

    merge_response = client.post(
        f"/api/students/{source['id']}/merge",
        json={"target_student_id": target["id"]},
    )
    assert merge_response.status_code == 200

    payment = client.get(f"/api/payments/{payment_id}").json()
    assert payment["student_id"] == target["id"]

    source_after = client.get(f"/api/students/{source['id']}").json()
    assert source_after["active"] is False


def test_student_group_can_be_cleared(client: TestClient) -> None:
    group = _create_group(client, name="2019")
    student = client.post(
        "/api/students",
        json={"full_name": "Другой Ученик", "group_id": group["id"]},
    ).json()

    response = client.patch(
        f"/api/students/{student['id']}",
        json={"group_id": None},
    )

    assert response.status_code == 200
    assert response.json()["group_id"] is None
    assert response.json()["group_name"] is None


def test_groups_ui_renders(client: TestClient) -> None:
    response = client.get("/groups-ui")
    assert response.status_code == 200
    assert "Добавить ученика" in response.text
    assert "memberEditor" in response.text
    assert "Оплата" in response.text or "оплата" in response.text
    assert "expectedTotal" in response.text
    assert "ожидаем" in response.text.lower() or "Ожидаем" in response.text
