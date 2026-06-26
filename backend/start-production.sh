#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "[*] Creating MetPay virtual environment..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[*] Installing MetPay dependencies..."
python -m pip install -e . -q

METPAY_PORT="${METPAY_PORT:-8000}"
echo "[*] Starting MetPay on 127.0.0.1:${METPAY_PORT}"

exec python -m uvicorn app.main:app --host 127.0.0.1 --port "${METPAY_PORT}"
