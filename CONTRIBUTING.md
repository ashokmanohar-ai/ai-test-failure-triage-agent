# Contributing

1. Create a focused branch and never commit credentials or generated test artifacts.
2. Install `.[dev]`, then run Ruff, formatting, MyPy and Pytest.
3. Add deterministic fixtures for every new diagnostic rule, including counter-evidence.
4. Run the full mock evaluation and explain any baseline change.
5. Keep model output structured and preserve `UNKNOWN` plus human-review behaviour.
6. Open a draft pull request with validation evidence and security impact.

New framework adapters should normalize into `FailureEvidence`; they must not
introduce provider-specific logic into deterministic diagnostics.

