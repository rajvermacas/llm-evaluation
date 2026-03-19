"""Teacher judgment parsing helpers."""

import logging

from llm_evaluator.domain.results import JudgmentResult

LOGGER = logging.getLogger(__name__)


def judge_candidate_output(payload: dict) -> JudgmentResult:
    """Parse teacher judgment payload."""
    LOGGER.info("Parsing teacher judgment payload.")
    judgment = JudgmentResult.model_validate(payload)
    LOGGER.info("Parsed teacher judgment with passed=%s.", judgment.passed)
    return judgment
