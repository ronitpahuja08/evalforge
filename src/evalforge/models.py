"""Validated, immutable contracts for evaluation inputs and outputs."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

Outcome = Literal["pass", "fail"]


def _required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be blank")
    return normalized


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    """One representative user task with observable success conditions."""

    id: str
    feature: str
    scenario: str
    prompt: str
    required_phrases: tuple[str, ...] = ()
    minimum_citations: int = 0
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("id", "feature", "scenario", "prompt"):
            object.__setattr__(self, field_name, _required(getattr(self, field_name), field_name))
        if self.minimum_citations < 0:
            raise ValueError("minimum_citations must be non-negative")
        phrases = tuple(_required(phrase, "required_phrase") for phrase in self.required_phrases)
        object.__setattr__(self, "required_phrases", phrases)
        object.__setattr__(self, "tags", tuple(_required(tag, "tag") for tag in self.tags))


@dataclass(frozen=True, slots=True)
class CandidateResponse:
    """Candidate output kept separate from the evaluator's expectations."""

    text: str
    citations: tuple[str, ...] = ()
    version: str = "local"

    def __post_init__(self) -> None:
        object.__setattr__(self, "text", _required(self.text, "text"))
        object.__setattr__(self, "version", _required(self.version, "version"))
        citations = tuple(_required(item, "citation") for item in self.citations)
        object.__setattr__(self, "citations", citations)


@dataclass(frozen=True, slots=True)
class AssertionResult:
    code: str
    outcome: Outcome
    detail: str


@dataclass(frozen=True, slots=True)
class EvaluationTrace:
    case_id: str
    feature: str
    scenario: str
    candidate_version: str
    response: CandidateResponse
    assertions: tuple[AssertionResult, ...]
    duration_ms: float
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def passed(self) -> bool:
        return all(result.outcome == "pass" for result in self.assertions)


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    traces: tuple[EvaluationTrace, ...]

    @property
    def total(self) -> int:
        return len(self.traces)

    @property
    def passed(self) -> int:
        return sum(trace.passed for trace in self.traces)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0
