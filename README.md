# EvalForge

EvalForge is a local-first evaluation harness for AI and RAG workflows. It starts with the parts that should be cheap and dependable: representative cases, explicit success criteria, deterministic assertions, structured traces, and reproducible reports.

It is intentionally provider-independent. A candidate can be an LLM application, a RAG pipeline, or a deterministic function used in tests.

## Today’s vertical slice

- JSONL evaluation cases with feature and scenario labels
- deterministic answer and citation assertions
- immutable per-case traces and JSON reports
- a terminal runner for an offline demo

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m ruff check src tests
python -m evalforge.cli run examples/support_cases.jsonl --report reports/demo.json
```

The [implementation plan](tasks/plan.md) describes the next five days: dataset coverage, human review, model-judge calibration, CI regression gates, and experiment readiness.

## Report artifacts

Each run produces JSON with an overall pass rate plus breakdowns by feature and assertion. Every trace retains the candidate version, response, citations, assertion outcomes, duration, and timestamp. That makes failures inspectable instead of collapsing them into one opaque score.

The included `support_cases.jsonl` is deliberately small but representative: each case carries the feature, scenario, success phrases, citation requirement, and tags that future coverage checks will use.

## Principles

1. Make success criteria specific to the user task.
2. Keep fast deterministic checks in the edit loop.
3. Preserve traces so failures can be inspected and reviewed.
4. Treat human labels as the reference for calibrating automatic judges.

