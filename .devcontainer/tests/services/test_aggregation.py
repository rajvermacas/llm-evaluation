from decimal import Decimal

from llm_evaluator.domain.results import ModelAggregate
from llm_evaluator.services.aggregation import rank_models


def test_rank_models_uses_cost_to_break_pass_rate_ties() -> None:
    result_set_with_tie = [
        ModelAggregate(
            model_id="expensive-model",
            passed=4,
            failed=1,
            pass_rate=Decimal("0.8"),
            total_cost=Decimal("1.25"),
        ),
        ModelAggregate(
            model_id="cheaper-model",
            passed=4,
            failed=1,
            pass_rate=Decimal("0.8"),
            total_cost=Decimal("0.95"),
        ),
    ]

    ranked = rank_models(result_set_with_tie)

    assert ranked[0].model_id == "cheaper-model"
