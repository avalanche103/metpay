from app.services.artpay.signature import (
    form_v3_signature,
    sign_v2_payload,
    verify_v2_payload,
    verify_v3_signature,
)


def test_v2_signature_excludes_signature_field() -> None:
    payload = {"ap_amount": "10.00", "ap_currency": "BYN"}
    signature = sign_v2_payload(payload, "secret")

    signed_payload = {**payload, "ap_signature": signature}

    assert verify_v2_payload(signed_payload, "secret") is True


def test_v3_signature_uses_raw_body() -> None:
    raw_body = b'{"ap_amount":"10.00","ap_currency":"BYN"}'
    signature = form_v3_signature(raw_body, "secret")

    assert verify_v3_signature(raw_body, signature, "secret") is True
    assert verify_v3_signature(raw_body + b" ", signature, "secret") is False
