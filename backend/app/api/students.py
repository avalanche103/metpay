from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Parent, Student
from app.schemas import StudentCreate, StudentRead
from app.services.payment_matching import normalize_full_name

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)) -> Student:
    student = Student(
        full_name=payload.full_name,
        normalized_full_name=normalize_full_name(payload.full_name),
        group_id=payload.group_id,
        active=payload.active,
    )
    student.parents = [Parent(**parent.model_dump()) for parent in payload.parents]
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("", response_model=list[StudentRead])
def list_students(db: Session = Depends(get_db)) -> list[Student]:
    return list(db.scalars(select(Student).order_by(Student.full_name)))


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)) -> Student:
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student was not found")
    return student
