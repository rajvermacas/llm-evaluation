import pytest

from llm_evaluator.graph.nodes.generate_benchmark import build_benchmark_cases


def test_build_benchmark_cases_returns_requested_count() -> None:
    fake_teacher_response = {
        "cases": [
            {
                "id": "case-1",
                "input_prompt": "Prompt 1",
                "expected_output": "Output 1",
                "evaluation_criteria": "Criteria 1",
            },
            {
                "id": "case-2",
                "input_prompt": "Prompt 2",
                "expected_output": "Output 2",
                "evaluation_criteria": "Criteria 2",
            },
            {
                "id": "case-3",
                "input_prompt": "Prompt 3",
                "expected_output": "Output 3",
                "evaluation_criteria": "Criteria 3",
            },
        ]
    }

    cases = build_benchmark_cases(fake_teacher_response, expected_count=3)

    assert len(cases) == 3


def test_build_benchmark_cases_rejects_non_string_expected_output() -> None:
    fake_teacher_response = {
        "cases": [
            {
                "id": "case-1",
                "input_prompt": "Prompt 1",
                "expected_output": True,
                "evaluation_criteria": "Criteria 1",
            }
        ]
    }

    with pytest.raises(
        ValueError,
        match='Teacher generated invalid benchmark case at index 0: field "expected_output" must be a string.',
    ):
        build_benchmark_cases(fake_teacher_response, expected_count=1)
