import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.models import FailureEvidence, TriageResult


class FailureRepository:
    """Small SQLite repository; PostgreSQL can be supplied behind the same service boundary."""

    def __init__(self, path: Path = Path("triage.db")) -> None:
        self.path = path
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS failures (failure_id TEXT PRIMARY KEY, evidence_json TEXT NOT NULL, triage_json TEXT)"
            )

    def save_evidence(self, evidence: FailureEvidence) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO failures(failure_id, evidence_json) VALUES(?, ?) ON CONFLICT(failure_id) DO UPDATE SET evidence_json=excluded.evidence_json",
                (evidence.failure.failure_id, evidence.model_dump_json()),
            )

    def save_triage(self, result: TriageResult) -> None:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE failures SET triage_json=? WHERE failure_id=?",
                (result.model_dump_json(), result.failure_id),
            )
            if cursor.rowcount == 0:
                raise KeyError(result.failure_id)

    def get_evidence(self, failure_id: str) -> FailureEvidence:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT evidence_json FROM failures WHERE failure_id=?", (failure_id,)
            ).fetchone()
        if not row:
            raise KeyError(failure_id)
        return FailureEvidence.model_validate_json(row[0])

    def get_triage(self, failure_id: str) -> TriageResult | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT triage_json FROM failures WHERE failure_id=?", (failure_id,)
            ).fetchone()
        if not row:
            raise KeyError(failure_id)
        return TriageResult.model_validate_json(row[0]) if row[0] else None

    def list_failures(self) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT failure_id, evidence_json, triage_json FROM failures ORDER BY failure_id DESC"
            ).fetchall()
        return [
            {
                "failure_id": row[0],
                "test_name": json.loads(row[1])["failure"]["test_name"],
                "triaged": row[2] is not None,
            }
            for row in rows
        ]
