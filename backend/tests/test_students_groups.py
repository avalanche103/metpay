from decimal import Decimal

from fastapi.testclient import TestClient


def test_default_groups_are_seeded(client: TestClient) -> None:
    response = client.get("/api/groups")

    assert response.status_code == 200
    groups = response.json()
    assert [group["name"] for group in groups] == ["2012", "2013", "2014+"]
    assert all(Decimal(group["monthly_fee"]) == Decimal("120.00") for group in groups)


def test_student_group_can_be_assigned_from_api(client: TestClient) -> None:
    groups = client.get("/api/groups").json()
    group_2013 = next(group for group in groups if group["name"] == "2013")

    student = client.post(
        "/api/students",
        json={"full_name": "Тестов Ученик Тестович"},
    ).json()

    response = client.patch(
        f"/api/students/{student['id']}",
        json={"group_id": group_2013["id"]},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["group_id"] == group_2013["id"]
    assert payload["group_name"] == "2013"


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
    groups = client.get("/api/groups").json()
    group_2012 = groups[0]
    student = client.post(
        "/api/students",
        json={"full_name": "Другой Ученик", "group_id": group_2012["id"]},
    ).json()

    response = client.patch(
        f"/api/students/{student['id']}",
        json={"group_id": None},
    )

    assert response.status_code == 200
    assert response.json()["group_id"] is None
    assert response.json()["group_name"] is None
