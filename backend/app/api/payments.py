from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Payment, PaymentSource, PaymentStatus, Student
from app.schemas import ManualMatchRequest, PaymentRead, PaymentUpdate
from app.services.payments import manually_match_payment
from app.services.season_periods import is_valid_payment_for, payment_for_options

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/payment-for-options")
def list_payment_for_options(season: str | None = None) -> list[dict[str, str]]:
    return [
        {"value": option.value, "label": option.label}
        for option in payment_for_options(season)
    ]


@router.get("", response_model=list[PaymentRead])
def list_payments(
    status: PaymentStatus | None = None,
    student_id: int | None = None,
    season: str | None = None,
    source: PaymentSource | None = None,
    ungrouped: bool | None = None,
    payment_for: str | None = None,
    db: Session = Depends(get_db),
) -> list[Payment]:
    query = select(Payment).order_by(Payment.created_at.desc())
    if status:
        query = query.where(Payment.status == status)
    if student_id:
        query = query.where(Payment.student_id == student_id)
    if season:
        query = query.where(Payment.season == season)
    if source:
        query = query.where(Payment.source == source)
    if payment_for:
        query = query.where(Payment.payment_for == payment_for)
    if ungrouped:
        query = query.outerjoin(Student, Payment.student_id == Student.id).where(
            or_(Payment.student_id.is_(None), Student.group_id.is_(None))
        )
    return list(db.scalars(query))


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(payment_id: int, db: Session = Depends(get_db)) -> Payment:
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment was not found")
    return payment


@router.patch("/{payment_id}", response_model=PaymentRead)
def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    db: Session = Depends(get_db),
) -> Payment:
    payment = db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment was not found")

    updates = payload.model_dump(exclude_unset=True)
    if "payment_for" in updates:
        payment_for = updates["payment_for"]
        if payment_for is not None and not is_valid_payment_for(payment_for, payment.season):
            raise HTTPException(status_code=422, detail="Invalid payment_for value")
        payment.payment_for = payment_for

    db.commit()
    db.refresh(payment)
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
