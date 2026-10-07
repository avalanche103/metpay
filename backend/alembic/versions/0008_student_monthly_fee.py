"""Add optional per-student monthly fee override

Revision ID: 0008_student_monthly_fee
Revises: 0007_payment_note
Create Date: 2026-10-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "0008_student_monthly_fee"
down_revision: str | None = "0007_payment_note"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _column_names(table: str) -> set[str]:
    bind = op.get_bind()
    return {col["name"] for col in inspect(bind).get_columns(table)}


def upgrade() -> None:
    if "monthly_fee" not in _column_names("students"):
        with op.batch_alter_table("students") as batch_op:
            batch_op.add_column(
                sa.Column("monthly_fee", sa.Numeric(12, 2), nullable=True)
            )


def downgrade() -> None:
    if "monthly_fee" in _column_names("students"):
        with op.batch_alter_table("students") as batch_op:
            batch_op.drop_column("monthly_fee")
