"""Add payment note for manual payment method

Revision ID: 0007_payment_note
Revises: 0006_full_pay_month_skip
Create Date: 2026-10-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "0007_payment_note"
down_revision: str | None = "0006_full_pay_month_skip"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _column_names(table: str) -> set[str]:
    bind = op.get_bind()
    return {col["name"] for col in inspect(bind).get_columns(table)}


def upgrade() -> None:
    if "note" not in _column_names("payments"):
        with op.batch_alter_table("payments") as batch_op:
            batch_op.add_column(sa.Column("note", sa.String(length=255), nullable=True))


def downgrade() -> None:
    if "note" in _column_names("payments"):
        with op.batch_alter_table("payments") as batch_op:
            batch_op.drop_column("note")
