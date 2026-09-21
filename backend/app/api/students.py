from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Group, Parent, Student
from app.schemas import StudentCreate, StudentMergeRequest, StudentRead, StudentUpdate
from app.services.payment_matching import (
    find_active_duplicate,
    format_full_name,
    normalize_full_name,
)
from app.services.students import merge_students

router = APIRouter(prefix="/students", tags=["students"])


def student_to_read(student: Student) -> StudentRead:
    return StudentRead(
        id=student.id,
        full_name=format_full_name(student.full_name),
        normalized_full_name=student.normalized_full_name,
        group_id=student.group_id,
        group_name=student.group.name if student.group else None,
        active=student.active,
        parents=[parent for parent in student.parents],
    )


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)) -> StudentRead:
    formatted_name = format_full_name(payload.full_name)
    if not formatted_name:
        raise HTTPException(status_code=422, detail="full_name cannot be empty")

    duplicate = find_active_duplicate(db, formatted_name)
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Ученик уже существует: {duplicate.full_name} "
                f"(id={duplicate.id}). Используйте существующего или объедините записи."
            ),
        )

    student = Student(
        full_name=formatted_name,
        normalized_full_name=normalize_full_name(formatted_name),
        group_id=payload.group_id,
        active=payload.active,
    )
    student.parents = [Parent(**parent.model_dump()) for parent in payload.parents]
    db.add(student)
    db.commit()
    db.refresh(student)
    if student.group_id:
        db.refresh(student, attribute_names=["group"])
    return student_to_read(student)


@router.get("", response_model=list[StudentRead])
def list_students(db: Session = Depends(get_db)) -> list[StudentRead]:
    students = db.scalars(
        select(Student)
        .options(selectinload(Student.group), selectinload(Student.parents))
        .order_by(Student.full_name)
    ).all()
    return [student_to_read(student) for student in students]


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)) -> StudentRead:
    student = db.scalar(
        select(Student)
        .options(selectinload(Student.group), selectinload(Student.parents))
        .where(Student.id == student_id)
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student was not found")
    return student_to_read(student)


@router.patch("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
) -> StudentRead:
    student = db.scalar(
        select(Student)
        .options(selectinload(Student.group), selectinload(Student.parents))
        .where(Student.id == student_id)
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student was not found")

    updates = payload.model_dump(exclude_unset=True)
    if "full_name" in updates:
        formatted_name = format_full_name(updates["full_name"])
        if not formatted_name:
            raise HTTPException(status_code=422, detail="full_name cannot be empty")
        duplicate = find_active_duplicate(db, formatted_name, exclude_student_id=student.id)
        if duplicate:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Ученик с таким ФИО уже есть: {duplicate.full_name} "
                    f"(id={duplicate.id}). Объедините записи вместо переименования."
                ),
            )
        student.full_name = formatted_name
        student.normalized_full_name = normalize_full_name(formatted_name)

    if "group_id" in updates:
        group_id = updates["group_id"]
        if group_id is not None:
            group = db.get(Group, group_id)
            if not group:
                raise HTTPException(status_code=404, detail="Group was not found")
        student.group_id = group_id

    if "active" in updates:
        student.active = updates["active"]

    db.commit()
    db.refresh(student)
    if student.group_id:
        db.refresh(student, attribute_names=["group"])
    return student_to_read(student)


@router.post("/{student_id}/merge", response_model=StudentRead)
def merge_student_into(
    student_id: int,
    payload: StudentMergeRequest,
    db: Session = Depends(get_db),
) -> StudentRead:
    source = db.scalar(
        select(Student)
        .options(selectinload(Student.group), selectinload(Student.parents))
        .where(Student.id == student_id)
    )
    target = db.scalar(
        select(Student)
        .options(selectinload(Student.group), selectinload(Student.parents))
        .where(Student.id == payload.target_student_id)
    )
    if not source or not target:
        raise HTTPException(status_code=404, detail="Student was not found")

    try:
        merge_students(db, source, target)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    db.commit()
    db.refresh(target)
    if target.group_id:
        db.refresh(target, attribute_names=["group"])
    return student_to_read(target)
