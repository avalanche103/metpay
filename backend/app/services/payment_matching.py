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


def format_name_part(part: str) -> str:
    if not part:
        return ""
    lower = part.lower()
    return lower[0].upper() + lower[1:] if len(lower) > 1 else lower.upper()


def format_full_name(value: str | None) -> str:
    if not value:
        return ""
    cleaned = _SPACES.sub(" ", value.strip())
    formatted_parts: list[str] = []
    for token in cleaned.split():
        if "-" in token:
            formatted_parts.append(
                "-".join(format_name_part(piece) for piece in token.split("-") if piece)
            )
        else:
            formatted_parts.append(format_name_part(token))
    return " ".join(formatted_parts)


def normalize_full_name(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.strip().lower().replace("ё", "е")
    normalized = _NON_NAME_CHARS.sub(" ", normalized)
    normalized = normalized.replace("-", " ")
    return _SPACES.sub(" ", normalized).strip()


def name_parts(value: str | None) -> list[str]:
    normalized = normalize_full_name(value)
    return normalized.split() if normalized else []


def name_variants(value: str | None) -> set[str]:
    normalized = normalize_full_name(value)
    if not normalized:
        return set()
    parts = normalized.split()
    variants = {normalized}
    if 2 <= len(parts) <= 4:
        variants.update(" ".join(item) for item in permutations(parts))
    return variants


def _is_token_prefix(shorter: list[str], longer: list[str]) -> bool:
    if not shorter or len(shorter) > len(longer):
        return False
    return longer[: len(shorter)] == shorter


def names_compatible(left: str | None, right: str | None) -> bool:
    """True when names are the same person with/without patronymic.

    Examples:
    - "Валиев Александр" ~ "Валиев Александр Станиславович"
    - "Иванов Иван Петрович" !~ "Иванов Иван Сергеевич"
    """
    left_parts = name_parts(left)
    right_parts = name_parts(right)
    if not left_parts or not right_parts:
        return False
    if left_parts == right_parts:
        return True
    if len(left_parts) >= 2 and len(right_parts) >= 2:
        if frozenset(left_parts[:2]) != frozenset(right_parts[:2]):
            return False
        if len(left_parts) >= 3 and len(right_parts) >= 3:
            return (
                left_parts == right_parts
                or _is_token_prefix(left_parts, right_parts)
                or _is_token_prefix(right_parts, left_parts)
            )
        return True
    return _is_token_prefix(left_parts, right_parts) or _is_token_prefix(right_parts, left_parts)


def prefer_fuller_name(current: str, candidate: str) -> str:
    """Keep the longer/more complete formatted name when merging identity."""
    current_parts = name_parts(current)
    candidate_parts = name_parts(candidate)
    if len(candidate_parts) > len(current_parts):
        return format_full_name(candidate)
    if len(candidate_parts) == len(current_parts) and len(format_full_name(candidate)) > len(
        format_full_name(current)
    ):
        return format_full_name(candidate)
    return format_full_name(current) or format_full_name(candidate)


def find_compatible_students(db: Session, full_name: str | None) -> list[Student]:
    variants = name_variants(full_name)
    students = list(db.scalars(select(Student).where(Student.active.is_(True))))
    if not students:
        return []

    exact = [student for student in students if student.normalized_full_name in variants]
    if exact:
        return exact

    return [student for student in students if names_compatible(full_name, student.full_name)]


def find_student_for_payer(db: Session, payer_full_name: str | None) -> MatchResult:
    variants = name_variants(payer_full_name)
    if not variants:
        return MatchResult(student=None, candidate_ids=[], reason="payer full name is missing")

    students = find_compatible_students(db, payer_full_name)

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


def find_active_duplicate(
    db: Session,
    full_name: str,
    *,
    exclude_student_id: int | None = None,
) -> Student | None:
    matches = find_compatible_students(db, full_name)
    for student in matches:
        if exclude_student_id is not None and student.id == exclude_student_id:
            continue
        return student
    return None
