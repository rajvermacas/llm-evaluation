"""Candidate execution helpers."""

import logging
from decimal import Decimal

from llm_evaluator.domain.results import CandidateResult, JudgmentResult

LOGGER = logging.getLogger(__name__)


def build_candidate_result(
    model_id: str,
    benchmark_case_id: str,
    raw_output: str,
    total_cost: Decimal,
    judgment: JudgmentResult,
) -> CandidateResult:
    """Create a candidate result with an explicit teacher judgment."""
    LOGGER.info(
        "Building candidate result for model_id=%s benchmark_case_id=%s.",
        model_id,
        benchmark_case_id,
    )
    return CandidateResult(
        model_id=model_id,
        benchmark_case_id=benchmark_case_id,
        raw_output=raw_output,
        total_cost=total_cost,
        judgment=judgment,
    )
