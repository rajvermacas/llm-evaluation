"""Aggregation and ranking utilities."""

import logging

from llm_evaluator.domain.results import ModelAggregate

LOGGER = logging.getLogger(__name__)


def rank_models(items: list[ModelAggregate]) -> list[ModelAggregate]:
    """Rank models by pass rate descending, then total cost ascending."""
    LOGGER.info("Ranking %s model aggregates.", len(items))
    ranked = sorted(items, key=lambda item: (-item.pass_rate, item.total_cost))
    LOGGER.info("Ranking complete. Top model=%s.", ranked[0].model_id if ranked else None)
    return ranked
