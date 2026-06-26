from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Payment, PaymentSource, PaymentStatus, Student
from app.services.import_payments import ImportRow, import_season_payment_rows


def test_import_creates_students_and_payments() -> None:
    db = SessionLocal()
    try:
        rows = [
            ImportRow(
                paid_at=datetime(2025, 8, 4, 11, 47, 23),
                payer_full_name="Иванов Петр Сергеевич",
                amount=Decimal("120.00"),
                currency="BYN",
                description="Заказ №: Иванов Петр Сергеевич",
                raw={},
            ),
            ImportRow(
                paid_at=datetime(2025, 9, 4, 11, 47, 23),
                payer_full_name="Иванов Петр Сергеевич",
                amount=Decimal("120.00"),
                currency="BYN",
                description="Заказ №: Иванов Петр Сергеевич",
                raw={},
            ),
        ]
        result = import_season_payment_rows(db, rows, season="2025/2026", batch_id="test-batch")
        db.commit()

        assert result.students_created == 1
        assert result.payments_created == 2
        assert result.payments_matched == 2
        assert result.payments_skipped == 0

        student = db.scalar(select(Student))
        assert student is not None
        assert student.full_name == "Иванов Петр Сергеевич"

        payments = list(db.scalars(select(Payment)))
        assert len(payments) == 2
        assert all(payment.source == PaymentSource.import_ for payment in payments)
        assert all(payment.season == "2025/2026" for payment in payments)
        assert all(payment.status == PaymentStatus.matched for payment in payments)

        second = import_season_payment_rows(db, rows, season="2025/2026", batch_id="test-batch-2")
        db.commit()
        assert second.payments_skipped == 2
        assert second.payments_created == 0
    finally:
        db.close()
