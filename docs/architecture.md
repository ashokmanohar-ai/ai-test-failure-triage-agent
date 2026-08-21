# Architecture

## Runtime flow

```mermaid
sequenceDiagram
    participant PW as Playwright
    participant C as Collector
    participant D as Diagnostics
    participant M as Provider
    participant V as Validator
    participant R as Report
    PW->>C: JSON, trace, screenshot, logs
    C->>D: Sanitized FailureEvidence
    D->>M: Findings + history + changes
    M->>V: Structured TriageResult
    V->>R: Supported claims + confidence
    R-->>PW: Diagnostic artifact; failure unchanged
```

Collectors use structured reporter data when available. Sanitization and path
validation occur at the trust boundary. Deterministic rules produce scored
candidates before model reasoning. Exact historical signatures add corroborating
evidence; a previous classification is never automatically copied.

The provider abstraction validates every response with Pydantic. The
post-validator detects unsupported endpoint claims and unsafe actions.
Confidence is recomputed from documented components, not accepted from model
self-report. All non-high outputs and every unsupported claim require review.

SQLite is the reference persistence implementation. FastAPI, CLI, reporting and
evaluation call the same `FailureTriageAgent`, avoiding separate behaviour paths.

