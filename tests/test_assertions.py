from evalforge.assertions import evaluate_response
from evalforge.models import CandidateResponse, EvaluationCase


def test_assertions_report_required_phrases_citations_and_uuid_exposure() -> None:
    case = EvaluationCase(
        id="refund-window",
        feature="support",
        scenario="policy-answer",
        prompt="What is the refund window?",
        required_phrases=("30 days",),
        minimum_citations=1,
    )
    response = CandidateResponse(
        text=(
            "You may request a refund within 30 days. "
            "Internal ID: 123e4567-e89b-12d3-a456-426614174000"
        ),
        citations=("policy.md#refunds",),
    )

    results = evaluate_response(case, response)

    assert [result.outcome for result in results] == ["pass", "pass", "fail"]
    assert results[-1].code == "no_exposed_uuid"


def test_assertions_are_case_insensitive_and_identify_missing_requirements() -> None:
    case = EvaluationCase(
        id="sources",
        feature="rag",
        scenario="grounded-answer",
        prompt="Explain the policy.",
        required_phrases=("privacy",),
        minimum_citations=2,
    )

    results = evaluate_response(case, CandidateResponse(text="The PRIVACY policy applies."))

    assert [result.outcome for result in results] == ["pass", "fail", "pass"]
