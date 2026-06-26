import argparse
import sys
from pathlib import Path

from app.db import SessionLocal
from app.migrations import run_migrations
from app.services.import_payments import import_season_payments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import ArtPay season payments from XLS export")
    parser.add_argument("file", type=Path, help="Path to ArtPay XLS export")
    parser.add_argument("--season", default="2025/2026", help="Season label, e.g. 2025/2026")
    parser.add_argument("--batch-id", default=None, help="Optional import batch id")
    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1

    run_migrations()
    db = SessionLocal()
    try:
        result = import_season_payments(
            db,
            args.file,
            season=args.season,
            batch_id=args.batch_id,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"batch_id: {result.batch_id}")
    print(f"season: {result.season}")
    print(f"students_created: {result.students_created}")
    print(f"students_existing: {result.students_existing}")
    print(f"payments_created: {result.payments_created}")
    print(f"payments_skipped: {result.payments_skipped}")
    print(f"payments_matched: {result.payments_matched}")
    print(f"payments_needs_review: {result.payments_needs_review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
