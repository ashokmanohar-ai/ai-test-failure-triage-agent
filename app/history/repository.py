import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from app.models import FailureCategory, HistoricalFailure


class SignatureRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        with sqlite3.connect(path) as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS failure_signatures (
                signature TEXT PRIMARY KEY, classification TEXT NOT NULL, root_cause TEXT NOT NULL,
                resolved_by TEXT, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
                occurrence_count INTEGER NOT NULL, tests_affected TEXT NOT NULL)""")

    def record(
        self,
        signature: str,
        classification: FailureCategory,
        root_cause: str,
        test_id: str,
        resolved_by: str | None = None,
    ) -> None:
        now = datetime.now(UTC).isoformat()
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """INSERT INTO failure_signatures(signature, classification, root_cause, resolved_by, first_seen, last_seen, occurrence_count, tests_affected)
                VALUES(?, ?, ?, ?, ?, ?, 1, ?)
                ON CONFLICT(signature) DO UPDATE SET classification=excluded.classification, root_cause=excluded.root_cause,
                resolved_by=COALESCE(excluded.resolved_by, failure_signatures.resolved_by), last_seen=excluded.last_seen,
                occurrence_count=failure_signatures.occurrence_count+1,
                tests_affected=CASE WHEN instr(failure_signatures.tests_affected, excluded.tests_affected)=0 THEN failure_signatures.tests_affected||','||excluded.tests_affected ELSE failure_signatures.tests_affected END""",
                (signature, str(classification), root_cause, resolved_by, now, now, test_id),
            )

    def exact_match(self, signature: str) -> HistoricalFailure | None:
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                "SELECT signature, classification, root_cause, occurrence_count, first_seen, last_seen FROM failure_signatures WHERE signature=?",
                (signature,),
            ).fetchone()
        if not row:
            return None
        return HistoricalFailure(
            signature=row[0],
            classification=FailureCategory(row[1]),
            root_cause=row[2],
            occurrence_count=row[3],
            first_seen=datetime.fromisoformat(row[4]),
            last_seen=datetime.fromisoformat(row[5]),
            similarity=1.0,
        )
