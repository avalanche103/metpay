from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Payment, PaymentSource, PaymentStatus, Student
from app.services.import_payments import (
    ImportRow,
    import_season_payment_rows,
    parse_artpay_clipboard_text,
)

CLIPBOARD_SAMPLE = """
Дата
№ заказа
Сумма
Валюта
Курс НБ РБ
По курсу
Статус заказа
20.09.2026 19:06:56	Шулин Лев Борисович	120.00	BYN	0.0	120.00	Заказ оплачен
18.09.2026 20:20:14	Казанцев Святослав	70.00	BYN	0.0	70.00	Заказ оплачен
18.09.2026 17:14:19	Воробьев Ян	120.00	BYN	0.0	120.00	Заказ оплачен
"""


def test_parse_artpay_clipboard_text() -> None:
    rows = parse_artpay_clipboard_text(CLIPBOARD_SAMPLE)

    assert len(rows) == 3
    assert rows[0].payer_full_name == "Шулин Лев Борисович"
    assert rows[0].amount == Decimal("120.00")
    assert rows[0].currency == "BYN"
    assert rows[0].paid_at == datetime(2026, 9, 20, 19, 6, 56)
    assert rows[1].payer_full_name == "Казанцев Святослав"
    assert rows[2].amount == Decimal("120.00")


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


def test_clipboard_import_skips_duplicates() -> None:
    db = SessionLocal()
    try:
        rows = parse_artpay_clipboard_text(CLIPBOARD_SAMPLE)
        first = import_season_payment_rows(db, rows, season="2026/2027", batch_id="clip-1")
        db.commit()
        assert first.payments_created == 3
        assert first.payments_skipped == 0

        second = import_season_payment_rows(db, rows, season="2026/2027", batch_id="clip-2")
        db.commit()
        assert second.payments_created == 0
        assert second.payments_skipped == 3
        assert len(list(db.scalars(select(Payment)))) == 3
    finally:
        db.close()
