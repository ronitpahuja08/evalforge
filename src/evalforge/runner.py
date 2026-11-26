"""Offline case loading, execution, and reproducible trace reports."""

import json
from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import asdict
from pathlib import Path
from time import perf_counter
from typing import Any

from evalforge.assertions import evaluate_response
from evalforge.models import CandidateResponse, EvaluationCase, EvaluationReport, EvaluationTrace

Candidate = Callable[[str], CandidateResponse]


def load_cases(path: Path) -> tuple[EvaluationCase, ...]:
    """Load a JSONL suite while rejecting malformed lines and duplicate IDs."""
    cases: list[EvaluationCase] = []
    seen_ids: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as error:
            msg = f"invalid JSON on line {line_number}"
            raise ValueError(msg) from error
        if not isinstance(raw, dict):
            raise ValueError(f"case must be a JSON object on line {line_number}")
        case = EvaluationCase(
            id=_string(raw, "id", line_number),
            feature=_string(raw, "feature", line_number),
            scenario=_string(raw, "scenario", line_number),
            prompt=_string(raw, "prompt", line_number),
            required_phrases=_strings(
                raw.get("required_phrases", []), "required_phrases", line_number
            ),
            minimum_citations=_integer(
                raw.get("minimum_citations", 0), "minimum_citations", line_number
            ),
            tags=_strings(raw.get("tags", []), "tags", line_number),
        )
        if case.id in seen_ids:
            raise ValueError(f"duplicate case ID: {case.id}")
        seen_ids.add(case.id)
        cases.append(case)
    if not cases:
        raise ValueError("evaluation suite must contain at least one case")
    return tuple(cases)


def run_cases(cases: Iterable[EvaluationCase], candidate: Candidate) -> EvaluationReport:
    """Execute a candidate once per case and capture assertion-level evidence."""
    traces: list[EvaluationTrace] = []
    for case in cases:
        started = perf_counter()
        response = candidate(case.prompt)
        duration_ms = (perf_counter() - started) * 1_000
        traces.append(
            EvaluationTrace(
                case_id=case.id,
                feature=case.feature,
                scenario=case.scenario,
                candidate_version=response.version,
                response=response,
                assertions=evaluate_response(case, response),
                duration_ms=duration_ms,
            )
        )
    return EvaluationReport(traces=tuple(traces))


def write_report(report: EvaluationReport, path: Path) -> None:
    """Write a stable JSON artifact suitable for a CI upload or later comparison."""
    payload = {
        "summary": summarize_report(report),
        "traces": [
            {
                "case_id": trace.case_id,
                "feature": trace.feature,
                "scenario": trace.scenario,
                "passed": trace.passed,
                "candidate_version": trace.candidate_version,
                "response": {
                    "text": trace.response.text,
                    "citations": list(trace.response.citations),
                },
                "assertions": [asdict(result) for result in trace.assertions],
                "duration_ms": trace.duration_ms,
                "created_at": trace.created_at,
            }
            for trace in report.traces
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarize_report(report: EvaluationReport) -> dict[str, object]:
    """Aggregate outcomes by feature and assertion for regression tracking."""
    feature_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "passed": 0})
    assertion_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "passed": 0})
    for trace in report.traces:
        feature_totals[trace.feature]["total"] += 1
        feature_totals[trace.feature]["passed"] += int(trace.passed)
        for result in trace.assertions:
            assertion_totals[result.code]["total"] += 1
            assertion_totals[result.code]["passed"] += int(result.outcome == "pass")
    return {
        "total": report.total,
        "passed": report.passed,
        "pass_rate": report.pass_rate,
        "by_feature": dict(feature_totals),
        "by_assertion": dict(assertion_totals),
    }


def _string(raw: dict[str, Any], field: str, line_number: int) -> str:
    value = raw.get(field)
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string on line {line_number}")
    return value


def _strings(value: object, field: str, line_number: int) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings on line {line_number}")
    return tuple(value)


def _integer(value: object, field: str, line_number: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field} must be an integer on line {line_number}")
    return value
