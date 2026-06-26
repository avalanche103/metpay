from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import PaymentSource, PaymentStatus


class GroupCreate(BaseModel):
    name: str
    monthly_fee: Decimal | None = None
    active: bool = True


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
    ap_erip_service_no: str | None
    ap_erip_invoice_id: str | None
    ap_erip_trn_id: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class PaymentUpdate(BaseModel):
    payment_for: str | None = None


class ManualMatchRequest(BaseModel):
    student_id: int


class ArtPayWebhookResult(BaseModel):
    status: str
    payment_id: int | None = None
    duplicate: bool = False
    matched_student_id: int | None = None
    review_reason: str | None = None
