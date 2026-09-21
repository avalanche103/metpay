from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import PaymentSource, PaymentStatus


class GroupCreate(BaseModel):
    name: str
    monthly_fee: Decimal | None = None
    active: bool = True


class GroupUpdate(BaseModel):
    name: str | None = None
    monthly_fee: Decimal | None = None
    active: bool | None = None


class GroupRead(GroupCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ParentCreate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    email: str | None = None


class StudentCreate(BaseModel):
    full_name: str
    group_id: int | None = None
    active: bool = True
    parents: list[ParentCreate] = Field(default_factory=list)


class StudentUpdate(BaseModel):
    full_name: str | None = None
    group_id: int | None = None
    active: bool | None = None


class StudentMergeRequest(BaseModel):
    target_student_id: int


class ParentRead(ParentCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class StudentRead(BaseModel):
    id: int
    full_name: str
    normalized_full_name: str
    group_id: int | None
    group_name: str | None = None
    active: bool
    parents: list[ParentRead] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class PaymentRead(BaseModel):
    id: int
    student_id: int | None
    payer_full_name: str | None
    amount: Decimal
    currency: str
    paid_at: datetime | None
    status: PaymentStatus
    source: PaymentSource
    season: str | None
    payment_for: str | None
    split_group_id: str | None = None
    ap_erip_service_no: str | None
    ap_erip_invoice_id: str | None
    ap_erip_trn_id: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaymentUpdate(BaseModel):
    payment_for: str | None = None


class PaymentSplitPart(BaseModel):
    amount: Decimal = Field(gt=0)
    payment_for: str | None = None


class PaymentSplitRequest(BaseModel):
    parts: list[PaymentSplitPart] = Field(min_length=2)


class ManualMatchRequest(BaseModel):
    student_id: int


class ClipboardImportRequest(BaseModel):
    text: str = Field(min_length=1)
    season: str = "2026/2027"
    batch_id: str | None = None


class ClipboardImportResult(BaseModel):
    batch_id: str
    season: str
    rows_parsed: int
    students_created: int
    students_existing: int
    payments_created: int
    payments_skipped: int
    payments_matched: int
    payments_needs_review: int


class ArtPayWebhookResult(BaseModel):
    status: str
    payment_id: int | None = None
    duplicate: bool = False
    matched_student_id: int | None = None
    review_reason: str | None = None
