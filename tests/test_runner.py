import json

import pytest

from evalforge.models import CandidateResponse
from evalforge.runner import load_cases, run_cases, write_report


def test_runner_loads_cases_captures_failures_and_writes_a_report(tmp_path) -> None:
    source = tmp_path / "cases.jsonl"
    source.write_text(
        json.dumps(
            {
                "id": "case-1",
                "feature": "support",
                "scenario": "policy",
                "prompt": "What is the window?",
                "required_phrases": ["30 days"],
                "minimum_citations": 1,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    report = run_cases(
        load_cases(source), lambda _: CandidateResponse(text="30 days", version="candidate-a")
    )
    destination = tmp_path / "reports" / "run.json"
    write_report(report, destination)

    saved = json.loads(destination.read_text(encoding="utf-8"))
    assert report.total == 1
    assert report.passed == 0
    assert saved["summary"]["pass_rate"] == 0.0
    assert saved["traces"][0]["assertions"][1]["code"] == "citation_count"


def test_loader_rejects_duplicate_identifiers(tmp_path) -> None:
    source = tmp_path / "cases.jsonl"
    line = json.dumps({"id": "duplicate", "feature": "f", "scenario": "s", "prompt": "q"})
    source.write_text(f"{line}\n{line}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate case ID"):
        load_cases(source)
