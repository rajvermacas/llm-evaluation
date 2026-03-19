from llm_evaluator.graph.nodes.judge_outputs import judge_candidate_output


def test_judge_candidate_output_returns_pass_fail_and_rationale() -> None:
    fake_judgment_response = {
        "passed": True,
        "rationale": "The candidate response matches the expected result.",
    }

    judgment = judge_candidate_output(fake_judgment_response)

    assert judgment.passed is True
    assert judgment.rationale
