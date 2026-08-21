# Evidence model

`FailureEvidence` is the unit supplied to diagnostics and the model provider.

| Evidence | Purpose | Trust treatment |
|---|---|---|
| Failure/error/stack | Symptom and failed action | Length-limited, sanitized |
| Screenshot path | Human visual evidence | Root-bound path; no required OCR |
| Playwright trace | Actions, timing, linked evidence | Registered, not reverse engineered |
| Console errors | Page/runtime symptoms | Secret/PII masking; injection labels |
| Network failures | Endpoint/status/timing/correlation | Sensitive headers excluded |
| Environment health | Separate infrastructure from product | Failure cannot be silently ignored |
| Recent changes | Plausible impact relation | Collected from Git, never invented |
| History/signature | Recurrence and stability context | Current evidence still required |
| Timeline | Temporal correlation | Built only from timestamped evidence |

Facts and hypotheses remain separate in `TriageResult`: failure symptom,
technical cause, probable root cause, evidence for and evidence against.

