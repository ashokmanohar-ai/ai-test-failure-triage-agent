# Controlled Playwright failure source

The local demo is intentionally deterministic and never depends on a public site.
The normal profile passes. Each profile below creates real local Playwright artifacts
while preserving the failed exit status:

```bash
npm test
FAILURE_PROFILE=locator_change npm test
FAILURE_PROFILE=product_defect npm test
FAILURE_PROFILE=api_500 npm test
FAILURE_PROFILE=environment_down npm test
FAILURE_PROFILE=invalid_test_data npm test
FAILURE_PROFILE=flaky_timing npm test
FAILURE_PROFILE=auth_expired npm test
FAILURE_PROFILE=slow_endpoint npm test
```

`playwright-report.json`, screenshots and retained traces are inputs to the Python
collector. Generated artifacts are ignored by Git and are not presented as historical
production evidence.

