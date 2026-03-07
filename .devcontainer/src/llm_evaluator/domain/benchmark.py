"""Benchmark domain models."""

import logging

from pydantic import BaseModel, ConfigDict, Field

LOGGER = logging.getLogger(__name__)


class BenchmarkCase(BaseModel):
    """A single teacher-generated evaluation case."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    input_prompt: str = Field(min_length=1)
    expected_output: str = Field(min_length=1)
    evaluation_criteria: str = Field(min_length=1)
