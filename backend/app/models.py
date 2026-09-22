from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class PaymentStatus(StrEnum):
    received = "received"
    matched = "matched"
    needs_review = "needs_review"
    ignored = "ignored"
    duplicate = "duplicate"


class PaymentSource(StrEnum):
    webhook = "webhook"
    import_ = "import"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Group(TimestampMixin, Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    monthly_fee: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    students: Mapped[list["Student"]] = relationship(back_populates="group")


class Student(TimestampMixin, Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_full_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    passport_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    passport_personal_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    passport_issued_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    passport_issued_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    educational_institution: Mapped[str | None] = mapped_column(String(255), nullable=True)

    group: Mapped[Group | None] = relationship(back_populates="students")
    parents: Mapped[list["Parent"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(back_populates="student")
    month_skips: Mapped[list["StudentMonthSkip"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_students_name_active", "normalized_full_name", "active"),
    )


class Parent(TimestampMixin, Base):
    __tablename__ = "parents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    student: Mapped[Student] = relationship(back_populates="parents")


class Payment(TimestampMixin, Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)
    payer_full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    normalized_payer_full_name: Mapped[str | None] = mapped_column(
        String(255), index=True, nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BYN")
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), default=PaymentStatus.received, nullable=False
    )
    source: Mapped[PaymentSource] = mapped_column(
        Enum(PaymentSource), default=PaymentSource.webhook, nullable=False
    )
    season: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    payment_for: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    counts_as_full: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    import_batch_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    external_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    split_group_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)

    ap_store_id: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ap_order_num: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ap_erip_service_no: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ap_erip_invoice_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ap_erip_trn_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ap_sp_trn_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    student: Mapped[Student | None] = relationship(back_populates="payments")
    unmatched: Mapped["UnmatchedPayment | None"] = relationship(
        back_populates="payment", cascade="all, delete-orphan", uselist=False
    )

    __table_args__ = (
        UniqueConstraint("ap_erip_trn_id", name="uq_payments_ap_erip_trn_id"),
        Index("ix_payments_erip_invoice", "ap_erip_service_no", "ap_erip_invoice_id"),
    )


class StudentMonthSkip(TimestampMixin, Base):
    __tablename__ = "student_month_skips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False)

    student: Mapped[Student] = relationship(back_populates="month_skips")

    __table_args__ = (
        UniqueConstraint("student_id", "period", name="uq_student_month_skips_student_period"),
        Index("ix_student_month_skips_period", "period"),
    )


class UnmatchedPayment(TimestampMixin, Base):
    __tablename__ = "unmatched_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payments.id"), unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    candidate_student_ids: Mapped[list[int]] = mapped_column(JSON, nullable=False, default=list)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    payment: Mapped[Payment] = relationship(back_populates="unmatched")


class ArtPayEvent(TimestampMixin, Base):
    __tablename__ = "artpay_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ap_erip_trn_id: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    signature_valid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
