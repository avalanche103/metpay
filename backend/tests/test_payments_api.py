from fastapi.testclient import TestClient


def test_payment_for_options_for_season(client: TestClient) -> None:
    response = client.get("/api/payments/payment-for-options", params={"season": "2025/2026"})

    assert response.status_code == 200
    options = response.json()
    assert options[0] == {"value": "2025-08", "label": "Август 2025"}
    assert options[-1] == {"value": "tournament", "label": "Турнир"}
    assert len(options) == 12


def test_import_clipboard_payments_and_dedupe(client: TestClient) -> None:
    text = (
        "20.09.2026 19:06:56\tШулин Лев Борисович\t120.00\tBYN\t0.0\t120.00\tЗаказ оплачен\n"
        "18.09.2026 20:20:14\tКазанцев Святослав\t70.00\tBYN\t0.0\t70.00\tЗаказ оплачен\n"
    )
    first = client.post(
        "/api/payments/import-clipboard",
        json={"text": text, "season": "2026/2027"},
    )
    assert first.status_code == 200
    body = first.json()
    assert body["rows_parsed"] == 2
    assert body["payments_created"] == 2
    assert body["payments_skipped"] == 0
    assert body["students_created"] == 2

    second = client.post(
        "/api/payments/import-clipboard",
        json={"text": text, "season": "2026/2027"},
    )
    assert second.status_code == 200
    assert second.json()["payments_created"] == 0
    assert second.json()["payments_skipped"] == 2

    listed = client.get("/api/payments", params={"season": "2026/2027"}).json()
    assert len(listed) == 2


def test_import_clipboard_rejects_empty_rows(client: TestClient) -> None:
    response = client.post(
        "/api/payments/import-clipboard",
        json={"text": "Дата\n№ заказа\nСумма\n", "season": "2026/2027"},
    )
    assert response.status_code == 422


def test_payment_for_can_be_updated(client: TestClient) -> None:
    created = client.post(
        "/api/webhooks/artpay",
        json={
            "ap_amount": "120.00",
            "ap_currency": "BYN",
            "ap_erip_trn_id": "payment-for-update-1",
            "ap_erip_trn_state": "Paid",
            "up_student_fio": "Период Тестов",
        },
    ).json()
    payment_id = created["payment_id"]

    response = client.patch(
        f"/api/payments/{payment_id}",
        json={"payment_for": "2025-09"},
    )
    assert response.status_code == 200
    assert response.json()["payment_for"] == "2025-09"

    listed = client.get("/api/payments", params={"payment_for": "2025-09"}).json()
    assert [item["id"] for item in listed] == [payment_id]


def test_payment_can_be_split_into_parts(client: TestClient) -> None:
    created = client.post(
        "/api/webhooks/artpay",
        json={
            "ap_amount": "260.00",
            "ap_currency": "BYN",
            "ap_erip_trn_id": "payment-split-1",
            "ap_erip_trn_state": "Paid",
            "up_student_fio": "Петришенко Стас",
        },
    ).json()
    payment_id = created["payment_id"]

    response = client.post(
        f"/api/payments/{payment_id}/split",
        json={
            "parts": [
                {"amount": "140.00", "payment_for": "2026-08"},
                {"amount": "120.00", "payment_for": "2026-09"},
            ]
        },
    )
    assert response.status_code == 200
    parts = response.json()
    assert len(parts) == 2
    assert {part["amount"] for part in parts} == {"140.00", "120.00"}
    assert {part["payment_for"] for part in parts} == {"2026-08", "2026-09"}
    assert len({part["split_group_id"] for part in parts}) == 1
    assert sum(float(part["amount"]) for part in parts) == 260.0

    listed = client.get("/api/payments").json()
    split_ids = {part["id"] for part in parts}
    assert split_ids.issubset({item["id"] for item in listed})
    assert len([item for item in listed if item["id"] in split_ids]) == 2


def test_payment_split_rejects_wrong_sum(client: TestClient) -> None:
    created = client.post(
        "/api/webhooks/artpay",
        json={
            "ap_amount": "200.00",
            "ap_currency": "BYN",
            "ap_erip_trn_id": "payment-split-bad-sum",
            "ap_erip_trn_state": "Paid",
            "up_student_fio": "Сумма Тест",
        },
    ).json()

    response = client.post(
        f"/api/payments/{created['payment_id']}/split",
        json={
            "parts": [
                {"amount": "100.00", "payment_for": "2026-08"},
                {"amount": "50.00", "payment_for": "2026-09"},
            ]
        },
    )
    assert response.status_code == 422


def test_list_payments_ungrouped_filter(client: TestClient) -> None:
    grouped_student = client.post(
        "/api/students",
        json={"full_name": "Групповой Ученик"},
    ).json()
    client.post(
        "/api/students",
        json={"full_name": "Без Группы Ученик"},
    ).json()
    group = client.post(
        "/api/groups",
        json={"name": "Тестовая", "monthly_fee": "120.00"},
    ).json()
    client.patch(
        f"/api/students/{grouped_student['id']}",
        json={"group_id": group["id"]},
    )

    grouped_payment = client.post(
        "/api/webhooks/artpay",
        json={
            "ap_amount": "70.00",
            "ap_currency": "BYN",
            "ap_erip_trn_id": "ungrouped-filter-1",
            "ap_erip_trn_state": "Paid",
            "up_student_fio": "Групповой Ученик",
        },
    ).json()
    ungrouped_payment = client.post(
        "/api/webhooks/artpay",
        json={
            "ap_amount": "80.00",
            "ap_currency": "BYN",
            "ap_erip_trn_id": "ungrouped-filter-2",
            "ap_erip_trn_state": "Paid",
            "up_student_fio": "Без Группы Ученик",
        },
    ).json()
    no_student_payment = client.post(
        "/api/webhooks/artpay",
        json={
            "ap_amount": "90.00",
            "ap_currency": "BYN",
            "ap_erip_trn_id": "ungrouped-filter-3",
            "ap_erip_trn_state": "Paid",
            "up_student_fio": "Неизвестный Ученик",
        },
    ).json()

    response = client.get("/api/payments", params={"ungrouped": True})
    payment_ids = {item["id"] for item in response.json()}

    assert grouped_payment["payment_id"] not in payment_ids
    assert ungrouped_payment["payment_id"] in payment_ids
    assert no_student_payment["payment_id"] in payment_ids
