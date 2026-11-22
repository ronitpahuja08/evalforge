import pytest

from evalforge.models import CandidateResponse, EvaluationCase


def test_case_normalizes_required_fields_and_tags() -> None:
    case = EvaluationCase(
        id=" support-1 ",
        feature=" support ",
        scenario=" citation-required ",
        prompt=" What is the refund window? ",
        required_phrases=("30 days",),
        minimum_citations=1,
        tags=(" policy ",),
    )

    assert case.id == "support-1"
    assert case.tags == ("policy",)


def test_models_reject_blank_values_and_negative_citation_requirements() -> None:
    with pytest.raises(ValueError, match="prompt"):
        EvaluationCase(id="case", feature="feature", scenario="scenario", prompt=" ")
    with pytest.raises(ValueError, match="minimum_citations"):
        EvaluationCase(
            id="case",
            feature="feature",
            scenario="scenario",
            prompt="question",
            minimum_citations=-1,
        )
    with pytest.raises(ValueError, match="text"):
        CandidateResponse(text=" ")
