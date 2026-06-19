import re
from dataclasses import dataclass
from itertools import permutations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Student

_NON_NAME_CHARS = re.compile(r"[^a-zа-яё\s-]", re.IGNORECASE)
_SPACES = re.compile(r"\s+")


@dataclass(frozen=True)
class MatchResult:
    student: Student | None
    candidate_ids: list[int]
    reason: str | None = None


def normalize_full_name(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.strip().lower().replace("ё", "е")
    normalized = _NON_NAME_CHARS.sub(" ", normalized)
    normalized = normalized.replace("-", " ")
    return _SPACES.sub(" ", normalized).strip()


def name_variants(value: str | None) -> set[str]:
    normalized = normalize_full_name(value)
    if not normalized:
        return set()
    parts = normalized.split()
    variants = {normalized}
    if 2 <= len(parts) <= 4:
        variants.update(" ".join(item) for item in permutations(parts))
    return variants


def find_student_for_payer(db: Session, payer_full_name: str | None) -> MatchResult:
    variants = name_variants(payer_full_name)
    if not variants:
        return MatchResult(student=None, candidate_ids=[], reason="payer full name is missing")

    students = db.scalars(
        select(Student).where(Student.active.is_(True), Student.normalized_full_name.in_(variants))
    ).all()

    if len(students) == 1:
        return MatchResult(student=students[0], candidate_ids=[students[0].id])
    if len(students) > 1:
        return MatchResult(
            student=None,
            candidate_ids=[student.id for student in students],
            reason="multiple students match payer full name",
        )
    return MatchResult(
        student=None,
        candidate_ids=[],
        reason="student was not found by payer full name",
    )
