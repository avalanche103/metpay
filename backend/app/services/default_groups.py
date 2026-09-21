from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Group, Student

# Legacy seed names that should not be auto-created anymore.
LEGACY_EMPTY_GROUP_NAMES = ("2012", "2013", "2014+")


def ensure_default_groups(db: Session) -> list[Group]:
    """Keep startup hook, but do not seed obsolete year cohorts."""
    removed = remove_empty_legacy_groups(db)
    db.commit()
    return removed


def remove_empty_legacy_groups(db: Session) -> list[Group]:
    """Delete outdated empty groups left from previous seasons."""
    removed: list[Group] = []
    for name in LEGACY_EMPTY_GROUP_NAMES:
        group = db.scalar(select(Group).where(Group.name == name))
        if not group:
            continue
        has_students = db.scalar(
            select(Student.id).where(Student.group_id == group.id).limit(1)
        )
        if has_students is not None:
            continue
        removed.append(group)
        db.delete(group)
    return removed
