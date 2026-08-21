from pathlib import Path

import pytest

from app.llm.mock import MockProvider
from app.reporting import write_html, write_json, write_junit
from app.triage import FailureTriageAgent


@pytest.mark.asyncio
async def test_all_report_formats_are_generated(tmp_path: Path, evidence):
    result = await FailureTriageAgent(MockProvider()).triage(evidence)
    assert write_json(result, tmp_path / "report.json").exists()
    assert write_html(result, evidence, tmp_path / "report.html").exists()
    assert write_junit(result, evidence, tmp_path / "report.xml").exists()
