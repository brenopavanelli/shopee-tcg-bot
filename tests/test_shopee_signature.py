from tcgbot.shopee_client import build_signature, build_auth_header


def test_signature_is_deterministic():
    sig1 = build_signature("app123", "secret456", 1700000000, '{"a":1}')
    sig2 = build_signature("app123", "secret456", 1700000000, '{"a":1}')
    assert sig1 == sig2


def test_signature_changes_when_payload_changes():
    sig1 = build_signature("app123", "secret456", 1700000000, '{"a":1}')
    sig2 = build_signature("app123", "secret456", 1700000000, '{"a":2}')
    assert sig1 != sig2


def test_auth_header_format():
    header = build_auth_header("app123", "secret456", 1700000000, '{"a":1}')
    assert header.startswith("SHA256 Credential=app123, Timestamp=1700000000, Signature=")