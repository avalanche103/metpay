from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Group
from app.schemas import GroupCreate, GroupRead

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(payload: GroupCreate, db: Session = Depends(get_db)) -> Group:
    group = Group(**payload.model_dump())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("", response_model=list[GroupRead])
def list_groups(db: Session = Depends(get_db)) -> list[Group]:
    return list(db.scalars(select(Group).order_by(Group.name)))


@router.get("/{group_id}", response_model=GroupRead)
def get_group(group_id: int, db: Session = Depends(get_db)) -> Group:
    group = db.get(Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group was not found")
    return group
