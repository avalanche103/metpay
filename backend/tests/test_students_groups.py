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


def test_student_profile_can_be_created_and_updated(client: TestClient) -> None:
    create_response = client.post(
        "/api/students",
        json={
            "full_name": "Профилев Ученик",
            "birth_date": "2010-05-15",
            "passport_number": "AB1234567",
            "passport_personal_number": "1234567A123PB1",
            "passport_issued_at": "2024-01-10",
            "passport_issued_by": "РОВД Центрального района",
            "address": "г. Минск, ул. Примерная, 1",
            "educational_institution": "СШ №1",
            "parents": [
                {"full_name": "Профилева Мария", "phone": "+375291111111"},
                {"full_name": "Профилев Иван", "phone": "+375292222222"},
            ],
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["birth_date"] == "2010-05-15"
    assert created["passport_number"] == "AB1234567"
    assert created["passport_personal_number"] == "1234567A123PB1"
    assert created["passport_issued_at"] == "2024-01-10"
    assert created["passport_issued_by"] == "РОВД Центрального района"
    assert created["address"] == "г. Минск, ул. Примерная, 1"
    assert created["educational_institution"] == "СШ №1"
    assert len(created["parents"]) == 2
    assert created["parents"][0]["full_name"] == "Профилева Мария"
    assert created["parents"][0]["phone"] == "+375291111111"
    assert created["parents"][1]["full_name"] == "Профилев Иван"

    get_response = client.get(f"/api/students/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["educational_institution"] == "СШ №1"

    update_response = client.patch(
        f"/api/students/{created['id']}",
        json={
            "address": "г. Минск, ул. Новая, 5",
            "educational_institution": "Гимназия №2",
            "parents": [
                {"full_name": "Профилева Анна", "phone": "+375293333333"},
            ],
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["address"] == "г. Минск, ул. Новая, 5"
    assert updated["educational_institution"] == "Гимназия №2"
    assert updated["passport_number"] == "AB1234567"
    assert len(updated["parents"]) == 1
    assert updated["parents"][0]["full_name"] == "Профилева Анна"
    assert updated["parents"][0]["phone"] == "+375293333333"


def test_student_parents_are_replaced_on_patch(client: TestClient) -> None:
    student = client.post(
        "/api/students",
        json={
            "full_name": "Родительский Тест",
            "parents": [
                {"full_name": "Отец Один", "phone": "111"},
                {"full_name": "Мать Один", "phone": "222"},
            ],
        },
    ).json()
    assert len(student["parents"]) == 2

    response = client.patch(
        f"/api/students/{student['id']}",
        json={
            "parents": [
                {"full_name": "Только Мать", "phone": "333"},
                {"full_name": "", "phone": ""},
            ],
        },
    )
    assert response.status_code == 200
    parents = response.json()["parents"]
    assert len(parents) == 1
    assert parents[0]["full_name"] == "Только Мать"
    assert parents[0]["phone"] == "333"


def test_student_ui_shows_profile_form(client: TestClient) -> None:
    student = client.post("/api/students", json={"full_name": "Карточка Ученик"}).json()
    response = client.get(f"/students-ui/{student['id']}")
    assert response.status_code == 200
    assert "Данные ученика" in response.text
    assert "passportNumber" in response.text
    assert "parent1Name" in response.text
    assert "profileForm" in response.text
    assert "Полная оплата" in response.text
    assert "Пропуск месяца" in response.text
    assert "skipMonthSelect" in response.text


def test_student_month_skip_crud(client: TestClient) -> None:
    student = client.post("/api/students", json={"full_name": "Пропуск Ученик"}).json()

    create = client.post(
        f"/api/students/{student['id']}/month-skips",
        json={"period": "2026-09"},
    )
    assert create.status_code == 201
    assert create.json()["period"] == "2026-09"
    assert create.json()["student_id"] == student["id"]

    listed = client.get(f"/api/students/{student['id']}/month-skips")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    by_period = client.get("/api/students/month-skips", params={"period": "2026-09"})
    assert by_period.status_code == 200
    assert len(by_period.json()) == 1

    delete = client.delete(f"/api/students/{student['id']}/month-skips/2026-09")
    assert delete.status_code == 204
    assert client.get(f"/api/students/{student['id']}/month-skips").json() == []


def test_student_month_skip_rejects_tournament(client: TestClient) -> None:
    student = client.post("/api/students", json={"full_name": "Турнир Ученик"}).json()
    response = client.post(
        f"/api/students/{student['id']}/month-skips",
        json={"period": "tournament"},
    )
    assert response.status_code == 422
