from app.models import FailureEvidence, TimelineEvent


def build_timeline(evidence: FailureEvidence) -> list[TimelineEvent]:
    events = list(evidence.timeline)
    for console_event in evidence.console_errors:
        if console_event.timestamp:
            events.append(
                TimelineEvent(
                    timestamp=console_event.timestamp,
                    source="console",
                    event=f"{console_event.level}: {console_event.message}",
                )
            )
    for network_event in evidence.network_failures:
        if network_event.timestamp:
            outcome = network_event.status_code or network_event.failure_reason or "completed"
            events.append(
                TimelineEvent(
                    timestamp=network_event.timestamp,
                    source="network",
                    event=f"{network_event.method} {network_event.url} → {outcome}",
                )
            )
    for health_event in evidence.environment_health:
        if health_event.timestamp:
            events.append(
                TimelineEvent(
                    timestamp=health_event.timestamp,
                    source="health",
                    event=f"{health_event.name} is {health_event.status}",
                )
            )
    events.append(
        TimelineEvent(
            timestamp=evidence.failure.timestamp,
            source="test",
            event=f"Test {evidence.failure.status}: {evidence.failure.error_message[:200]}",
        )
    )
    return sorted(events, key=lambda item: item.timestamp)
