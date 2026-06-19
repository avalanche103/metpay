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

Run tests:

```powershell
cd backend
pytest
```

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
