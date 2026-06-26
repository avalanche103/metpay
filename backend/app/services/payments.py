from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import ArtPayEvent, Payment, PaymentSource, PaymentStatus, Student, UnmatchedPayment
from app.services.payment_matching import find_student_for_payer, normalize_full_name


def extract_payer_full_name(payload: dict[str, Any]) -> str | None:
    for key in (
        "up_student_fio",
        "up_payer_fio",
        "up_child_fio",
        "ap_payer_full_name",
        "ap_payer_name",
        "ap_invoice_desc",
        "ap_erip_cust_account",
    ):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    customer_name = payload.get("ap_cust_name")
    if isinstance(customer_name, dict):
        parts = [
            customer_name.get("last_name") or customer_name.get("lastName"),
            customer_name.get("first_name") or customer_name.get("firstName"),
            customer_name.get("middle_name") or customer_name.get("middleName"),
        ]
        full_name = " ".join(str(part).strip() for part in parts if part)
        return full_name or None

    return None


def parse_amount(payload: dict[str, Any]) -> Decimal:
    try:
        return Decimal(str(payload["ap_amount"])).quantize(Decimal("0.01"))
    except (KeyError, InvalidOperation) as exc:
        raise ValueError("ap_amount is required and must be a decimal value") from exc


def parse_paid_at(payload: dict[str, Any]) -> datetime:
    value = payload.get("ap_server_dt") or payload.get("ap_client_dt")
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            pass
    return datetime.now(UTC)


def find_existing_payment(db: Session, payload: dict[str, Any]) -> Payment | None:
    trn_id = payload.get("ap_erip_trn_id")
    service_no = payload.get("ap_erip_service_no")
    invoice_id = payload.get("ap_erip_invoice_id")

    conditions = []
    if trn_id:
        conditions.append(Payment.ap_erip_trn_id == str(trn_id))
    if service_no and invoice_id:
        conditions.append(
            (Payment.ap_erip_service_no == str(service_no))
            & (Payment.ap_erip_invoice_id == str(invoice_id))
        )
    if not conditions:
        return None
    return db.scalar(select(Payment).where(or_(*conditions)))


def record_artpay_event(
    db: Session,
    payload: dict[str, Any],
    *,
    signature_valid: bool,
    duplicate: bool = False,
) -> ArtPayEvent:
    erip_trn_id = payload.get("ap_erip_trn_id")
    event = ArtPayEvent(
        event_type=str(payload.get("ap_notice_type") or payload.get("ap_request") or "unknown"),
        ap_erip_trn_id=str(erip_trn_id) if erip_trn_id else None,
        signature_valid=signature_valid,
        duplicate=duplicate,
        raw_payload=payload,
    )
    db.add(event)
    return event


def create_payment_from_artpay_payload(db: Session, payload: dict[str, Any]) -> Payment:
    payer_full_name = extract_payer_full_name(payload)
    order_num = payload.get("ap_order_num")
    erip_service_no = payload.get("ap_erip_service_no")
    erip_invoice_id = payload.get("ap_erip_invoice_id")
    erip_trn_id = payload.get("ap_erip_trn_id")
    sp_trn_id = payload.get("ap_sp_trn_id")

    payment = Payment(
        payer_full_name=payer_full_name,
        normalized_payer_full_name=normalize_full_name(payer_full_name),
        amount=parse_amount(payload),
        currency=str(payload.get("ap_currency") or "BYN").upper(),
        paid_at=parse_paid_at(payload),
        status=PaymentStatus.received,
        source=PaymentSource.webhook,
        ap_store_id=str(payload.get("ap_storeid") or payload.get("ap_store_id") or "")
        or None,
        ap_order_num=str(order_num) if order_num is not None else None,
        ap_erip_service_no=str(erip_service_no) if erip_service_no is not None else None,
        ap_erip_invoice_id=str(erip_invoice_id) if erip_invoice_id is not None else None,
        ap_erip_trn_id=str(erip_trn_id) if erip_trn_id is not None else None,
        ap_sp_trn_id=str(sp_trn_id) if sp_trn_id is not None else None,
        raw_payload=payload,
    )

    match = find_student_for_payer(db, payer_full_name)
    if match.student:
        payment.student_id = match.student.id
        payment.status = PaymentStatus.matched
    else:
        payment.status = PaymentStatus.needs_review
        payment.unmatched = UnmatchedPayment(
            reason=match.reason or "student match needs review",
            candidate_student_ids=match.candidate_ids,
        )

    db.add(payment)
    return payment


def manually_match_payment(db: Session, payment: Payment, student: Student) -> Payment:
    payment.student_id = student.id
    payment.status = PaymentStatus.matched
    if payment.unmatched:
        payment.unmatched.resolved_at = datetime.now(UTC)
    return payment
