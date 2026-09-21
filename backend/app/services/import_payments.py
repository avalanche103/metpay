import hashlib
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment, PaymentSource, PaymentStatus, Student, UnmatchedPayment
from app.services.payment_matching import (
    find_compatible_students,
    find_student_for_payer,
    format_full_name,
    normalize_full_name,
    prefer_fuller_name,
)

DATE_PREFIX_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}")


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


def _to_import_row(
    *,
    paid_at: datetime,
    payer_full_name: str,
    amount: Decimal,
    currency: str,
    description: str | None,
    raw: dict,
) -> ImportRow:
    return ImportRow(
        paid_at=paid_at,
        payer_full_name=payer_full_name,
        amount=amount,
        currency=currency,
        description=description,
        raw=raw,
    )


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
            _to_import_row(
                paid_at=paid_at,
                payer_full_name=payer_full_name,
                amount=amount,
                currency=currency,
                description=description,
                raw={key: (None if pd.isna(value) else value) for key, value in record.items()},
            )
        )
    return rows


def _split_clipboard_line(line: str) -> list[str]:
    if "\t" in line:
        return [part.strip() for part in line.split("\t")]
    return [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]


def parse_artpay_clipboard_text(text: str) -> list[ImportRow]:
    """Parse ArtPay table copied from browser/excel (TSV or multi-space columns)."""
    rows: list[ImportRow] = []
    for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw_line.strip()
        if not line or not DATE_PREFIX_RE.match(line):
            continue

        parts = _split_clipboard_line(line)
        if len(parts) < 3:
            continue

        payer_full_name = parts[1].strip()
        if not payer_full_name or payer_full_name.lower() in {"итого", "total"}:
            continue

        try:
            paid_at = pd.to_datetime(parts[0], dayfirst=True).to_pydatetime()
            amount = Decimal(str(parts[2]).replace(",", ".")).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError, ValueError):
            continue

        currency = str(parts[3] if len(parts) > 3 and parts[3] else "BYN").upper()
        status = parts[6].strip() if len(parts) > 6 and parts[6] else None
        description = status or f"Заказ №: {payer_full_name}"
        rows.append(
            _to_import_row(
                paid_at=paid_at,
                payer_full_name=payer_full_name,
                amount=amount,
                currency=currency,
                description=description,
                raw={
                    "date": parts[0],
                    "order_no": payer_full_name,
                    "amount": str(parts[2]),
                    "currency": currency,
                    "rate": parts[4] if len(parts) > 4 else None,
                    "amount2": parts[5] if len(parts) > 5 else None,
                    "status": status,
                    "source": "clipboard",
                },
            )
        )
    return rows


def build_external_key(row: ImportRow) -> str:
    payload = f"{row.paid_at.isoformat()}|{row.payer_full_name}|{row.amount}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def ensure_students(db: Session, names: list[str]) -> tuple[int, int]:
    created = 0
    existing = 0
    # Longer FIO first so short variants reuse the fuller student record.
    ordered_names = sorted(
        set(names),
        key=lambda value: (-len(normalize_full_name(value).split()), normalize_full_name(value)),
    )
    for full_name in ordered_names:
        formatted_name = format_full_name(full_name)
        normalized = normalize_full_name(formatted_name)
        matches = find_compatible_students(db, formatted_name)
        if matches:
            student = matches[0]
            fuller = prefer_fuller_name(student.full_name, formatted_name)
            if normalize_full_name(fuller) != student.normalized_full_name:
                student.full_name = fuller
                student.normalized_full_name = normalize_full_name(fuller)
            existing += 1
            continue
        db.add(Student(full_name=formatted_name, normalized_full_name=normalized, active=True))
        db.flush()
        created += 1
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


def import_season_payments_from_text(
    db: Session,
    text: str,
    *,
    season: str,
    batch_id: str | None = None,
) -> tuple[ImportResult, int]:
    rows = parse_artpay_clipboard_text(text)
    result = import_season_payment_rows(db, rows, season=season, batch_id=batch_id)
    return result, len(rows)
