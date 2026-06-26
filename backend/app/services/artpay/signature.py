import hashlib
import hmac
import json
from typing import Any


def canonical_json(payload: dict[str, Any], *, exclude_signature: bool = True) -> str:
    data = dict(payload)
    if exclude_signature:
        data.pop("ap_signature", None)
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sign_message(message: str | bytes, secret: str, *, algorithm: str = "sha256") -> str:
    if isinstance(message, str):
        message = message.encode("utf-8")
    digestmod = hashlib.sha512 if algorithm == "sha512" else hashlib.sha256
    return hmac.new(secret.encode("utf-8"), message, digestmod).hexdigest()


def sign_v2_payload(payload: dict[str, Any], secret: str) -> str:
    return sign_message(canonical_json(payload), secret)


def verify_v2_payload(payload: dict[str, Any], secret: str) -> bool:
    received_signature = str(payload.get("ap_signature", ""))
    if not received_signature:
        return False
    expected_signature = sign_v2_payload(payload, secret)
    return hmac.compare_digest(expected_signature, received_signature)


def form_v3_signature(raw_body: bytes, secret: str, key_index: str = "1") -> str:
    return f"{key_index}.{sign_message(raw_body, secret)}"


def verify_v3_signature(raw_body: bytes, signature_header: str | None, secret: str) -> bool:
    if not signature_header or "." not in signature_header:
        return False
    key_index, _ = signature_header.split(".", 1)
    expected_signature = form_v3_signature(raw_body, secret, key_index)
    return hmac.compare_digest(expected_signature, signature_header.strip('"'))


def verify_v2_payload_with_secrets(payload: dict[str, Any], secrets: list[str]) -> bool:
    return any(verify_v2_payload(payload, secret) for secret in secrets)


def verify_v3_signature_with_secrets(
    raw_body: bytes,
    signature_header: str | None,
    secrets: list[str],
) -> bool:
    if not signature_header or "." not in signature_header:
        return False
    key_index, _ = signature_header.split(".", 1)
    index = int(key_index) if key_index.isdigit() else 1
    if 1 <= index <= len(secrets):
        return verify_v3_signature(raw_body, signature_header, secrets[index - 1])
    return any(verify_v3_signature(raw_body, signature_header, secret) for secret in secrets)
