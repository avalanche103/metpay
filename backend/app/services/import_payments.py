import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment, PaymentSource, PaymentStatus, Student, UnmatchedPayment
from app.services.payment_matching import (
    find_student_for_payer,
    format_full_name,
    normalize_full_name,
)


@dataclass(frozen=True)
class ImportRow:
    paid_at: datetime
    payer_full_name: str
    amount: Decimal
    currency: str
    description: str | None
    raw: dict


@dataclass
class ImportResult:
    batch_id: str
    season: str
    students_created: int
    students_existing: int
    payments_created: int
    payments_skipped: int
    payments_matched: int
    payments_needs_review: int


def parse_artpay_export_file(path: Path) -> list[ImportRow]:
    raw = pd.read_excel(path, sheet_name=0, header=0)
    data = raw[
        raw.iloc[:, 0].astype(str).str.contains(r"\d{2}\.\d{2}\.\d{4}", na=False, regex=True)
    ].copy()
    data.columns = [
        "date",
        "order_no",
        "amount",
        "currency",
        "rate",
        "amount2",
        "status",
        "last_name",
        "first_name",
        "middle_name",
        "description",
        "bin",
    ]

    rows: list[ImportRow] = []
    for record in data.to_dict(orient="records"):
        payer_full_name = str(record["order_no"]).strip()
        paid_at = pd.to_datetime(record["date"], dayfirst=True).to_pydatetime()
        amount = Decimal(str(record["amount"])).quantize(Decimal("0.01"))
        currency = str(record["currency"] or "BYN").upper()
        description = str(record["description"]).strip() if record.get("description") else None
        rows.append(
            ImportRow(
                paid_at=paid_at,
                payer_full_name=payer_full_name,
                amount=amount,
                currency=currency,
                description=description,
                raw={key: (None if pd.isna(value) else value) for key, value in record.items()},
            )
        )
    return rows


def build_external_key(row: ImportRow) -> str:
    payload = f"{row.paid_at.isoformat()}|{row.payer_full_name}|{row.amount}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def ensure_students(db: Session, names: list[str]) -> tuple[int, int]:
    created = 0
    existing = 0
    for full_name in sorted(set(names)):
        formatted_name = format_full_name(full_name)
        normalized = normalize_full_name(formatted_name)
        student = db.scalar(
            select(Student).where(
                Student.normalized_full_name == normalized,
                Student.active.is_(True),
            )
        )
        if student:
            existing += 1
            continue
        db.add(Student(full_name=formatted_name, normalized_full_name=normalized, active=True))
        created += 1
    db.flush()
    return created, existing


def import_season_payment_rows(
    db: Session,
    rows: list[ImportRow],
    *,
    season: str,
    batch_id: str | None = None,
) -> ImportResult:
    batch_id = batch_id or f"import-{season}-{uuid.uuid4().hex[:8]}"
    unique_names = [row.payer_full_name for row in rows]
    students_created, students_existing = ensure_students(db, unique_names)

    payments_created = 0
    payments_skipped = 0
    payments_matched = 0
    payments_needs_review = 0

    for row in rows:
        external_key = build_external_key(row)
        existing = db.scalar(select(Payment).where(Payment.external_key == external_key))
        if existing:
            payments_skipped += 1
            continue

        payment = Payment(
            payer_full_name=row.payer_full_name,
            normalized_payer_full_name=normalize_full_name(row.payer_full_name),
            amount=row.amount,
            currency=row.currency,
            paid_at=row.paid_at,
            status=PaymentStatus.received,
            source=PaymentSource.import_,
            season=season,
            import_batch_id=batch_id,
            external_key=external_key,
            ap_erip_trn_id=f"import:{external_key}",
            raw_payload={"import_row": row.raw, "description": row.description},
        )

        match = find_student_for_payer(db, row.payer_full_name)
        if match.student:
            payment.student_id = match.student.id
            payment.status = PaymentStatus.matched
            payments_matched += 1
        else:
            payment.status = PaymentStatus.needs_review
            payment.unmatched = UnmatchedPayment(
                reason=match.reason or "student match needs review",
                candidate_student_ids=match.candidate_ids,
            )
            payments_needs_review += 1

        db.add(payment)
        payments_created += 1

    return ImportResult(
        batch_id=batch_id,
        season=season,
        students_created=students_created,
        students_existing=students_existing,
        payments_created=payments_created,
        payments_skipped=payments_skipped,
        payments_matched=payments_matched,
        payments_needs_review=payments_needs_review,
    )


def import_season_payments(
    db: Session,
    path: Path,
    *,
    season: str,
    batch_id: str | None = None,
) -> ImportResult:
    rows = parse_artpay_export_file(path)
    return import_season_payment_rows(db, rows, season=season, batch_id=batch_id)
