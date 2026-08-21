# Observability

Structured JSON logging is configured at application startup. The pipeline has
explicit boundaries for request, collection, normalization, diagnostics,
history lookup, provider analysis, post-validation, confidence and reporting.
These boundaries are suitable for OpenTelemetry spans and optional
Phoenix/OpenInference export without coupling the core engine to an exporter.

Recommended operational metrics are triage request count, category distribution,
unknown rate, average confidence/latency, provider/model errors, evidence count,
evaluation accuracy and high-confidence accuracy. Remote provider adapters should
also capture returned input/output tokens and calculate cost from a versioned,
deployment-owned price table. The mock provider reports no invented token/cost data.

