import httpx
import pytest

from llm_evaluator.domain.benchmark import BenchmarkCase
from llm_evaluator.prompts.judge_output import JUDGE_OUTPUT_PROMPT
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


def test_generate_benchmark_uses_reference_answer_prompt(monkeypatch) -> None:
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
    assert "input_prompt must be a fully self-contained instruction for the candidate model." in message
    assert "input_prompt must be derived from the provided problem statement" in message
    assert "input_prompt must specify the expected response format" in message
    assert "expected_output must be a concise natural-language reference answer" in message
    assert "evaluation_criteria must instruct the judge to evaluate semantic correctness" in message


def test_judge_candidate_output_uses_semantic_evaluation_prompt(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_request_json(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> tuple[dict[str, object], object]:
        captured["model"] = model
        captured["messages"] = messages
        return {"passed": True, "rationale": "The answer matches the meaning."}, 0

    monkeypatch.setattr(OpenRouterClient, "_request_json", fake_request_json)

    client = OpenRouterClient(api_key="test-key")
    judgment, _cost = client.judge_candidate_output(
        teacher_model="openai/gpt-4o-mini",
        case=BenchmarkCase(
            id="case-1",
            input_prompt="Classify this news item.",
            expected_output="This news is price sensitive because it reports earnings.",
            evaluation_criteria="Pass answers that correctly identify the news as price sensitive.",
        ),
        candidate_output="This looks price sensitive due to earnings.",
        prompt=JUDGE_OUTPUT_PROMPT,
    )

    assert judgment.passed is True
    assert captured["model"] == "openai/gpt-4o-mini"
    messages = captured["messages"]
    assert isinstance(messages, list)
    message = messages[0]["content"]
    assert "Do not require exact wording or exact string matching." in message
    assert "Reference Answer:" in message
    assert "Candidate Output:" in message
