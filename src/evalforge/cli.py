"""Small local CLI for running deterministic evaluation suites."""

import argparse
from pathlib import Path

from evalforge.models import CandidateResponse
from evalforge.runner import load_cases, run_cases, write_report


def demo_candidate(prompt: str) -> CandidateResponse:
    """Offline stand-in that makes the repository runnable without an API key."""
    normalized = prompt.casefold()
    if "refund" in normalized:
        return CandidateResponse(
            text="You can request a refund within 30 days of purchase.",
            citations=("support-policy.md#refunds",),
            version="demo-v1",
        )
    return CandidateResponse(
        text="Account deletion is completed within 7 days after verification.",
        citations=("privacy-policy.md#deletion",),
        version="demo-v1",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local EvalForge JSONL suites.")
    subcommands = parser.add_subparsers(dest="command", required=True)
    run = subcommands.add_parser(
        "run", help="run an evaluation suite using the offline demo candidate"
    )
    run.add_argument("suite", type=Path)
    run.add_argument("--report", type=Path, required=True)
    arguments = parser.parse_args()

    if arguments.command == "run":
        report = run_cases(load_cases(arguments.suite), demo_candidate)
        write_report(report, arguments.report)
        print(f"{report.passed}/{report.total} cases passed ({report.pass_rate:.0%})")
        for trace in report.traces:
            if not trace.passed:
                failed_codes = ", ".join(
                    result.code for result in trace.assertions if result.outcome == "fail"
                )
                print(f"FAIL {trace.case_id}: {failed_codes}")
        return 0 if report.passed == report.total else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
