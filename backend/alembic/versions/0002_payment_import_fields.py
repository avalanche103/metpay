"""Add payment import metadata fields

Revision ID: 0002_payment_import_fields
Revises: 0001_initial
Create Date: 2026-06-24
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_payment_import_fields"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("payments") as batch_op:
        batch_op.add_column(
            sa.Column("source", sa.String(length=20), nullable=False, server_default="webhook")
        )
        batch_op.add_column(sa.Column("season", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("import_batch_id", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("external_key", sa.String(length=64), nullable=True))
        batch_op.create_index("ix_payments_season", ["season"])
        batch_op.create_index("ix_payments_import_batch_id", ["import_batch_id"])
        batch_op.create_unique_constraint("uq_payments_external_key", ["external_key"])


def downgrade() -> None:
    with op.batch_alter_table("payments") as batch_op:
        batch_op.drop_constraint("uq_payments_external_key", type_="unique")
        batch_op.drop_index("ix_payments_import_batch_id")
        batch_op.drop_index("ix_payments_season")
        batch_op.drop_column("external_key")
        batch_op.drop_column("import_batch_id")
        batch_op.drop_column("season")
        batch_op.drop_column("source")
