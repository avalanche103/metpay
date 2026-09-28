from fastapi.testclient import TestClient


def _create_group(client: TestClient, name: str, fee: str = "140.00") -> dict:
    return client.post(
        "/api/groups",
        json={"name": name, "monthly_fee": fee, "active": True},
    ).json()


def _create_student(client: TestClient, full_name: str, group_id: int) -> dict:
    return client.post(
        "/api/students",
        json={"full_name": full_name, "group_id": group_id},
    ).json()


def test_unpaid_by_month_lists_unpaid_and_partial(client: TestClient) -> None:
    group = _create_group(client, "Отчётная группа")
    unpaid = _create_student(client, "Неоплативший Ученик", group["id"])
    partial = _create_student(client, "Частичный Ученик", group["id"])
    paid = _create_student(client, "Оплативший Ученик", group["id"])
    skipped = _create_student(client, "Пропущенный Ученик", group["id"])

    assert (
        client.post(
            "/api/payments",
            json={
                "student_id": partial["id"],
                "amount": "70.00",
                "paid_at": "2026-09-10",
                "payment_for": "2026-09",
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            "/api/payments",
            json={
                "student_id": paid["id"],
                "amount": "140.00",
                "paid_at": "2026-09-10",
                "payment_for": "2026-09",
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/api/students/{skipped['id']}/month-skips",
            json={"period": "2026-09"},
        ).status_code
        == 201
    )

    response = client.get("/api/reports/unpaid-by-month", params={"period": "2026-09"})
    assert response.status_code == 200
    body = response.json()
    assert body["period"] == "2026-09"
    assert body["period_label"] == "Сентябрь 2026"
    assert body["unpaid_count"] == 1
    assert body["partial_count"] == 1
    assert body["expected_total"] == "210.00"

    names = {item["student_full_name"]: item for item in body["items"]}
    assert set(names) == {"Неоплативший Ученик", "Частичный Ученик"}
    assert names["Неоплативший Ученик"]["status"] == "unpaid"
    assert names["Неоплативший Ученик"]["expected_amount"] == "140.00"
    assert names["Частичный Ученик"]["status"] == "partial"
    assert names["Частичный Ученик"]["paid_amount"] == "70.00"
    assert names["Частичный Ученик"]["expected_amount"] == "70.00"
    assert paid["full_name"] not in names
    assert skipped["full_name"] not in names


def test_unpaid_by_month_respects_counts_as_full(client: TestClient) -> None:
    group = _create_group(client, "Полный кредит")
    student = _create_student(client, "Кредитный Ученик", group["id"])
    payment = client.post(
        "/api/payments",
        json={
            "student_id": student["id"],
            "amount": "50.00",
            "paid_at": "2026-09-12",
            "payment_for": "2026-09",
        },
    ).json()
    assert (
        client.patch(
            f"/api/payments/{payment['id']}",
            json={"counts_as_full": True},
        ).status_code
        == 200
    )

    response = client.get("/api/reports/unpaid-by-month", params={"period": "2026-09"})
    assert response.status_code == 200
    assert response.json()["items"] == []


def test_unpaid_by_month_can_filter_by_group(client: TestClient) -> None:
    group_a = _create_group(client, "Группа А")
    group_b = _create_group(client, "Группа Б")
    student_a = _create_student(client, "Ученик А", group_a["id"])
    _create_student(client, "Ученик Б", group_b["id"])

    response = client.get(
        "/api/reports/unpaid-by-month",
        params={"period": "2026-09", "group_id": group_a["id"]},
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["student_id"] == student_a["id"]


def test_unpaid_by_month_status_filter(client: TestClient) -> None:
    group = _create_group(client, "Фильтр статуса")
    unpaid = _create_student(client, "Полный Долг", group["id"])
    partial = _create_student(client, "Частичный Долг", group["id"])
    client.post(
        "/api/payments",
        json={
            "student_id": partial["id"],
            "amount": "40.00",
            "paid_at": "2026-09-10",
            "payment_for": "2026-09",
        },
    )

    not_full = client.get(
        "/api/reports/unpaid-by-month",
        params={"period": "2026-09", "status": "not_full"},
    ).json()
    assert not_full["status_filter"] == "not_full"
    assert {item["student_id"] for item in not_full["items"]} == {unpaid["id"], partial["id"]}

    only_unpaid = client.get(
        "/api/reports/unpaid-by-month",
        params={"period": "2026-09", "status": "unpaid"},
    ).json()
    assert [item["student_id"] for item in only_unpaid["items"]] == [unpaid["id"]]
    assert only_unpaid["unpaid_count"] == 1
    assert only_unpaid["partial_count"] == 0

    only_partial = client.get(
        "/api/reports/unpaid-by-month",
        params={"period": "2026-09", "status": "partial"},
    ).json()
    assert [item["student_id"] for item in only_partial["items"]] == [partial["id"]]
    assert only_partial["partial_count"] == 1
    assert only_partial["unpaid_count"] == 0


def test_unpaid_by_month_rejects_tournament(client: TestClient) -> None:
    response = client.get("/api/reports/unpaid-by-month", params={"period": "tournament"})
    assert response.status_code == 422


def test_unpaid_ui_loads(client: TestClient) -> None:
    response = client.get("/unpaid-ui")
    assert response.status_code == 200
    assert "Отчёт по неоплаченным" in response.text
    assert "/api/reports/unpaid-by-month" in response.text
    assert 'id="periodSelect"' in response.text
    assert 'id="statusSelect"' in response.text
    assert "Не оплатили полностью" in response.text
