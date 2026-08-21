# Validation report

Validated on 21 August 2026 with Python 3.12.13 and Node.js 24.19.0.

| Check | Result | Evidence |
|---|---|---|
| Python syntax/import compilation | PASS | `python -m compileall -q app scripts tests` |
| Ruff | PASS | `ruff check .` |
| Ruff formatting | PASS | `ruff format --check .` |
| MyPy | PASS | 50 source files |
| Unit/collector/diagnostic/triage/security/report tests | PASS | 19 tests |
| Mock triage evaluation | PASS | 80/80 controlled cases; quality gate PASS |
| Unknown handling | PASS | dedicated unit cases and 5 dataset cases |
| Secret scan | PASS | no known credential pattern detected |
| FastAPI health/create/triage/report flow | PASS | TestClient end-to-end; HTML 2,126 bytes |
| JSON/HTML/JUnit/console reporting | PASS | all formats generated for API 500 fixture |
| Node ESLint | PASS | controlled demo source |
| TypeScript type check | PASS | `tsc --noEmit` |
| Playwright test discovery | PASS | 1 Chromium controlled-flow test discovered |
| Playwright browser execution | NOT RUN LOCALLY | Chromium binary unavailable in workspace; CI installs it |
| Docker build/Compose health | NOT RUN LOCALLY | Docker runtime unavailable in workspace; CI builds image |
| GitHub Actions execution | PENDING | Runs on the published draft PR |

The 100% mock result measures deterministic controlled fixtures and framework
orchestration only; it is not evidence of real-LLM or production accuracy.

## Negative checks covered

- locator failure plus healthy application/change evidence → automation defect;
- backend 500 → API/backend;
- health down → environment;
- expired token/401 → authentication;
- invalid account state → test data;
- retry alone → not flaky;
- multiple same-context instability signals → flaky candidate;
- insufficient evidence → unknown;
- invented endpoint → unsupported claim;
- prompt-like console instruction → labelled as untrusted data;
- path traversal → blocked; and
- secret-bearing headers/text → masked.

## Delivery status

Ready for draft-PR review and CI validation. Merge should occur only after the
GitHub Python, Playwright and Docker jobs are green. No external-provider quality
claim has been made.

