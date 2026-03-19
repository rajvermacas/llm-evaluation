from pathlib import Path

from typer.testing import CliRunner

from llm_evaluator.cli import app


class FakeWorkflow:
    """Test workflow that captures CLI invocation state."""

    def __init__(self) -> None:
        self.received_state: dict | None = None

    def invoke(self, state: dict) -> None:
        """Record the incoming workflow state."""
        self.received_state = state


def test_evaluate_loads_openrouter_api_key_from_dotenv(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        (
            "teacher_model: teacher-model\n"
            "candidate_models:\n"
            "  - candidate-a\n"
            "problem_statement: Solve the task.\n"
            "benchmark_case_count: 1\n"
            f"output_dir: {tmp_path / 'artifacts'}\n"
        ),
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text(
        "OPENROUTER_API_KEY=dotenv-test-key\n",
        encoding="utf-8",
    )
    fake_workflow = FakeWorkflow()

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr("llm_evaluator.cli.build_workflow", lambda: fake_workflow)

    runner = CliRunner()
    result = runner.invoke(app, ["evaluate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert fake_workflow.received_state is not None
    assert fake_workflow.received_state["api_key"] == "dotenv-test-key"
