from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Group, Parent, Student, StudentMonthSkip
from app.schemas import (
    MonthSkipCreate,
    MonthSkipRead,
    ParentCreate,
    StudentCreate,
    StudentMergeRequest,
    StudentRead,
    StudentUpdate,
)
from app.services.payment_matching import (
    find_active_duplicate,
    format_full_name,
    normalize_full_name,
)
from app.services.season_periods import TOURNAMENT_KEY, is_valid_payment_for
from app.services.students import merge_students

router = APIRouter(prefix="/students", tags=["students"])

_PROFILE_FIELDS = (
    "birth_date",
    "passport_number",
    "passport_personal_number",
    "passport_issued_at",
    "passport_issued_by",
    "address",
    "educational_institution",
)


def _parent_has_data(parent: ParentCreate) -> bool:
    return bool((parent.full_name or "").strip() or (parent.phone or "").strip())


def _parents_from_payload(parents: list[ParentCreate]) -> list[Parent]:
    return [
        Parent(**parent.model_dump())
        for parent in parents
        if _parent_has_data(parent)
    ]


def _validate_skip_period(period: str) -> None:
    if period == TOURNAMENT_KEY or not is_valid_payment_for(period):
        raise HTTPException(status_code=422, detail="Некорректный период для пропуска")


def student_to_read(student: Student) -> StudentRead:
    return StudentRead(
        id=student.id,
        full_name=format_full_name(student.full_name),
        normalized_full_name=student.normalized_full_name,
        group_id=student.group_id,
        group_name=student.group.name if student.group else None,
        active=student.active,
        birth_date=student.birth_date,
        passport_number=student.passport_number,
        passport_personal_number=student.passport_personal_number,
        passport_issued_at=student.passport_issued_at,
        passport_issued_by=student.passport_issued_by,
        address=student.address,
        educational_institution=student.educational_institution,
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
        birth_date=payload.birth_date,
        passport_number=payload.passport_number,
        passport_personal_number=payload.passport_personal_number,
        passport_issued_at=payload.passport_issued_at,
        passport_issued_by=payload.passport_issued_by,
        address=payload.address,
        educational_institution=payload.educational_institution,
    )
    student.parents = _parents_from_payload(payload.parents)
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


@router.get("/month-skips", response_model=list[MonthSkipRead])
def list_month_skips(
    period: str | None = None,
    student_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[StudentMonthSkip]:
    query = select(StudentMonthSkip).order_by(StudentMonthSkip.period.desc())
    if period:
        query = query.where(StudentMonthSkip.period == period)
    if student_id:
        query = query.where(StudentMonthSkip.student_id == student_id)
    return list(db.scalars(query))


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


@router.get("/{student_id}/month-skips", response_model=list[MonthSkipRead])
def list_student_month_skips(
    student_id: int,
    db: Session = Depends(get_db),
) -> list[StudentMonthSkip]:
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student was not found")
    return list(
        db.scalars(
            select(StudentMonthSkip)
            .where(StudentMonthSkip.student_id == student_id)
            .order_by(StudentMonthSkip.period.desc())
        )
    )


@router.post(
    "/{student_id}/month-skips",
    response_model=MonthSkipRead,
    status_code=status.HTTP_201_CREATED,
)
def create_student_month_skip(
    student_id: int,
    payload: MonthSkipCreate,
    db: Session = Depends(get_db),
) -> StudentMonthSkip:
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student was not found")

    _validate_skip_period(payload.period)

    existing = db.scalar(
        select(StudentMonthSkip).where(
            StudentMonthSkip.student_id == student_id,
            StudentMonthSkip.period == payload.period,
        )
    )
    if existing:
        return existing

    skip = StudentMonthSkip(student_id=student_id, period=payload.period)
    db.add(skip)
    db.commit()
    db.refresh(skip)
    return skip


@router.delete("/{student_id}/month-skips/{period}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_month_skip(
    student_id: int,
    period: str,
    db: Session = Depends(get_db),
) -> None:
    skip = db.scalar(
        select(StudentMonthSkip).where(
            StudentMonthSkip.student_id == student_id,
            StudentMonthSkip.period == period,
        )
    )
    if not skip:
        raise HTTPException(status_code=404, detail="Пропуск месяца не найден")
    db.delete(skip)
    db.commit()


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

    for field in _PROFILE_FIELDS:
        if field in updates:
            setattr(student, field, updates[field])

    if "parents" in updates:
        student.parents = _parents_from_payload(payload.parents or [])

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
