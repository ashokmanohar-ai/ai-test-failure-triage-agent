import time
from datetime import UTC, datetime

import httpx

from app.models import HealthCheck


async def collect_health(name: str, url: str, *, timeout_seconds: float = 3.0) -> HealthCheck:
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=False) as client:
            response = await client.get(url)
        latency = int((time.perf_counter() - started) * 1000)
        if response.status_code >= 500:
            status = "DOWN"
        elif response.status_code >= 400 or latency > timeout_seconds * 800:
            status = "DEGRADED"
        else:
            status = "UP"
        return HealthCheck(
            name=name,
            url=url,
            status=status,
            latency_ms=latency,
            detail=f"HTTP {response.status_code}",
            timestamp=datetime.now(UTC),
        )
    except httpx.HTTPError as exc:
        return HealthCheck(
            name=name,
            url=url,
            status="DOWN",
            detail=type(exc).__name__,
            timestamp=datetime.now(UTC),
        )
