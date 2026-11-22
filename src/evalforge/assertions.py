"""Fast deterministic checks reusable in CI and candidate retries."""

import re

from evalforge.models import AssertionResult, CandidateResponse, EvaluationCase

_UUID_PATTERN = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE
)


def evaluate_response(
    case: EvaluationCase, response: CandidateResponse
) -> tuple[AssertionResult, ...]:
    """Evaluate explicit case requirements without a model call."""
    normalized_text = response.text.casefold()
    phrase_results = tuple(
        AssertionResult(
            code="required_phrase",
            outcome="pass" if phrase.casefold() in normalized_text else "fail",
            detail=f"required phrase: {phrase}",
        )
        for phrase in case.required_phrases
    )
    citation_result = AssertionResult(
        code="citation_count",
        outcome="pass" if len(response.citations) >= case.minimum_citations else "fail",
        detail=f"expected at least {case.minimum_citations}; received {len(response.citations)}",
    )
    uuid_result = AssertionResult(
        code="no_exposed_uuid",
        outcome="fail" if _UUID_PATTERN.search(response.text) else "pass",
        detail="response must not expose internal UUIDs",
    )
    return (*phrase_results, citation_result, uuid_result)
