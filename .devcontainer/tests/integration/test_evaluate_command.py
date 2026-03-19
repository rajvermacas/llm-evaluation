from pathlib import Path

from typer.testing import CliRunner

from llm_evaluator.cli import app
from llm_evaluator.domain.results import JudgmentResult


def test_evaluate_command_writes_reports(tmp_path: Path, monkeypatch) -> None:
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

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "llm_evaluator.providers.openrouter_client.OpenRouterClient.generate_benchmark",
        lambda self, teacher_model, problem_statement, benchmark_case_count, prompt: (
            {
                "cases": [
                    {
                        "id": "case-1",
                        "input_prompt": "Prompt 1",
                        "expected_output": "Output 1",
                        "evaluation_criteria": "Criteria 1",
                    }
                ]
            },
            0,
        ),
    )
    monkeypatch.setattr(
        "llm_evaluator.providers.openrouter_client.OpenRouterClient.run_candidate_prompt",
        lambda self, model_id, case: ("Output 1", 0),
    )
    monkeypatch.setattr(
        "llm_evaluator.providers.openrouter_client.OpenRouterClient.judge_candidate_output",
        lambda self, teacher_model, case, candidate_output, prompt: (
            JudgmentResult(passed=True, rationale="Matches expectation."),
            0,
        ),
    )

    runner = CliRunner()
    result = runner.invoke(app, ["evaluate", "--config", str(config_path)])

    assert result.exit_code == 0
    assert (tmp_path / "artifacts" / "report.md").exists()
    assert (tmp_path / "artifacts" / "results.json").exists()
