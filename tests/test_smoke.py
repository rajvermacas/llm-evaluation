from typer.testing import CliRunner

from llm_evaluator.cli import app


def test_cli_help_exposes_evaluate_command() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "evaluate" in result.stdout
