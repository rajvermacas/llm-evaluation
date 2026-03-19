from llm_evaluator.graph.workflow import build_workflow


def test_workflow_contains_expected_nodes() -> None:
    graph = build_workflow()

    assert "generate_benchmark_with_teacher" in graph.nodes
    assert "write_reports" in graph.nodes
