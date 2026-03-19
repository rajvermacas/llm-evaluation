import pytest

from llm_evaluator.domain.benchmark import BenchmarkCase


def test_benchmark_case_requires_expected_output() -> None:
    with pytest.raises(ValueError):
        BenchmarkCase(
            id="case-1",
            input_prompt="Classify this news item.",
            evaluation_criteria="Return pass only when classification matches.",
        )
