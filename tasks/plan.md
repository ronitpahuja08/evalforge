# Implementation Plan: EvalForge

## Overview

EvalForge is a local-first Python toolkit for evaluating AI and RAG workflows. It begins with fast deterministic checks, representative JSONL datasets, structured traces, and reproducible score reports. The design follows the evaluation loop described in Hamel Husain's article: test specific behaviors cheaply, inspect failures with traces, then use reviewed examples to calibrate richer evaluators.

## Architecture Decisions

- Store evaluation cases and run artifacts as JSONL so examples are easy to review, diff, and version.
- Keep the core evaluator provider-independent and deterministic; model judges are adapters introduced only after human-review infrastructure exists.
- Treat every result as an immutable trace with case ID, candidate version, assertion outcomes, and timing.
- Produce machine-readable reports first, with a small terminal summary for local feedback and CI.

## Today: Foundation Build

1. Bootstrap the Python package and quality tooling.
2. Define validated contracts for cases, candidate outputs, traces, and reports.
3. Implement deterministic response and citation assertions.
4. Build a runner that executes a candidate against JSONL cases.
5. Persist traces and calculate per-criterion score summaries.
6. Add an offline CLI demo, representative seed cases, tests, and documentation.

## Next Five Days

### Day 2 — Dataset quality and scenario coverage

- [ ] Add dataset manifests, tags, scenario coverage checks, and stable case IDs.
- [ ] Add dataset validation and duplicate/near-duplicate detection.
- [ ] Add regression baselines with explicit pass-rate thresholds.

### Day 3 — Trace inspection and human review

- [ ] Add trace filtering by feature, scenario, failure code, and candidate version.
- [ ] Add a review queue with binary labels, critiques, and desired-answer fields.
- [ ] Add CSV export/import with schema validation for lightweight human review.

### Day 4 — Model-judge and RAG evaluation adapters

- [ ] Define a typed judge-provider protocol and a deterministic fake judge for tests.
- [ ] Measure judge-vs-human precision and recall instead of raw agreement.
- [ ] Add retrieval relevance, citation correctness, and groundedness criteria.

### Day 5 — Change tracking and CI

- [ ] Compare two report artifacts and classify improvements, regressions, and inconclusive changes.
- [ ] Publish JSON and Markdown run summaries as CI artifacts.
- [ ] Add a GitHub Actions workflow that enforces the regression threshold.

### Day 6 — Experiment readiness and release polish

- [ ] Add experiment assignment and outcome schemas for future A/B analysis.
- [ ] Add runbook documentation for failure triage and evaluator calibration.
- [ ] Add an end-to-end example and release checklist.

## Checkpoints

- [ ] After today: offline demo runs, tests pass, and a JSON report identifies failing criteria.
- [ ] After Day 3: a reviewer can label and critique a failed trace without editing source code.
- [ ] After Day 5: CI rejects measurable regressions and preserves report artifacts.
- [ ] After Day 6: the README demonstrates the complete evaluate → inspect → improve loop.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Metrics optimize the wrong behavior | High | Keep cases feature-specific and review failures regularly. |
| Model judges drift from human judgment | High | Track precision/recall against human labels and retain critiques. |
| Sensitive prompts or outputs appear in traces | High | Make trace persistence explicit and document redaction hooks before hosted integrations. |
| Unstable model calls make CI noisy | Medium | Keep deterministic assertions as the CI gate; run model judges on a separate cadence. |

