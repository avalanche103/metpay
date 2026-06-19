from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Group, Payment, PaymentStatus, Student

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
def payment_summary(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
) -> dict:
    query = select(Payment)
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
    }


@router.get("/by-student")
def payments_by_student(db: Session = Depends(get_db)) -> list[dict]:
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
        .join(Payment, Payment.student_id == Student.id, isouter=True)
        .group_by(Student.id, Student.full_name, Group.name)
        .order_by(Student.full_name)
    ).all()
    return [
        {
            "student_id": row.id,
            "student_full_name": row.full_name,
            "group_name": row.group_name,
            "total_amount": str(row.total_amount),
            "payments_count": row.payments_count,
        }
        for row in rows
    ]


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
