from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Group

DEFAULT_GROUPS: list[dict[str, object]] = [
    {"name": "2012", "monthly_fee": Decimal("120.00")},
    {"name": "2013", "monthly_fee": Decimal("120.00")},
    {"name": "2014+", "monthly_fee": Decimal("120.00")},
]


def ensure_default_groups(db: Session) -> list[Group]:
    groups: list[Group] = []
    for item in DEFAULT_GROUPS:
        group = db.scalar(select(Group).where(Group.name == item["name"]))
        if not group:
            group = Group(
                name=str(item["name"]),
                monthly_fee=item["monthly_fee"],  # type: ignore[arg-type]
                active=True,
            )
            db.add(group)
        groups.append(group)
    db.commit()
    for group in groups:
        db.refresh(group)
    return groups
