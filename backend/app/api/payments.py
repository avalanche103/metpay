from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Payment, PaymentStatus, Student
from app.schemas import ManualMatchRequest, PaymentRead
from app.services.payments import manually_match_payment

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=list[PaymentRead])
def list_payments(
    status: PaymentStatus | None = None,
    student_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[Payment]:
    query = select(Payment).order_by(Payment.created_at.desc())
    if status:
        query = query.where(Payment.status == status)
    if student_id:
        query = query.where(Payment.student_id == student_id)
    return list(db.scalars(query))


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)) -> Payment:
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment was not found")
    return payment


@router.post("/{payment_id}/match", response_model=PaymentRead)
def match_payment(
    payment_id: int,
    payload: ManualMatchRequest,
    db: Session = Depends(get_db),
) -> Payment:
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment was not found")

    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student was not found")

    manually_match_payment(db, payment, student)
    db.commit()
    db.refresh(payment)
    return payment
