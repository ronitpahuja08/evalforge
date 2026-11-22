import sys

from evalforge import cli


def test_cli_runs_demo_suite_and_writes_report(tmp_path, monkeypatch, capsys) -> None:
    suite = tmp_path / "suite.jsonl"
    suite.write_text(
        '{"id":"refund","feature":"support","scenario":"policy","prompt":"refund window",'
        '"required_phrases":["30 days"],"minimum_citations":1}\n',
        encoding="utf-8",
    )
    report = tmp_path / "report.json"
    monkeypatch.setattr(sys, "argv", ["evalforge", "run", str(suite), "--report", str(report)])

    assert cli.main() == 0
    assert report.exists()
    assert "1/1 cases passed" in capsys.readouterr().out
