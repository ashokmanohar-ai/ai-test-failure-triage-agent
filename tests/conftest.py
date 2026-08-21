from datetime import UTC, datetime

import pytest

from app.models import FailureEvidence, FailureRecord


@pytest.fixture
def evidence() -> FailureEvidence:
    return FailureEvidence(
        failure=FailureRecord(
            failure_id="FAIL-TEST",
            test_id="test-checkout",
            test_name="checkout",
            suite="e2e",
            error_message="Unexpected failure",
            timestamp=datetime.now(UTC),
        )
    )
