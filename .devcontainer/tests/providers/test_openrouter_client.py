import pytest

from llm_evaluator.providers.openrouter_client import OpenRouterClient


def test_client_requires_api_key() -> None:
    with pytest.raises(ValueError):
        OpenRouterClient(api_key="")
