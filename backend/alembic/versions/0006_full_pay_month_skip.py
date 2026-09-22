"""Add payment counts_as_full and student month skips

Revision ID: 0006_full_pay_month_skip
Revises: 0005_student_profile
Create Date: 2026-09-22
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_full_pay_month_skip"
down_revision: str | None = "0005_student_profile"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("payments") as batch_op:
        batch_op.add_column(
            sa.Column(
                "counts_as_full",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    op.create_table(
        "student_month_skips",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("student_id", "period", name="uq_student_month_skips_student_period"),
    )
    op.create_index("ix_student_month_skips_period", "student_month_skips", ["period"])


def downgrade() -> None:
    op.drop_index("ix_student_month_skips_period", table_name="student_month_skips")
    op.drop_table("student_month_skips")
    with op.batch_alter_table("payments") as batch_op:
        batch_op.drop_column("counts_as_full")
