import pytest

from llm_evaluator.domain.benchmark import BenchmarkCase
from llm_evaluator.graph.nodes.validate_benchmark import validate_benchmark


def test_validate_benchmark_rejects_duplicate_prompts() -> None:
    duplicate_case_set = [
        BenchmarkCase(
            id="case-1",
            input_prompt="Repeat prompt",
            expected_output="Output 1",
            evaluation_criteria="Criteria 1",
        ),
        BenchmarkCase(
            id="case-2",
            input_prompt="Repeat prompt",
            expected_output="Output 2",
            evaluation_criteria="Criteria 2",
        ),
    ]

    with pytest.raises(ValueError):
        validate_benchmark(duplicate_case_set)
