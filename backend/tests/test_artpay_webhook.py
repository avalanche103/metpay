from fastapi.testclient import TestClient


def paid_payload(**overrides: object) -> dict:
    payload = {
        "ap_storeid": "100024",
        "ap_test": 1,
        "ap_notice_type": "EripTrnStatus",
        "ap_erip_trn_state": "Paid",
        "ap_amount": "85.00",
        "ap_currency": "BYN",
        "ap_erip_service_no": "6",
        "ap_erip_invoice_id": "1207-6-770",
        "ap_erip_trn_id": "173035295",
        "ap_sp_trn_id": "6",
        "up_student_fio": "Иванов Петр",
    }
    payload.update(overrides)
    return payload


def test_webhook_creates_matched_payment(client: TestClient) -> None:
    student_response = client.post("/api/students", json={"full_name": "Иванов Петр"})
    assert student_response.status_code == 201
    student_id = student_response.json()["id"]

    response = client.post("/api/webhooks/artpay", json=paid_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "matched"
    assert body["matched_student_id"] == student_id

    payments = client.get("/api/payments").json()
    assert len(payments) == 1
    assert payments[0]["amount"] == "85.00"
    assert payments[0]["student_id"] == student_id


def test_webhook_is_idempotent_by_erip_transaction_id(client: TestClient) -> None:
    client.post("/api/students", json={"full_name": "Иванов Петр"})

    first_response = client.post("/api/webhooks/artpay", json=paid_payload())
    second_response = client.post("/api/webhooks/artpay", json=paid_payload())

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["duplicate"] is True
    assert len(client.get("/api/payments").json()) == 1


def test_webhook_marks_unknown_name_for_review(client: TestClient) -> None:
    response = client.post("/api/webhooks/artpay", json=paid_payload(up_student_fio="Петров Иван"))

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "needs_review"
    assert body["review_reason"] == "student was not found by payer full name"

    review = client.get("/api/reports/needs-review").json()
    assert len(review) == 1
    assert review[0]["payer_full_name"] == "Петров Иван"


def test_manual_match_resolves_payment(client: TestClient) -> None:
    student_id = client.post("/api/students", json={"full_name": "Петров Иван"}).json()["id"]
    payment_id = client.post(
        "/api/webhooks/artpay",
        json=paid_payload(up_student_fio="Иван Петров"),
    ).json()["payment_id"]

    response = client.post(f"/api/payments/{payment_id}/match", json={"student_id": student_id})

    assert response.status_code == 200
    assert response.json()["status"] == "matched"
    assert response.json()["student_id"] == student_id
