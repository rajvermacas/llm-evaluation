"""Workflow state definitions."""

from pathlib import Path
from typing import TypedDict

from llm_evaluator.domain.benchmark import BenchmarkCase
from llm_evaluator.domain.config import RunConfig
from llm_evaluator.domain.results import CandidateOutput, CandidateResult, ModelAggregate
from llm_evaluator.providers.openrouter_client import OpenRouterClient


class EvaluatorState(TypedDict, total=False):
    """State carried through the evaluation workflow."""

    api_key: str
    config_path: Path
    run_config: RunConfig
    openrouter_client: OpenRouterClient
    benchmark_cases: list[BenchmarkCase]
    candidate_outputs: list[CandidateOutput]
    candidate_results: list[CandidateResult]
    model_aggregates: list[ModelAggregate]
    recommended_model: str
    output_dir: Path
