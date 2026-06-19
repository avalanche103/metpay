import json
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.schemas import ArtPayWebhookResult
from app.services.artpay.client import ArtPayGateway
from app.services.payments import (
    create_payment_from_artpay_payload,
    find_existing_payment,
    record_artpay_event,
)

router = APIRouter(prefix="/webhooks/artpay", tags=["artpay-webhooks"])


@router.post("", response_model=ArtPayWebhookResult)
async def receive_artpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    ap_content_signature: str | None = Header(default=None),
) -> ArtPayWebhookResult:
    raw_body = await request.body()
    try:
        payload: dict[str, Any] = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from exc

    gateway = ArtPayGateway(settings)
    verification = gateway.verify_webhook(
        payload,
        raw_body=raw_body,
        signature_header=ap_content_signature,
    )
    if not verification.valid:
        record_artpay_event(db, payload, signature_valid=False)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=verification.reason or "Invalid ArtPay signature",
        )

    existing_payment = find_existing_payment(db, payload)
    if existing_payment:
        record_artpay_event(db, payload, signature_valid=True, duplicate=True)
        db.commit()
        return ArtPayWebhookResult(
            status="duplicate",
            payment_id=existing_payment.id,
            duplicate=True,
            matched_student_id=existing_payment.student_id,
        )

    if payload.get("ap_erip_trn_state") and payload.get("ap_erip_trn_state") != "Paid":
        record_artpay_event(db, payload, signature_valid=True)
        db.commit()
        return ArtPayWebhookResult(status="ignored")

    try:
        payment = create_payment_from_artpay_payload(db, payload)
    except ValueError as exc:
        record_artpay_event(db, payload, signature_valid=True)
        db.commit()
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    record_artpay_event(db, payload, signature_valid=True)
    db.commit()
    db.refresh(payment)

    return ArtPayWebhookResult(
        status=payment.status.value,
        payment_id=payment.id,
        matched_student_id=payment.student_id,
        review_reason=payment.unmatched.reason if payment.unmatched else None,
    )
