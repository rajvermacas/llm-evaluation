# Agentic LLM Evaluator Design

**Goal:** Build a CLI-first LangGraph-based evaluation system that takes a problem statement, generates benchmark cases with a teacher model, evaluates configured candidate models, and recommends the best model by pass rate with cost as a tie-breaker.

**Scope:** Version 1 is an offline evaluator. It does not route production traffic, re-run benchmarks on a schedule, or adapt model choice dynamically at runtime.

## Summary

The system accepts a problem statement and a configuration containing one teacher model and multiple candidate models available through OpenRouter. A teacher model generates test cases, expected outputs, and judging criteria. Candidate models answer the generated cases. The teacher model then judges each candidate response and produces a pass or fail result with rationale. The system aggregates pass rates and estimated costs, then recommends the winning model by highest pass rate and lowest cost among ties.

This benchmark is comparative, not absolute. Because the teacher defines expectations and performs judging, the recommendation should be interpreted as the best model under the teacher-defined benchmark.

## Core Requirements

- Use OpenRouter as the provider for teacher and candidate models.
- Configure the teacher model explicitly. Do not use hidden defaults.
- Generate test cases and expected outputs automatically with the teacher model.
- Evaluate candidate outputs using LLM-as-judge with the teacher model.
- Persist the exact test case, expected output, candidate output, and judgment for every evaluation.
- Rank models by highest pass rate first. Use total cost only as a tie-breaker.
- Fail fast with clear exceptions when required inputs or outputs are missing.
- Produce machine-readable and human-readable reports.

## Recommended Tech Stack

- Python
- LangGraph for workflow orchestration
- LangChain for model wrappers, prompt templates, and structured outputs
- Pydantic for strict schemas and validation
- Typer for CLI commands
- httpx for direct OpenRouter metadata or pricing requests when needed
- logging or structlog for detailed logs
- PyYAML for user-authored configuration
- Jinja2 for Markdown or HTML report rendering
- pytest for unit and integration tests

## System Architecture

The system is organized as a CLI-first evaluation engine driven by a LangGraph workflow. The graph coordinates the evaluation run while domain logic remains explicit in Python.

### High-Level Flow

1. Load configuration and problem statement.
2. Generate a benchmark set with the teacher model.
3. Validate the generated benchmark before spending candidate evaluation cost.
4. Run each candidate model on every benchmark case.
5. Judge each candidate response using the teacher model.
6. Aggregate model metrics including pass counts, pass rate, token usage, and estimated cost.
7. Rank models and select a recommendation.
8. Write JSON and Markdown reports.

### LangGraph Nodes

- `load_config`
- `generate_benchmark_with_teacher`
- `validate_benchmark`
- `run_candidate_models`
- `judge_candidate_outputs`
- `aggregate_scores_and_costs`
- `rank_models`
- `write_reports`

LangGraph owns orchestration, retries, and state transitions. Ranking logic, pricing logic, and report assembly remain plain Python to keep business rules transparent and auditable.

## Data Model

### Run Configuration

The run configuration should capture:

- problem statement
- teacher model identifier
- candidate model identifiers
- generation settings
- judging settings
- ranking rule
- output directory

### Benchmark Case

Each benchmark case should include:

- `id`
- `input_prompt`
- `expected_output`
- `evaluation_criteria`
- optional `category`
- optional `difficulty`

### Candidate Evaluation Result

For every candidate-model and test-case pair, persist:

- model identifier
- benchmark case identifier
- raw candidate output
- token usage
- estimated cost
- teacher judgment
- pass or fail decision
- judge rationale

### Final Report

The final report should include model-level aggregates:

- total passed
- total failed
- pass rate
- total cost
- cost per passed test
- final rank
- recommended model

## Validation Stage

The `validate_benchmark` node protects the rest of the pipeline from invalid teacher-generated cases. It should reject the run if any benchmark case is unusable.

Validation should cover:

- required fields present
- generated case count matches request
- expected outputs are non-empty
- evaluation criteria are explicit enough to judge
- structured outputs parse cleanly
- duplicate or near-duplicate test cases are flagged
- prompt and expected output formats are internally consistent

On failure, the node should raise a clear exception, stop the workflow, and write validation diagnostics.

## Reporting

Every run should create a dedicated output directory containing:

- `config.yaml`
- `benchmark.json`
- `results.json`
- `report.md`

The report must show, for each case:

- test case input
- expected output
- candidate output
- teacher judgment
- pass or fail

The report must also show, for each model:

- total cases
- pass count
- fail count
- pass rate
- estimated total cost
- ranking position

## Guardrails

- Require explicit configuration for teacher and candidate models.
- Persist raw prompts and raw outputs used during generation and judgment.
- Log every graph node with detailed context.
- Fail fast when model calls, metadata lookups, or judgment artifacts are missing.
- Mark runs as invalid when teacher judgments are malformed.
- Avoid fallback defaults for required fields.

## Version 1 Non-Goals

- Live model routing in production
- Scheduled re-benchmarking
- Dynamic model selection by prompt class at runtime
- Multiple judge models or consensus judging
- Human review workflows

## Risks

- Teacher bias because one model generates and judges benchmark data
- Cost estimation can drift if provider pricing metadata changes
- Non-determinism in generation and judging may affect reproducibility

These risks should be surfaced in the generated report so the recommendation is interpreted correctly.

## Operational Notes

- Required environment variable: `OPENROUTER_API_KEY`
- Required run configuration fields: `teacher_model`, `candidate_models`, `problem_statement`, `benchmark_case_count`, `output_dir`
- Expected output artifacts per run: `config.yaml`, `benchmark.json`, `results.json`, `report.md`
- Local run command:

```bash
cd /workspaces/llm-evaluation/.devcontainer
export OPENROUTER_API_KEY=your-api-key
PYTHONPATH=src python -m llm_evaluator.cli evaluate --config examples/sample-config.yaml
```
