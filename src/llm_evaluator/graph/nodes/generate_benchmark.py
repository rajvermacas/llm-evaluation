"""Teacher benchmark generation helpers."""

import logging

from pydantic import ValidationError

from llm_evaluator.domain.benchmark import BenchmarkCase

LOGGER = logging.getLogger(__name__)


def build_benchmark_cases(payload: dict, expected_count: int) -> list[BenchmarkCase]:
    """Validate and convert teacher benchmark payload into domain models."""
    LOGGER.info("Building benchmark cases with expected_count=%s.", expected_count)
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list):
        LOGGER.error('Teacher payload must include a "cases" list.')
        raise ValueError('Teacher payload must include a "cases" list.')

    cases: list[BenchmarkCase] = []
    for index, item in enumerate(raw_cases):
        try:
            cases.append(BenchmarkCase.model_validate(item))
        except ValidationError as exc:
            field_name = ".".join(str(part) for part in exc.errors()[0]["loc"])
            LOGGER.error(
                'Teacher generated invalid benchmark case at index %s for field "%s": %s',
                index,
                field_name,
                exc.errors()[0]["msg"],
            )
            raise ValueError(
                f'Teacher generated invalid benchmark case at index {index}: field "{field_name}" must be a string.'
            ) from exc

    if len(cases) != expected_count:
        LOGGER.error(
            "Teacher generated unexpected benchmark count: expected=%s actual=%s.",
            expected_count,
            len(cases),
        )
        raise ValueError("Teacher generated an unexpected number of benchmark cases.")

    LOGGER.info("Built %s benchmark cases.", len(cases))
    return cases
