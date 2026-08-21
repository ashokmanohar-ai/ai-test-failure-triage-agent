# Confidence model

The score is an evidence-strength indicator:

`0.40 × deterministic + 0.25 × historical + 0.20 × agreement + 0.15 × provider`

`HIGH ≥ 0.85`, `MEDIUM ≥ 0.65`, otherwise `LOW`. `UNKNOWN` is capped below
high/medium auto-routing. Unsupported claims force human review.

This number is not a probability until calibrated against a representative,
independently labelled production dataset. Evaluation reports accuracy per
confidence bin so overconfident mistakes are visible. Organization-specific
data, provider versions, prompt versions and taxonomy changes require
recalibration.

