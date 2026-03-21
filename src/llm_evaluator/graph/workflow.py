"""LangGraph workflow wiring."""

import logging
import shutil
from decimal import Decimal

from langgraph.graph import END, START, StateGraph

from llm_evaluator.domain.results import CandidateOutput, CandidateResult, ModelAggregate, ReportContext
from llm_evaluator.graph.nodes.generate_benchmark import build_benchmark_cases
from llm_evaluator.graph.nodes.run_candidates import build_candidate_result
from llm_evaluator.graph.nodes.validate_benchmark import validate_benchmark
from llm_evaluator.graph.state import EvaluatorState
from llm_evaluator.prompts.generate_benchmark import GENERATE_BENCHMARK_PROMPT
from llm_evaluator.prompts.judge_output import JUDGE_OUTPUT_PROMPT
from llm_evaluator.reports.write_json import write_json_report
from llm_evaluator.reports.write_markdown import render_report
from llm_evaluator.services.aggregation import rank_models
from llm_evaluator.services.config_loader import load_config
from llm_evaluator.services.output_paths import create_timestamped_output_dir

LOGGER = logging.getLogger(__name__)


def load_run_context(state: EvaluatorState) -> EvaluatorState:
    """Load config and initialize the API client."""
    from llm_evaluator.providers.openrouter_client import OpenRouterClient

    LOGGER.info("Loading run context from config_path=%s.", state["config_path"])
    run_config = load_config(state["config_path"])
    output_dir = create_timestamped_output_dir(run_config.output_dir)
    shutil.copy2(state["config_path"], output_dir / "config.yaml")
    LOGGER.info("Run context ready with output_dir=%s.", output_dir)
    return {
        "run_config": run_config,
        "openrouter_client": OpenRouterClient(api_key=state["api_key"]),
        "output_dir": output_dir,
    }


def generate_benchmark_with_teacher(state: EvaluatorState) -> EvaluatorState:
    """Generate benchmark cases using the teacher model."""
    run_config = state["run_config"]
    LOGGER.info(
        "Generating %s benchmark cases with teacher_model=%s.",
        run_config.benchmark_case_count,
        run_config.teacher_model,
    )
    payload, _cost = state["openrouter_client"].generate_benchmark(
        teacher_model=run_config.teacher_model,
        problem_statement=run_config.problem_statement,
        benchmark_case_count=run_config.benchmark_case_count,
        prompt=GENERATE_BENCHMARK_PROMPT,
    )
    cases = build_benchmark_cases(payload, expected_count=run_config.benchmark_case_count)
    return {"benchmark_cases": cases}


def validate_benchmark_node(state: EvaluatorState) -> EvaluatorState:
    """Validate generated benchmark cases."""
    return {"benchmark_cases": validate_benchmark(state["benchmark_cases"])}


def run_candidate_models(state: EvaluatorState) -> EvaluatorState:
    """Run every candidate model against every benchmark case."""
    outputs: list[CandidateOutput] = []
    run_config = state["run_config"]
    client = state["openrouter_client"]
    LOGGER.info(
        "Running %s candidate models across %s benchmark cases.",
        len(run_config.candidate_models),
        len(state["benchmark_cases"]),
    )
    for case in state["benchmark_cases"]:
        for model_id in run_config.candidate_models:
            raw_output, total_cost = client.run_candidate_prompt(model_id=model_id, case=case)
            outputs.append(
                CandidateOutput(
                    model_id=model_id,
                    benchmark_case_id=case.id,
                    raw_output=raw_output,
                    total_cost=total_cost,
                )
            )
    return {"candidate_outputs": outputs}


def judge_candidate_outputs(state: EvaluatorState) -> EvaluatorState:
    """Judge each candidate output using the teacher model."""
    benchmark_by_id = {case.id: case for case in state["benchmark_cases"]}
    run_config = state["run_config"]
    client = state["openrouter_client"]
    results: list[CandidateResult] = []
    LOGGER.info(
        "Judging %s candidate outputs with teacher_model=%s.",
        len(state["candidate_outputs"]),
        run_config.teacher_model,
    )
    for output in state["candidate_outputs"]:
        case = benchmark_by_id[output.benchmark_case_id]
        judgment, judgment_cost = client.judge_candidate_output(
            teacher_model=run_config.teacher_model,
            case=case,
            candidate_output=output.raw_output,
            prompt=JUDGE_OUTPUT_PROMPT,
        )
        results.append(
            build_candidate_result(
                model_id=output.model_id,
                benchmark_case_id=output.benchmark_case_id,
                raw_output=output.raw_output,
                total_cost=output.total_cost + judgment_cost,
                judgment=judgment,
            )
        )
    return {"candidate_results": results}


def aggregate_scores_and_costs(state: EvaluatorState) -> EvaluatorState:
    """Aggregate results at the model level and choose the recommendation."""
    aggregates_by_model: dict[str, dict[str, object]] = {}
    LOGGER.info("Aggregating %s candidate results.", len(state["candidate_results"]))
    for result in state["candidate_results"]:
        bucket = aggregates_by_model.setdefault(
            result.model_id,
            {"passed": 0, "failed": 0, "total_cost": 0},
        )
        if result.judgment.passed:
            bucket["passed"] = int(bucket["passed"]) + 1
        else:
            bucket["failed"] = int(bucket["failed"]) + 1
        bucket["total_cost"] = bucket["total_cost"] + result.total_cost

    aggregates = []
    for model_id, bucket in aggregates_by_model.items():
        passed = int(bucket["passed"])
        failed = int(bucket["failed"])
        total = passed + failed
        if total == 0:
            raise ValueError(f"No results were recorded for model: {model_id}")
        aggregates.append(
            ModelAggregate(
                model_id=model_id,
                passed=passed,
                failed=failed,
                pass_rate=Decimal(passed) / Decimal(total),
                total_cost=bucket["total_cost"],
            )
        )

    ranked = rank_models(aggregates)
    return {
        "model_aggregates": ranked,
        "recommended_model": ranked[0].model_id,
    }


def write_reports(state: EvaluatorState) -> EvaluatorState:
    """Write machine-readable and Markdown reports."""
    context = ReportContext(
        recommended_model=state["recommended_model"],
        benchmark_cases=state["benchmark_cases"],
        candidate_results=state["candidate_results"],
        model_aggregates=state["model_aggregates"],
    )
    output_dir = state["output_dir"]
    write_json_report(context, output_dir / "results.json")
    (output_dir / "benchmark.json").write_text(
        "[" + ",\n".join(case.model_dump_json() for case in state["benchmark_cases"]) + "]",
        encoding="utf-8",
    )
    (output_dir / "report.md").write_text(render_report(context), encoding="utf-8")
    LOGGER.info("Wrote evaluation artifacts to %s.", output_dir)
    return {}


def build_workflow():
    """Build the evaluator workflow graph."""
    graph = StateGraph(EvaluatorState)
    graph.add_node("load_run_context", load_run_context)
    graph.add_node("generate_benchmark_with_teacher", generate_benchmark_with_teacher)
    graph.add_node("validate_benchmark", validate_benchmark_node)
    graph.add_node("run_candidate_models", run_candidate_models)
    graph.add_node("judge_candidate_outputs", judge_candidate_outputs)
    graph.add_node("aggregate_scores_and_costs", aggregate_scores_and_costs)
    graph.add_node("write_reports", write_reports)
    graph.add_edge(START, "load_run_context")
    graph.add_edge("load_run_context", "generate_benchmark_with_teacher")
    graph.add_edge("generate_benchmark_with_teacher", "validate_benchmark")
    graph.add_edge("validate_benchmark", "run_candidate_models")
    graph.add_edge("run_candidate_models", "judge_candidate_outputs")
    graph.add_edge("judge_candidate_outputs", "aggregate_scores_and_costs")
    graph.add_edge("aggregate_scores_and_costs", "write_reports")
    graph.add_edge("write_reports", END)
    return graph.compile()
