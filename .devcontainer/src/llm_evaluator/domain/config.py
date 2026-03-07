"""Configuration domain models."""

import logging

from pydantic import BaseModel, ConfigDict, Field, field_validator

LOGGER = logging.getLogger(__name__)


class RunConfig(BaseModel):
    """Validated configuration for a single evaluation run."""

    model_config = ConfigDict(extra="forbid")

    teacher_model: str = Field(min_length=1)
    candidate_models: list[str]
    problem_statement: str = Field(min_length=1)

    @field_validator("candidate_models")
    @classmethod
    def validate_candidate_models(cls, value: list[str]) -> list[str]:
        """Reject missing or empty candidate model identifiers."""
        if not value:
            LOGGER.error("Configuration validation failed: candidate_models is empty.")
            raise ValueError("candidate_models must contain at least one model.")
        if any(not item.strip() for item in value):
            LOGGER.error("Configuration validation failed: candidate_models contains blank values.")
            raise ValueError("candidate_models must not contain blank model identifiers.")
        return value
