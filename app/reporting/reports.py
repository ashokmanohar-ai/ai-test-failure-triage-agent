import html
import json
from pathlib import Path
from xml.etree import ElementTree as ET

from app.models import FailureEvidence, TriageResult


def render_console(result: TriageResult, evidence: FailureEvidence) -> str:
    evidence_lines = "\n".join(f"  + {item}" for item in result.evidence_for)
    actions = "\n".join(
        f"  {index}. {item}" for index, item in enumerate(result.recommended_actions, 1)
    )
    return f"""AI TEST FAILURE TRIAGE

Failure: {result.failure_id}
Test: {evidence.failure.test_name}
Classification: {result.primary_classification}
Confidence: {result.confidence:.0%} ({result.confidence_band})
Probable Root Cause: {result.probable_root_cause}

Evidence:
{evidence_lines}

Recommended Actions:
{actions}

Human Review: {"Required" if result.requires_human_review else "Auto-route suggestion allowed; approval still required"}"""


def write_json(result: TriageResult, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.model_dump(mode="json"), indent=2), encoding="utf-8")
    return path


def write_html(result: TriageResult, evidence: FailureEvidence, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    esc = html.escape
    items = lambda values: "".join(f"<li>{esc(str(value))}</li>" for value in values)  # noqa: E731
    timeline = items(
        f"{item.timestamp.isoformat()} — {item.source}: {item.event}"
        for item in sorted(evidence.timeline, key=lambda event: event.timestamp)
    )
    network = items(
        f"{n.method} {n.url} → {n.status_code or n.failure_reason}"
        for n in evidence.network_failures
    )
    console = items(f"{e.level}: {e.message}" for e in evidence.console_errors)
    findings = items(
        f"{f.rule_id}: {f.category} ({f.score:.2f}) — {f.explanation}"
        for f in evidence.deterministic_findings
    )
    document = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Triage {esc(result.failure_id)}</title><style>body{{font:16px system-ui;max-width:1050px;margin:2rem auto;padding:0 1rem;color:#182230}}header{{background:#0b1f3a;color:white;padding:1.5rem;border-radius:12px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}}section{{border:1px solid #d8dee9;border-radius:10px;padding:1rem;margin-top:1rem}}.badge{{background:#dbeafe;color:#1e3a8a;padding:.2rem .6rem;border-radius:1rem}}code{{overflow-wrap:anywhere}}</style></head><body><header><h1>AI Test Failure Triage</h1><p>{esc(result.failure_id)} · {esc(evidence.failure.test_name)}</p><p><span class="badge">{esc(str(result.primary_classification))}</span> {result.confidence:.0%} ({result.confidence_band})</p></header><div class="grid"><section><h2>Symptom</h2><p>{esc(result.failure_symptom)}</p><h2>Technical cause</h2><p>{esc(result.probable_technical_cause)}</p></section><section><h2>Probable root cause</h2><p>{esc(result.probable_root_cause)}</p><p><b>Human review:</b> {result.requires_human_review}</p></section></div><section><h2>Evidence for</h2><ul>{items(result.evidence_for)}</ul><h2>Evidence against</h2><ul>{items(result.evidence_against)}</ul></section><section><h2>Network</h2><ul>{network or "<li>None supplied</li>"}</ul><h2>Console</h2><ul>{console or "<li>None supplied</li>"}</ul></section><section><h2>Deterministic findings</h2><ul>{findings or "<li>None</li>"}</ul><h2>Timeline</h2><ul>{timeline or "<li>None supplied</li>"}</ul></section><section><h2>Recommended actions</h2><ol>{items(result.recommended_actions)}</ol></section><footer><p>Prompt {esc(result.prompt_version)} · Provider {esc(result.model_provider)} · Model {esc(result.model_name)}</p><p>Triage is diagnostic and never changes the original test result.</p></footer></body></html>"""
    path.write_text(document, encoding="utf-8")
    return path


def write_junit(result: TriageResult, evidence: FailureEvidence, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    suite = ET.Element("testsuite", name="ai-test-failure-triage", tests="1", failures="1")
    case = ET.SubElement(
        suite, "testcase", name=evidence.failure.test_name, classname=evidence.failure.suite
    )
    failure = ET.SubElement(
        case, "failure", type=str(result.primary_classification), message=result.probable_root_cause
    )
    failure.text = "\n".join(result.evidence_for)
    path.write_bytes(ET.tostring(suite, encoding="utf-8", xml_declaration=True))
    return path
