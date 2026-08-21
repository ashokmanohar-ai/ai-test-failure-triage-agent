import asyncio
import json
from pathlib import Path

from app.config import Settings
from app.evaluation import run_evaluation
from app.llm import create_provider
from app.triage import FailureTriageAgent


async def main() -> int:
    agent = FailureTriageAgent(create_provider(Settings(model_provider="mock")))
    report = await run_evaluation(agent, Path("datasets/triage/cases.json"), Path.cwd())
    Path("reports").mkdir(exist_ok=True)
    Path("reports/evaluation.json").write_text(
        json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8"
    )
    print(f"TRIAGE QUALITY GATE: {'PASS' if report.quality_gate_passed else 'FAIL'}")
    print(f"Overall Accuracy: {report.overall_accuracy:.1%}")
    return 0 if report.quality_gate_passed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
