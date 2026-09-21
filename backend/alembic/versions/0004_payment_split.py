"""Add payment split_group_id

Revision ID: 0004_payment_split
Revises: 0003_payment_for
Create Date: 2026-09-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_payment_split"
down_revision: str | None = "0003_payment_for"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("payments") as batch_op:
        batch_op.add_column(sa.Column("split_group_id", sa.String(length=64), nullable=True))
        batch_op.create_index("ix_payments_split_group_id", ["split_group_id"])


def downgrade() -> None:
    with op.batch_alter_table("payments") as batch_op:
        batch_op.drop_index("ix_payments_split_group_id")
        batch_op.drop_column("split_group_id")
