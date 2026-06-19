from dataclasses import dataclass
from typing import Any

from app.config import Settings
from app.services.artpay.signature import verify_v2_payload, verify_v3_signature


@dataclass(frozen=True)
class ArtPayVerification:
    valid: bool
    reason: str | None = None


class ArtPayGateway:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def verify_webhook(
        self,
        payload: dict[str, Any],
        *,
        raw_body: bytes,
        signature_header: str | None,
    ) -> ArtPayVerification:
        if self.settings.artpay_api_mode == "stub":
            return ArtPayVerification(valid=True)

        payload_store_id = str(payload.get("ap_storeid") or payload.get("ap_store_id") or "")
        if self.settings.artpay_store_id and payload_store_id != self.settings.artpay_store_id:
            return ArtPayVerification(valid=False, reason="unexpected ArtPay store id")

        if self.settings.artpay_api_mode == "v2_store":
            if verify_v2_payload(payload, self.settings.artpay_secret):
                return ArtPayVerification(valid=True)
            return ArtPayVerification(valid=False, reason="invalid ArtPay v2 signature")

        if self.settings.artpay_api_mode == "v3_epos":
            if verify_v3_signature(raw_body, signature_header, self.settings.artpay_secret):
                return ArtPayVerification(valid=True)
            return ArtPayVerification(valid=False, reason="invalid ArtPay v3 signature")

        return ArtPayVerification(valid=False, reason="unsupported ArtPay API mode")
