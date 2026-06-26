from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment, Student


def merge_students(db: Session, source: Student, target: Student) -> Student:
    if source.id == target.id:
        raise ValueError("cannot merge student into itself")

    payments = db.scalars(select(Payment).where(Payment.student_id == source.id)).all()
    for payment in payments:
        payment.student_id = target.id

    source.active = False
    return target
