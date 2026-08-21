# Flaky-test analysis

Retry success is a useful observation, not proof. The indicator combines:

- repeated pass/fail or root-cause variation;
- recovery under retry;
- same commit, environment and data context;
- absence of relevant source/environment changes; and
- historical signature behaviour.

`≥ 0.80` means likely flaky, `0.50–0.79` possible flaky, and below `0.50`
insufficient evidence. A stable failure that begins after a product change and
continues on retry is deliberately protected from a flaky label. Teams should
preserve artifacts, reproduce under controlled context and use reviewed
quarantine policies rather than increasing timeouts reflexively.

