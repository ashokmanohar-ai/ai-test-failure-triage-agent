from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class FailureCategory(StrEnum):
    PRODUCT_DEFECT = "PRODUCT_DEFECT"
    AUTOMATION_DEFECT = "AUTOMATION_DEFECT"
    FLAKY_TEST = "FLAKY_TEST"
    TEST_DATA = "TEST_DATA"
    ENVIRONMENT = "ENVIRONMENT"
    NETWORK = "NETWORK"
    API_BACKEND = "API_BACKEND"
    AUTHENTICATION = "AUTHENTICATION"
    DEPENDENCY = "DEPENDENCY"
    BROWSER = "BROWSER"
    PERFORMANCE_TIMEOUT = "PERFORMANCE_TIMEOUT"
    ASSERTION_DEFECT = "ASSERTION_DEFECT"
    CONFIGURATION = "CONFIGURATION"
    UNKNOWN = "UNKNOWN"


class FailureRecord(BaseModel):
    failure_id: str = Field(min_length=1, max_length=128)
    test_id: str = Field(min_length=1, max_length=256)
    test_name: str = Field(min_length=1, max_length=512)
    suite: str = "default"
    status: Literal["FAILED", "TIMED_OUT"] = "FAILED"
    error_message: str = Field(min_length=1, max_length=20_000)
    stack_trace: str | None = None
    duration_ms: int = Field(default=0, ge=0)
    retry_count: int = Field(default=0, ge=0)
    browser: str | None = None
    project: str | None = None
    environment: str | None = None
    commit_sha: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConsoleEvent(BaseModel):
    level: str
    message: str
    timestamp: datetime | None = None


class NetworkFailure(BaseModel):
    method: str = "GET"
    url: str
    status_code: int | None = None
    failure_reason: str | None = None
    duration_ms: int | None = Field(default=None, ge=0)
    correlation_id: str | None = None
    timestamp: datetime | None = None


class HealthCheck(BaseModel):
    name: str
    url: str | None = None
    status: Literal["UP", "DOWN", "DEGRADED", "UNKNOWN"]
    latency_ms: int | None = Field(default=None, ge=0)
    detail: str | None = None
    timestamp: datetime | None = None


class CodeChange(BaseModel):
    path: str
    change_type: Literal["ADDED", "MODIFIED", "DELETED", "RENAMED"] = "MODIFIED"
    commit_sha: str | None = None
    summary: str | None = None


class HistoricalFailure(BaseModel):
    signature: str
    classification: FailureCategory
    root_cause: str
    occurrence_count: int = Field(ge=1)
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    similarity: float = Field(default=1.0, ge=0, le=1)
    retry_recovered: bool = False
    same_commit: bool = False
    same_environment: bool = False


class DiagnosticFinding(BaseModel):
    rule_id: str
    category: FailureCategory
    subcategory: str | None = None
    score: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    explanation: str


class TimelineEvent(BaseModel):
    timestamp: datetime
    source: str
    event: str


class FailureEvidence(BaseModel):
    failure: FailureRecord
    screenshot_paths: list[str] = Field(default_factory=list)
    trace_path: str | None = None
    console_errors: list[ConsoleEvent] = Field(default_factory=list)
    network_failures: list[NetworkFailure] = Field(default_factory=list)
    page_url: str | None = None
    environment_health: list[HealthCheck] = Field(default_factory=list)
    recent_changes: list[CodeChange] = Field(default_factory=list)
    historical_failures: list[HistoricalFailure] = Field(default_factory=list)
    deterministic_findings: list[DiagnosticFinding] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TriageResult(BaseModel):
    failure_id: str
    primary_classification: FailureCategory
    secondary_classifications: list[FailureCategory] = Field(default_factory=list)
    subcategory: str | None = None
    confidence: float = Field(ge=0, le=1)
    confidence_band: Literal["HIGH", "MEDIUM", "LOW"]
    failure_symptom: str
    probable_technical_cause: str
    probable_root_cause: str
    evidence_for: list[str]
    evidence_against: list[str]
    recommended_actions: list[str]
    requires_human_review: bool = True
    unsupported_claims: list[str] = Field(default_factory=list)
    prompt_version: str = "triage-agent/v1"
    model_provider: str = "mock"
    model_name: str = "mock-evidence-v1"
    deterministic_score: float = Field(default=0, ge=0, le=1)
    historical_score: float = Field(default=0, ge=0, le=1)
    agreement_score: float = Field(default=0, ge=0, le=1)
    model_score: float = Field(default=0, ge=0, le=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("secondary_classifications")
    @classmethod
    def unique_secondary(cls, value: list[FailureCategory]) -> list[FailureCategory]:
        return list(dict.fromkeys(value))


class TriageEvaluationCase(BaseModel):
    id: str
    evidence_fixture: str
    expected_primary_classification: FailureCategory
    accepted_secondary: list[FailureCategory] = Field(default_factory=list)
    expected_root_cause_facts: list[str] = Field(default_factory=list)
    min_confidence: float | None = Field(default=None, ge=0, le=1)
    tags: list[str] = Field(default_factory=list)


class PlaywrightImportRequest(BaseModel):
    report_path: str = Field(min_length=1, max_length=1024)
