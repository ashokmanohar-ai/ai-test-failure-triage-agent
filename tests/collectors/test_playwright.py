import json
from pathlib import Path

from app.collectors.playwright_results import collect_playwright_json


def test_parses_failed_playwright_result(tmp_path: Path):
    report = {
        "suites": [
            {
                "title": "checkout",
                "specs": [
                    {
                        "id": "spec-1",
                        "title": "places order",
                        "tests": [
                            {
                                "projectName": "chromium",
                                "results": [
                                    {
                                        "status": "failed",
                                        "duration": 123,
                                        "retry": 0,
                                        "errors": [{"message": "boom", "stack": "trace"}],
                                        "attachments": [{"name": "screenshot", "path": "shot.png"}],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    records = collect_playwright_json(path)
    assert len(records) == 1
    assert records[0].failure.test_id == "spec-1"
    assert records[0].screenshot_paths == ["shot.png"]
