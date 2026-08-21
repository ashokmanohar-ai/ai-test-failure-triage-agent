import asyncio
import json
from pathlib import Path

import typer

from app.collectors.playwright_results import collect_playwright_json
from app.config import Settings
from app.evaluation.runner import run_evaluation
from app.llm import create_provider
from app.models import FailureEvidence
from app.reporting import render_console, write_html, write_json, write_junit
from app.triage import FailureTriageAgent

app = typer.Typer(no_args_is_help=True, help="Evidence-first automated-test failure triage")


def _agent(provider: str) -> FailureTriageAgent:
    settings = Settings(model_provider=provider)
    return FailureTriageAgent(create_provider(settings))


@app.command()
def analyze(
    artifact: Path = typer.Option(
        ..., exists=True, readable=True, help="FailureEvidence JSON or Playwright JSON report"
    ),
    provider: str = typer.Option("mock", help="mock, azure_openai, or openai"),
    output_dir: Path = typer.Option(Path("reports")),
    playwright: bool = typer.Option(False, help="Parse as Playwright JSON reporter output"),
) -> None:
    """Analyze one or more failed tests and generate JSON, HTML and JUnit reports."""
    evidence_records = (
        collect_playwright_json(artifact)
        if playwright
        else [FailureEvidence.model_validate_json(artifact.read_text(encoding="utf-8"))]
    )

    async def execute() -> None:
        triage_agent = _agent(provider)
        for evidence in evidence_records:
            result = await triage_agent.triage(evidence)
            stem = result.failure_id
            write_json(result, output_dir / f"{stem}.json")
            write_html(result, evidence, output_dir / f"{stem}.html")
            write_junit(result, evidence, output_dir / f"{stem}.xml")
            typer.echo(render_console(result, evidence))

    asyncio.run(execute())


@app.command()
def evaluate(
    dataset: Path = typer.Option(Path("datasets/triage/cases.json"), exists=True),
    provider: str = typer.Option("mock"),
    output: Path = typer.Option(Path("reports/evaluation.json")),
) -> None:
    """Run the repeatable triage benchmark and enforce the quality gate."""

    async def execute() -> None:
        report = await run_evaluation(_agent(provider), dataset, Path.cwd())
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
        typer.echo(f"Overall accuracy: {report.overall_accuracy:.1%}")
        typer.echo(f"High-confidence accuracy: {report.high_confidence_accuracy:.1%}")
        typer.echo(f"Quality gate: {'PASS' if report.quality_gate_passed else 'FAIL'}")
        if not report.quality_gate_passed:
            for failure in report.gate_failures:
                typer.echo(f"- {failure}")
            raise typer.Exit(code=1)

    asyncio.run(execute())


if __name__ == "__main__":
    app()
