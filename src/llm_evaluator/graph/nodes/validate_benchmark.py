"""Benchmark validation node."""

import logging

from llm_evaluator.domain.benchmark import BenchmarkCase

LOGGER = logging.getLogger(__name__)


def validate_benchmark(cases: list[BenchmarkCase]) -> list[BenchmarkCase]:
    """Reject duplicate benchmark prompts."""
    LOGGER.info("Validating %s benchmark cases.", len(cases))
    seen_prompts: set[str] = set()
    for case in cases:
        if case.input_prompt in seen_prompts:
            LOGGER.error("Duplicate benchmark prompt detected for case_id=%s.", case.id)
            raise ValueError("Duplicate benchmark prompt detected.")
        seen_prompts.add(case.input_prompt)

    LOGGER.info("Benchmark validation completed successfully.")
    return cases
