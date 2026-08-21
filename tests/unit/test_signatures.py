from app.history.signatures import build_signature


def test_dynamic_ids_normalize_to_same_signature(evidence):
    evidence.failure.error_message = "Timeout waiting for order-87362"
    first = build_signature(evidence)
    evidence.failure.error_message = "Timeout waiting for order-92741"
    assert build_signature(evidence) == first
