# MetPay

Service for accounting incoming football class payments received through ERIP via ArtPay.

## Backend

The initial implementation is a FastAPI monolith with SQLite.

Quick start on Windows:

```bat
start.bat
```

The script creates `.venv` if needed, installs dependencies, copies `.env.example` to `.env`, starts
the server, and opens the payments UI.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
copy .env.example .env
uvicorn app.main:app --reload
```

Open the payments web interface:

```text
http://127.0.0.1:8000/payments-ui
```

## Integration with teling.by

If MetPay runs on the same server as the Next.js site (`H:\Teling2026\teling2026`), the site proxies:

```text
POST https://teling.by/api/webhooks/artpay
```

to the local MetPay backend on port `8000`.

Production startup:

```bash
cd backend
bash start-production.sh
```

Or let `teling2026/start-production.sh` start MetPay automatically when `../MetPay` is present.

In ArtPay, configure the notification URL:

```text
https://teling.by/api/webhooks/artpay
```

Run tests:

```powershell
cd backend
pytest
```

## Season import (historical payments)

Recommended rollout order:

1. Import students and season payments from the ArtPay XLS export.
2. Review the `needs_review` queue (typos, duplicate names).
3. Enable the ArtPay webhook so new payments are recorded on top of history.
4. Use season reports in the UI or API.

Import command:

```powershell
cd backend
python -m app.import_season "..\Платежи за год.XLS" --season "2025/2026"
```

The importer auto-creates students from unique payer names, sets `source=import` and
`season=2025/2026`, and skips duplicates on re-run.

Reports:

```text
GET /api/reports/by-student?season=2025/2026
GET /api/reports/by-month?season=2025/2026
GET /api/reports/needs-review
```

The payments UI (`/payments-ui`) shows both reports for the selected season.

## ArtPay Flow

Parents pay directly in ERIP and enter the student's full name. ArtPay sends a webhook to:

```text
POST /api/webhooks/artpay
```

In `ARTPAY_API_MODE=stub`, signatures are skipped so local test payloads can be posted manually. In
`v2_store`, the service verifies the `ap_signature` field. In `v3_epos`, it verifies the
`ap-content-signature` header against the raw request body.

Payments are matched to students by normalized full name. Ambiguous or unknown names are stored with
`needs_review` status and can be manually linked through:

```text
POST /api/payments/{payment_id}/match
```
