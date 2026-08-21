from app.diagnostics import run_diagnostics
from app.models import CodeChange, FailureCategory, HealthCheck, HistoricalFailure, NetworkFailure


def category(evidence):
    return run_diagnostics(evidence)[0].category


def test_locator_with_healthy_app_and_ui_change_is_automation(evidence):
    evidence.failure.error_message = "locator('Checkout') resolved to 0 elements"
    evidence.environment_health = [HealthCheck(name="app", status="UP")]
    evidence.recent_changes = [CodeChange(path="src/components/CheckoutButton.tsx")]
    assert category(evidence) == FailureCategory.AUTOMATION_DEFECT


def test_backend_500_ranks_api_backend(evidence):
    evidence.network_failures = [
        NetworkFailure(method="POST", url="http://app/api/orders", status_code=500)
    ]
    assert category(evidence) == FailureCategory.API_BACKEND


def test_environment_down(evidence):
    evidence.environment_health = [HealthCheck(name="app", status="DOWN")]
    assert category(evidence) == FailureCategory.ENVIRONMENT


def test_expired_auth(evidence):
    evidence.failure.error_message = "expired token redirected to login"
    evidence.network_failures = [NetworkFailure(url="http://app/api/session", status_code=401)]
    assert category(evidence) == FailureCategory.AUTHENTICATION


def test_invalid_data(evidence):
    evidence.failure.error_message = "Invalid account state: account expired"
    assert category(evidence) == FailureCategory.TEST_DATA


def test_retry_alone_is_not_flaky(evidence):
    evidence.failure.retry_count = 1
    assert not any(f.category == FailureCategory.FLAKY_TEST for f in run_diagnostics(evidence))


def test_multiple_independent_signals_can_flag_flaky(evidence):
    evidence.failure.retry_count = 1
    evidence.historical_failures = [
        HistoricalFailure(
            signature="a",
            classification="FLAKY_TEST",
            root_cause="timing",
            occurrence_count=2,
            retry_recovered=True,
            same_commit=True,
            same_environment=True,
        ),
        HistoricalFailure(
            signature="b",
            classification="FLAKY_TEST",
            root_cause="render",
            occurrence_count=2,
            retry_recovered=True,
            same_commit=True,
            same_environment=True,
        ),
    ]
    assert category(evidence) == FailureCategory.FLAKY_TEST


def test_consistent_post_change_failure_is_not_flaky(evidence):
    evidence.failure.retry_count = 1
    evidence.recent_changes = [CodeChange(path="src/domain/order.py")]
    assert not any(f.category == FailureCategory.FLAKY_TEST for f in run_diagnostics(evidence))
