from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Group, Payment, PaymentSource, PaymentStatus, Student

router = APIRouter(prefix="/reports", tags=["reports"])


def _payment_filters(season: str | None, source: PaymentSource | None):
    conditions = []
    if season:
        conditions.append(Payment.season == season)
    if source:
        conditions.append(Payment.source == source)
    return conditions


@router.get("/summary")
def payment_summary(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    season: str | None = None,
    source: PaymentSource | None = None,
    db: Session = Depends(get_db),
) -> dict:
    query = select(Payment)
    for condition in _payment_filters(season, source):
        query = query.where(condition)
    if date_from:
        query = query.where(Payment.paid_at >= date_from)
    if date_to:
        query = query.where(Payment.paid_at <= date_to)
    payments = list(db.scalars(query))

    total_amount = sum(payment.amount for payment in payments)
    needs_review = sum(1 for payment in payments if payment.status == PaymentStatus.needs_review)
    matched = sum(1 for payment in payments if payment.status == PaymentStatus.matched)

    return {
        "payments_count": len(payments),
        "matched_count": matched,
        "needs_review_count": needs_review,
        "total_amount": str(total_amount),
        "season": season,
        "source": source.value if source else None,
    }


@router.get("/by-student")
def payments_by_student(
    season: str | None = None,
    source: PaymentSource | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    payment_on = Payment.student_id == Student.id
    if season:
        payment_on = payment_on & (Payment.season == season)
    if source:
        payment_on = payment_on & (Payment.source == source)

    rows = db.execute(
        select(
            Student.id,
            Student.full_name,
            Group.name.label("group_name"),
            func.coalesce(func.sum(Payment.amount), 0).label("total_amount"),
            func.count(Payment.id).label("payments_count"),
        )
        .select_from(Student)
        .join(Group, Group.id == Student.group_id, isouter=True)
        .join(Payment, payment_on, isouter=True)
        .group_by(Student.id, Student.full_name, Group.name)
        .having(func.count(Payment.id) > 0)
        .order_by(Student.full_name)
    ).all()
    return [
        {
            "student_id": row.id,
            "student_full_name": row.full_name,
            "group_name": row.group_name,
            "total_amount": str(row.total_amount),
            "payments_count": row.payments_count,
            "season": season,
        }
        for row in rows
    ]


@router.get("/by-month")
def payments_by_month(
    season: str | None = None,
    source: PaymentSource | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    query = select(Payment).where(Payment.paid_at.is_not(None))
    for condition in _payment_filters(season, source):
        query = query.where(condition)
    payments = list(db.scalars(query.order_by(Payment.paid_at)))

    totals: dict[str, dict[str, int | str]] = {}
    for payment in payments:
        month_key = payment.paid_at.strftime("%Y-%m") if payment.paid_at else "unknown"
        bucket = totals.setdefault(
            month_key,
            {"month": month_key, "payments_count": 0, "total_amount": "0"},
        )
        bucket["payments_count"] = int(bucket["payments_count"]) + 1
        bucket["total_amount"] = str(
            Decimal(str(bucket["total_amount"])) + Decimal(str(payment.amount))
        )

    return sorted(totals.values(), key=lambda item: item["month"])


@router.get("/needs-review")
def payments_needing_review(db: Session = Depends(get_db)) -> list[dict]:
    payments = db.scalars(
        select(Payment)
        .where(Payment.status == PaymentStatus.needs_review)
        .order_by(Payment.created_at)
    ).all()
    return [
        {
            "payment_id": payment.id,
            "payer_full_name": payment.payer_full_name,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "reason": payment.unmatched.reason if payment.unmatched else None,
            "candidate_student_ids": payment.unmatched.candidate_student_ids
            if payment.unmatched
            else [],
        }
        for payment in payments
    ]
