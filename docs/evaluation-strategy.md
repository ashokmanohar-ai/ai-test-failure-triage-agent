# Evaluation strategy

The committed dataset contains 80 sanitized controlled cases: 15 automation,
15 product, 10 API/backend, 10 environment, 10 test-data, 10 flaky, 5
authentication and 5 unknown.

The runner reports primary accuracy, category precision/recall/F1, confusion
matrix, required root-cause fact recall, high-confidence accuracy, unknown
precision and correctness in confidence bins. `config/evaluation.yaml` versions
the quality gate and baseline. Regression is meaningful only when dataset,
taxonomy, provider and prompt versions are held constant.

Mock-provider PASS demonstrates framework/rule behaviour only. It does not
establish real-LLM quality or general model superiority. Production adoption
requires a representative held-out dataset labelled through independent review.

