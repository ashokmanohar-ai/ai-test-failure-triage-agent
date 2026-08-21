# Failure taxonomy

| Category | Definition / typical signals | Counter-evidence | Recommended owner |
|---|---|---|---|
| PRODUCT_DEFECT | Approved behaviour is violated; assertion and product evidence agree | Expectation or data is unverified | Product engineering |
| AUTOMATION_DEFECT | Locator, wait, test logic or shared state is wrong | UI is genuinely missing/broken | QE automation |
| FLAKY_TEST | Outcome varies under controlled equivalent context | Stable repeatable signature/change | QE + owning team |
| TEST_DATA | Missing, expired, duplicate or invalid controlled state | Same data works independently | Test-data owner |
| ENVIRONMENT | Health, configuration or resources prevent execution | All components healthy | Platform/SRE |
| NETWORK | DNS, TLS, proxy, reset or transport failure | Valid response reached client | Network/platform |
| API_BACKEND | Correlated request returns backend error | UI failed before request | Service owner |
| AUTHENTICATION | 401/403, expiry, storage state or login redirect | Session remains valid | Identity/platform |
| DEPENDENCY | Downstream service failure causes symptom | Dependency is healthy | Dependency owner |
| BROWSER | Launch/crash/context/page lifecycle failure | App fails outside browser too | QE/platform |
| PERFORMANCE_TIMEOUT | Latency exceeds expectation/SLO | Locator never exists | Product/SRE |
| ASSERTION_DEFECT | Expectation conflicts with approved requirement | Product output is incorrect | QE |
| CONFIGURATION | Runtime settings differ from approved baseline | Configuration verified | Platform |
| UNKNOWN | Evidence cannot distinguish credible causes | New decisive evidence | Triage owner |

Subcategories capture technical specificity without expanding primary routing.

