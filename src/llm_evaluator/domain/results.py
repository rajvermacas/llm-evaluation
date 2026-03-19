"""Evaluation result domain models."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from llm_evaluator.domain.benchmark import BenchmarkCase


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


class CandidateOutput(BaseModel):
    """Raw candidate model output before teacher judgment."""

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(min_length=1)
    benchmark_case_id: str = Field(min_length=1)
    raw_output: str = Field(min_length=1)
    total_cost: Decimal


class ModelAggregate(BaseModel):
    """Model-level aggregate metrics."""

    model_config = ConfigDict(extra="forbid")

    model_id: str = Field(min_length=1)
    passed: int = Field(ge=0)
    failed: int = Field(ge=0)
    pass_rate: Decimal
    total_cost: Decimal


class ReportContext(BaseModel):
    """Inputs required to render the final evaluation report."""

    model_config = ConfigDict(extra="forbid")

    recommended_model: str = Field(min_length=1)
    benchmark_cases: list[BenchmarkCase]
    candidate_results: list[CandidateResult]
    model_aggregates: list[ModelAggregate]
