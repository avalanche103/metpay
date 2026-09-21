from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db import SessionLocal
from app.models import Payment, PaymentStatus, Student
from app.services.import_payments import ImportRow, import_season_payment_rows
from app.services.payment_matching import names_compatible


def test_names_compatible_with_and_without_patronymic() -> None:
    assert names_compatible("Валиев Александр", "Валиев Александр Станиславович")
    assert names_compatible("Валиев Александр Станиславович", "Валиев Александр")
    assert not names_compatible("Иванов Иван Петрович", "Иванов Иван Сергеевич")


def test_import_reuses_compatible_student_instead_of_duplicate() -> None:
    db = SessionLocal()
    try:
        rows = [
            ImportRow(
                paid_at=datetime(2026, 8, 11, 21, 14, 1),
                payer_full_name="Валиев Александр Станиславович",
                amount=Decimal("120.00"),
                currency="BYN",
                description=None,
                raw={},
            ),
            ImportRow(
                paid_at=datetime(2026, 9, 10, 10, 4, 2),
                payer_full_name="Валиев Александр",
                amount=Decimal("140.00"),
                currency="BYN",
                description=None,
                raw={},
            ),
        ]
        result = import_season_payment_rows(db, rows, season="2026/2027", batch_id="valiev")
        db.commit()

        assert result.students_created == 1
        assert result.students_existing == 1
        assert result.payments_created == 2
        assert result.payments_matched == 2

        students = list(
            db.scalars(select(Student).where(Student.active.is_(True)).order_by(Student.id))
        )
        assert len(students) == 1
        assert students[0].full_name == "Валиев Александр Станиславович"

        payments = list(db.scalars(select(Payment)))
        assert len(payments) == 2
        assert {payment.student_id for payment in payments} == {students[0].id}
        assert all(payment.status == PaymentStatus.matched for payment in payments)
    finally:
        db.close()


def test_create_student_rejects_compatible_duplicate(client: TestClient) -> None:
    first = client.post(
        "/api/students",
        json={"full_name": "Валиев Александр Станиславович"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/students",
        json={"full_name": "Валиев Александр"},
    )
    assert second.status_code == 409
    assert "уже существует" in second.json()["detail"]
