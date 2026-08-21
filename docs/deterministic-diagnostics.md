# Deterministic diagnostics

Rules run before model analysis because high-signal facts should not depend on
prompt wording. Each rule returns a category candidate, subcategory, evidence,
counter-evidence, explanation and bounded score.

- 401/403 plus session evidence → authentication candidate
- backend 5xx → API/backend candidate
- failed/degraded health check → environment candidate
- locator cardinality plus UI change → automation/locator candidate
- slow request plus timeout → performance-timeout candidate
- expected/actual mismatch plus product change → product candidate
- invalid or expired controlled record → test-data candidate
- browser/page termination → browser candidate
- retry recovery plus same-context instability and history → flaky candidate

Rules do not claim universal truth. Competing findings reduce cross-evidence
agreement. A bare timeout remains `UNKNOWN`; a retry pass alone is insufficient.

