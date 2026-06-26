import sys
from datetime import date, datetime

from sqlalchemy import or_, select

from app.db import SessionLocal
from app.models import ArtPayEvent, Payment


def main() -> int:
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    amount = sys.argv[2] if len(sys.argv) > 2 else ""
    day = sys.argv[3] if len(sys.argv) > 3 else ""

    db = SessionLocal()
    try:
        query = select(Payment)
        if name:
            query = query.where(
                or_(
                    Payment.payer_full_name.ilike(f"%{name}%"),
                    Payment.normalized_payer_full_name.ilike(f"%{name.lower()}%"),
                )
            )
        if amount:
            query = query.where(Payment.amount == amount)
        if day:
            start = datetime.fromisoformat(day)
            end = datetime.combine(date.fromisoformat(day), datetime.max.time())
            query = query.where(Payment.paid_at >= start, Payment.paid_at <= end)

        payments = list(db.scalars(query.order_by(Payment.paid_at.desc())))
        print(f"payments_found: {len(payments)}")
        for payment in payments[:20]:
            print(
                f"id={payment.id} payer={payment.payer_full_name!r} "
                f"amount={payment.amount} paid_at={payment.paid_at} "
                f"status={payment.status} source={payment.source} "
                f"trn={payment.ap_erip_trn_id}"
            )

        if name:
            events = list(
                db.scalars(
                    select(ArtPayEvent).order_by(ArtPayEvent.created_at.desc()).limit(500)
                )
            )
            name_lower = name.lower()
            events = [
                event
                for event in events
                if name_lower in str(event.raw_payload).lower()
            ]
        else:
            events = list(
                db.scalars(select(ArtPayEvent).order_by(ArtPayEvent.created_at.desc()).limit(20))
            )
        print(f"artpay_events_found: {len(events)}")
        for event in events[:10]:
            print(
                f"event_id={event.id} created_at={event.created_at} "
                f"erip_trn_id={event.ap_erip_trn_id}"
            )
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
