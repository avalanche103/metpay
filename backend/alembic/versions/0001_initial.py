"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-19
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("monthly_fee", sa.Numeric(12, 2), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("normalized_full_name", sa.String(length=255), nullable=False),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("groups.id"), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_students_name_active", "students", ["normalized_full_name", "active"])
    op.create_table(
        "parents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("students.id"), nullable=True),
        sa.Column("payer_full_name", sa.String(length=255), nullable=True),
        sa.Column("normalized_payer_full_name", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("ap_store_id", sa.String(length=30), nullable=True),
        sa.Column("ap_order_num", sa.String(length=64), nullable=True),
        sa.Column("ap_erip_service_no", sa.String(length=30), nullable=True),
        sa.Column("ap_erip_invoice_id", sa.String(length=64), nullable=True),
        sa.Column("ap_erip_trn_id", sa.String(length=64), nullable=True),
        sa.Column("ap_sp_trn_id", sa.String(length=64), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("ap_erip_trn_id", name="uq_payments_ap_erip_trn_id"),
    )
    op.create_index(
        "ix_payments_erip_invoice",
        "payments",
        ["ap_erip_service_no", "ap_erip_invoice_id"],
    )
    op.create_index(
        "ix_payments_normalized_payer_full_name",
        "payments",
        ["normalized_payer_full_name"],
    )
    op.create_table(
        "unmatched_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "payment_id",
            sa.Integer(),
            sa.ForeignKey("payments.id"),
            unique=True,
            nullable=False,
        ),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("candidate_student_ids", sa.JSON(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "artpay_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("ap_erip_trn_id", sa.String(length=64), nullable=True),
        sa.Column("signature_valid", sa.Boolean(), nullable=False),
        sa.Column("duplicate", sa.Boolean(), nullable=False),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_artpay_events_ap_erip_trn_id", "artpay_events", ["ap_erip_trn_id"])


def downgrade() -> None:
    op.drop_index("ix_artpay_events_ap_erip_trn_id", table_name="artpay_events")
    op.drop_table("artpay_events")
    op.drop_table("unmatched_payments")
    op.drop_index("ix_payments_normalized_payer_full_name", table_name="payments")
    op.drop_index("ix_payments_erip_invoice", table_name="payments")
    op.drop_table("payments")
    op.drop_table("parents")
    op.drop_index("ix_students_name_active", table_name="students")
    op.drop_table("students")
    op.drop_table("groups")
