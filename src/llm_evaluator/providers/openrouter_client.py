"""OpenRouter API client."""

from decimal import Decimal
import json
import logging
from typing import Any

import httpx

from llm_evaluator.domain.benchmark import BenchmarkCase
from llm_evaluator.domain.results import JudgmentResult

LOGGER = logging.getLogger(__name__)


def _build_benchmark_generation_content(
    prompt: str,
    problem_statement: str,
    benchmark_case_count: int,
) -> str:
    """Build the teacher benchmark-generation message content."""
    return (
        f"{prompt}\n\n"
        f"Problem Statement:\n{problem_statement}\n\n"
        f"Generate exactly {benchmark_case_count} cases.\n"
        "Every field value must be a JSON string.\n"
        "expected_output must be a concise natural-language reference answer.\n"
        "Do not reduce expected_output to bare booleans or exact-match labels unless the ideal answer is genuinely that short.\n"
        "evaluation_criteria must require semantic evaluation, not exact string matching."
    )


class OpenRouterClient:
    """Minimal OpenRouter client wrapper."""

    _base_url = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            LOGGER.error("OpenRouter API key was not provided.")
            raise ValueError("OpenRouter API key is required.")

        self._api_key = api_key
        LOGGER.info("Initialized OpenRouter client.")

    def generate_benchmark(
        self,
        teacher_model: str,
        problem_statement: str,
        benchmark_case_count: int,
        prompt: str,
    ) -> tuple[dict[str, Any], Decimal]:
        """Generate benchmark cases using the teacher model."""
        return self._request_json(
            model=teacher_model,
            messages=[
                {
                    "role": "user",
                    "content": _build_benchmark_generation_content(
                        prompt=prompt,
                        problem_statement=problem_statement,
                        benchmark_case_count=benchmark_case_count,
                    ),
                }
            ],
        )

    def run_candidate_prompt(
        self,
        model_id: str,
        case: BenchmarkCase,
    ) -> tuple[str, Decimal]:
        """Run a candidate model on a single benchmark case."""
        payload, cost = self._request_completion(
            model=model_id,
            messages=[{"role": "user", "content": case.input_prompt}],
        )
        return self._extract_message_content(payload), cost

    def judge_candidate_output(
        self,
        teacher_model: str,
        case: BenchmarkCase,
        candidate_output: str,
        prompt: str,
    ) -> tuple[JudgmentResult, Decimal]:
        """Judge a candidate response with the teacher model."""
        content = (
            f"{prompt}\n\n"
            f"Input Prompt:\n{case.input_prompt}\n\n"
            f"Reference Answer:\n{case.expected_output}\n\n"
            f"Evaluation Criteria:\n{case.evaluation_criteria}\n\n"
            f"Candidate Output:\n{candidate_output}"
        )
        payload, cost = self._request_json(
            model=teacher_model,
            messages=[{"role": "user", "content": content}],
        )
        return JudgmentResult.model_validate(payload), cost

    def _request_json(
        self,
        model: str,
        messages: list[dict[str, str]],
    ) -> tuple[dict[str, Any], Decimal]:
        """Request structured JSON from OpenRouter."""
        payload, cost = self._request_completion(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
        )
        message_content = self._extract_message_content(payload)
        try:
            return json.loads(message_content), cost
        except json.JSONDecodeError as exc:
            LOGGER.error("OpenRouter returned invalid JSON content.")
            raise ValueError("OpenRouter returned invalid JSON content.") from exc

    def _request_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        response_format: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], Decimal]:
        """Send a non-streaming chat completion request."""
        request_payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
        }
        if response_format is not None:
            request_payload["response_format"] = response_format

        LOGGER.info("Sending OpenRouter request for model=%s.", model)
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self._base_url}/chat/completions",
                headers=self._build_headers(),
                json=request_payload,
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            LOGGER.error(
                "OpenRouter request failed: status=%s url=%s body=%s",
                exc.response.status_code,
                exc.request.url,
                exc.response.text,
            )
            raise ValueError(
                f"OpenRouter request failed with status {exc.response.status_code}: {exc.response.text}"
            ) from exc
        payload = response.json()
        return payload, self._extract_cost(payload)

    def _build_headers(self) -> dict[str, str]:
        """Build OpenRouter request headers."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _extract_message_content(self, payload: dict[str, Any]) -> str:
        """Extract assistant content from a completion response."""
        try:
            content = payload["choices"][0]["message"]["content"]
        except (IndexError, KeyError, TypeError) as exc:
            LOGGER.error("OpenRouter response missing assistant message content.")
            raise ValueError("OpenRouter response missing assistant message content.") from exc

        if not isinstance(content, str) or not content.strip():
            LOGGER.error("OpenRouter assistant message content is empty.")
            raise ValueError("OpenRouter assistant message content is empty.")
        return content

    def _extract_cost(self, payload: dict[str, Any]) -> Decimal:
        """Extract request cost from a completion response."""
        usage = payload.get("usage")
        if not isinstance(usage, dict) or "cost" not in usage:
            LOGGER.error("OpenRouter response missing usage cost.")
            raise ValueError("OpenRouter response missing usage cost.")
        return Decimal(str(usage["cost"]))
