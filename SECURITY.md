# Security policy

## Supported version

The latest release/`main` branch receives security fixes.

## Report a vulnerability

Use GitHub private vulnerability reporting. Do not open a public issue containing
credentials, personal data, exploit artifacts or customer logs.

## Security boundaries

Evidence is untrusted. The framework masks common secrets/PII, labels prompt-like
instructions as data, restricts artifact paths, never executes imported content,
validates structured model output, flags unsupported endpoint claims and blocks
unsafe recommendations. The container runs non-root with reduced privileges.

Pattern-based redaction is not a formal DLP system and cannot guarantee removal
of every organization-specific identifier. Configure upstream artifact filtering,
least-privilege credentials, retention controls, encryption, network egress policy,
RBAC and audit logging before production use. ZIP import is not enabled in the
reference API; any future implementation must enforce size/type limits and zip-slip prevention.

