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


def delete_student(student: Student) -> Student:
    """Deactivate a student and remove them from their group.

    Payments stay linked for history; the student disappears from active lists.
    """
    student.active = False
    student.group_id = None
    return student
