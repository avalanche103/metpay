"""Add student profile fields

Revision ID: 0005_student_profile
Revises: 0004_payment_split
Create Date: 2026-09-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_student_profile"
down_revision: str | None = "0004_payment_split"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("students") as batch_op:
        batch_op.add_column(sa.Column("birth_date", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("passport_number", sa.String(length=64), nullable=True))
        batch_op.add_column(
            sa.Column("passport_personal_number", sa.String(length=64), nullable=True)
        )
        batch_op.add_column(sa.Column("passport_issued_at", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("passport_issued_by", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("address", sa.String(length=512), nullable=True))
        batch_op.add_column(
            sa.Column("educational_institution", sa.String(length=255), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("students") as batch_op:
        batch_op.drop_column("educational_institution")
        batch_op.drop_column("address")
        batch_op.drop_column("passport_issued_by")
        batch_op.drop_column("passport_issued_at")
        batch_op.drop_column("passport_personal_number")
        batch_op.drop_column("passport_number")
        batch_op.drop_column("birth_date")
