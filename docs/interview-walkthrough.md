# Interview walkthrough

## Two-minute explanation

This project demonstrates AI-assisted test failure triage using evidence from
Playwright, network activity, application logs, environment health, history and
code changes. Deterministic diagnostics run first, AI correlates the evidence,
and a confidence-aware triage result is produced without automatically changing
source code or hiding the failed test.

## Five-minute walkthrough

1. Run the local `api_500` Playwright profile and retain its failed status.
2. Show JSON collection into typed `FailureEvidence`, including the request and correlation ID.
3. Show the deterministic 5xx rule outranking a locator explanation.
4. Run mock triage and open JSON/HTML reports with evidence for and against.
5. Run the 80-case evaluation and discuss confusion, unknowns and calibration.
6. Show secret masking, injection handling and path-traversal tests.

## Concise interview answers

- **Product vs automation?** Compare approved behaviour, locator/render evidence,
  network/health state and recent product/test changes; do not infer from the error alone.
- **Why not only an LLM?** It would lack causal evidence and could invent context.
- **Traces?** Register them and use documented reporter metadata; avoid undocumented internals.
- **Flaky tests?** Require multiple same-context historical signals; retry alone is insufficient.
- **Confidence?** Combine transparent signals and evaluate calibration; never call it truth.
- **Hallucinations?** Structured output, supplied-evidence-only prompt and claim post-validation.
- **UNKNOWN?** It is the correct safe result when causal evidence is insufficient.
- **Scale?** Store immutable artifacts externally, queue triage, partition signatures, batch metrics.
- **Jira/ADO?** Route only reviewed results through separate authenticated adapters with audit logs.
- **Auto-fix locators?** No. A patch may be suggested, but change and rerun require review.
- **Prevent hidden product defects?** Never alter the test outcome; retain counter-evidence and measure recall.

