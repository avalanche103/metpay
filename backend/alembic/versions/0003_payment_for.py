"""Add payment_for period field

Revision ID: 0003_payment_for
Revises: 0002_payment_import_fields
Create Date: 2026-06-26
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_payment_for"
down_revision: str | None = "0002_payment_import_fields"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("payments") as batch_op:
        batch_op.add_column(sa.Column("payment_for", sa.String(length=20), nullable=True))
        batch_op.create_index("ix_payments_payment_for", ["payment_for"])


def downgrade() -> None:
    with op.batch_alter_table("payments") as batch_op:
        batch_op.drop_index("ix_payments_payment_for")
        batch_op.drop_column("payment_for")
