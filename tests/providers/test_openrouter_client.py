import httpx
import pytest

from llm_evaluator.providers.openrouter_client import OpenRouterClient


def test_client_requires_api_key() -> None:
    with pytest.raises(ValueError):
        OpenRouterClient(api_key="")


def test_request_completion_surfaces_openrouter_http_error(monkeypatch) -> None:
    class FakeResponse:
        status_code = 404
        text = (
            '{"error":{"message":"No endpoints available matching your guardrail '
            'restrictions and data policy. Configure: https://openrouter.ai/settings/privacy","code":404}}'
        )

        def raise_for_status(self) -> None:
            request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
            raise httpx.HTTPStatusError("not found", request=request, response=self)

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def post(self, *args, **kwargs) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr("llm_evaluator.providers.openrouter_client.httpx.Client", FakeClient)

    client = OpenRouterClient(api_key="test-key")

    with pytest.raises(ValueError, match="No endpoints available matching your guardrail restrictions and data policy"):
        client._request_completion(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hi."}],
        )


def test_generate_benchmark_requires_string_fields_in_prompt(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_request_json(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> tuple[dict[str, object], object]:
        captured["model"] = model
        captured["messages"] = messages
        return {"cases": []}, 0

    monkeypatch.setattr(OpenRouterClient, "_request_json", fake_request_json)

    client = OpenRouterClient(api_key="test-key")
    payload, _cost = client.generate_benchmark(
        teacher_model="openai/gpt-4o-mini",
        problem_statement="Return yes or no.",
        benchmark_case_count=2,
        prompt="Base prompt.",
    )

    assert payload == {"cases": []}
    assert captured["model"] == "openai/gpt-4o-mini"
    messages = captured["messages"]
    assert isinstance(messages, list)
    message = messages[0]["content"]
    assert 'Every field value must be a JSON string.' in message
    assert 'Use string literals like "true" or "false", never bare booleans.' in message
