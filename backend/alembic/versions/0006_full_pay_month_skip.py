"""Add payment counts_as_full and student month skips

Revision ID: 0006_full_pay_month_skip
Revises: 0005_student_profile
Create Date: 2026-09-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "0006_full_pay_month_skip"
down_revision: str | None = "0005_student_profile"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_names() -> set[str]:
    bind = op.get_bind()
    return set(inspect(bind).get_table_names())


def _column_names(table: str) -> set[str]:
    bind = op.get_bind()
    return {col["name"] for col in inspect(bind).get_columns(table)}


def upgrade() -> None:
    tables = _table_names()

    # Leftover from an interrupted SQLite batch_alter_table — blocks retries.
    if "_alembic_tmp_payments" in tables:
        op.drop_table("_alembic_tmp_payments")

    if "counts_as_full" not in _column_names("payments"):
        with op.batch_alter_table("payments") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "counts_as_full",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                )
            )

    tables = _table_names()
    if "student_month_skips" not in tables:
        op.create_table(
            "student_month_skips",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
            sa.Column("period", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.UniqueConstraint(
                "student_id", "period", name="uq_student_month_skips_student_period"
            ),
        )
        op.create_index("ix_student_month_skips_period", "student_month_skips", ["period"])

    # batch_alter can leave this behind after an interrupted or retried run
    if "_alembic_tmp_payments" in _table_names():
        op.drop_table("_alembic_tmp_payments")


def downgrade() -> None:
    tables = _table_names()
    if "student_month_skips" in tables:
        op.drop_index("ix_student_month_skips_period", table_name="student_month_skips")
        op.drop_table("student_month_skips")
    if "counts_as_full" in _column_names("payments"):
        with op.batch_alter_table("payments") as batch_op:
            batch_op.drop_column("counts_as_full")
