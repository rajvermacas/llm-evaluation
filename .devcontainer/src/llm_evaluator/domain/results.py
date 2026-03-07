"""Evaluation result domain models."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class JudgmentResult(BaseModel):
    """Teacher judgment for a candidate response."""

    model_config = ConfigDict(extra="forbid")

    passed: bool
    rationale: str = Field(min_length=1)


class CandidateResult(BaseModel):
    """Candidate model output and teacher judgment for one case."""

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(min_length=1)
    benchmark_case_id: str = Field(min_length=1)
    raw_output: str = Field(min_length=1)
    total_cost: Decimal
    judgment: JudgmentResult
