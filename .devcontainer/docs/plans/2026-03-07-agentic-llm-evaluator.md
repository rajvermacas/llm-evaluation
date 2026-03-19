# Agentic LLM Evaluator Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a CLI-first LangGraph evaluation tool that benchmarks OpenRouter models using a teacher model for test generation and judging, then recommends the winner by pass rate with cost as the tie-breaker.

**Architecture:** The system uses LangGraph to orchestrate a deterministic evaluation workflow across config loading, benchmark generation, validation, candidate execution, judging, aggregation, ranking, and report writing. LangChain handles model interaction and structured outputs, while domain schemas, ranking logic, and reporting remain explicit Python modules.

**Tech Stack:** Python, LangGraph, LangChain, Pydantic, Typer, httpx, PyYAML, Jinja2, pytest, logging

---

### Task 1: Bootstrap the Python project

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `src/llm_evaluator/__init__.py`
- Create: `src/llm_evaluator/cli.py`
- Create: `tests/test_smoke.py`

**Step 1: Write the failing test**

```python
from typer.testing import CliRunner

from llm_evaluator.cli import app


def test_cli_help_exposes_evaluate_command() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "evaluate" in result.stdout
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_smoke.py -v`
Expected: FAIL with import errors because the package and CLI do not exist yet.

**Step 3: Write minimal implementation**

```python
import typer

app = typer.Typer()


@app.command()
def evaluate() -> None:
    """Run an evaluation."""
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml README.md src/llm_evaluator/__init__.py src/llm_evaluator/cli.py tests/test_smoke.py
git commit -m "feat: bootstrap evaluator cli"
```

### Task 2: Add strict configuration schemas and loader

**Files:**
- Create: `src/llm_evaluator/domain/config.py`
- Create: `src/llm_evaluator/services/config_loader.py`
- Create: `tests/domain/test_config.py`
- Modify: `src/llm_evaluator/cli.py`

**Step 1: Write the failing test**

```python
import pytest

from llm_evaluator.services.config_loader import load_config


def test_load_config_requires_teacher_model(tmp_path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("candidate_models: []\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(config_path)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/domain/test_config.py -v`
Expected: FAIL because the config loader does not exist.

**Step 3: Write minimal implementation**

```python
class RunConfig(BaseModel):
    teacher_model: str
    candidate_models: list[str]
    problem_statement: str


def load_config(path: Path) -> RunConfig:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return RunConfig.model_validate(payload)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/domain/test_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/domain/config.py src/llm_evaluator/services/config_loader.py src/llm_evaluator/cli.py tests/domain/test_config.py
git commit -m "feat: add strict run configuration loading"
```

### Task 3: Define benchmark, result, and report schemas

**Files:**
- Create: `src/llm_evaluator/domain/benchmark.py`
- Create: `src/llm_evaluator/domain/results.py`
- Create: `tests/domain/test_benchmark_schema.py`

**Step 1: Write the failing test**

```python
import pytest

from llm_evaluator.domain.benchmark import BenchmarkCase


def test_benchmark_case_requires_expected_output() -> None:
    with pytest.raises(ValueError):
        BenchmarkCase(
            id="case-1",
            input_prompt="Classify this news item.",
            evaluation_criteria="Return pass only when classification matches.",
        )
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/domain/test_benchmark_schema.py -v`
Expected: FAIL because the benchmark schema does not exist.

**Step 3: Write minimal implementation**

```python
class BenchmarkCase(BaseModel):
    id: str
    input_prompt: str
    expected_output: str
    evaluation_criteria: str
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/domain/test_benchmark_schema.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/domain/benchmark.py src/llm_evaluator/domain/results.py tests/domain/test_benchmark_schema.py
git commit -m "feat: add benchmark and result schemas"
```

### Task 4: Implement the OpenRouter model client

**Files:**
- Create: `src/llm_evaluator/providers/openrouter_client.py`
- Create: `tests/providers/test_openrouter_client.py`
- Modify: `src/llm_evaluator/domain/config.py`

**Step 1: Write the failing test**

```python
import pytest

from llm_evaluator.providers.openrouter_client import OpenRouterClient


def test_client_requires_api_key() -> None:
    with pytest.raises(ValueError):
        OpenRouterClient(api_key="")
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/providers/test_openrouter_client.py -v`
Expected: FAIL because the provider client does not exist.

**Step 3: Write minimal implementation**

```python
class OpenRouterClient:
    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("OpenRouter API key is required.")
        self._api_key = api_key
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/providers/test_openrouter_client.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/providers/openrouter_client.py tests/providers/test_openrouter_client.py src/llm_evaluator/domain/config.py
git commit -m "feat: add openrouter provider client"
```

### Task 5: Build the teacher benchmark-generation node

**Files:**
- Create: `src/llm_evaluator/prompts/generate_benchmark.py`
- Create: `src/llm_evaluator/graph/nodes/generate_benchmark.py`
- Create: `tests/graph/test_generate_benchmark.py`

**Step 1: Write the failing test**

```python
from llm_evaluator.graph.nodes.generate_benchmark import build_benchmark_cases


def test_build_benchmark_cases_returns_requested_count(fake_teacher_response) -> None:
    cases = build_benchmark_cases(fake_teacher_response, expected_count=3)
    assert len(cases) == 3
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/graph/test_generate_benchmark.py -v`
Expected: FAIL because the generation node does not exist.

**Step 3: Write minimal implementation**

```python
def build_benchmark_cases(payload: dict, expected_count: int) -> list[BenchmarkCase]:
    cases = [BenchmarkCase.model_validate(item) for item in payload["cases"]]
    if len(cases) != expected_count:
        raise ValueError("Teacher generated an unexpected number of benchmark cases.")
    return cases
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/graph/test_generate_benchmark.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/prompts/generate_benchmark.py src/llm_evaluator/graph/nodes/generate_benchmark.py tests/graph/test_generate_benchmark.py
git commit -m "feat: add teacher benchmark generation node"
```

### Task 6: Build the benchmark-validation node

**Files:**
- Create: `src/llm_evaluator/graph/nodes/validate_benchmark.py`
- Create: `tests/graph/test_validate_benchmark.py`

**Step 1: Write the failing test**

```python
import pytest

from llm_evaluator.graph.nodes.validate_benchmark import validate_benchmark


def test_validate_benchmark_rejects_duplicate_prompts(duplicate_case_set) -> None:
    with pytest.raises(ValueError):
        validate_benchmark(duplicate_case_set)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/graph/test_validate_benchmark.py -v`
Expected: FAIL because the validation node does not exist.

**Step 3: Write minimal implementation**

```python
def validate_benchmark(cases: list[BenchmarkCase]) -> list[BenchmarkCase]:
    seen_prompts: set[str] = set()
    for case in cases:
        if case.input_prompt in seen_prompts:
            raise ValueError("Duplicate benchmark prompt detected.")
        seen_prompts.add(case.input_prompt)
    return cases
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/graph/test_validate_benchmark.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/graph/nodes/validate_benchmark.py tests/graph/test_validate_benchmark.py
git commit -m "feat: add benchmark validation node"
```

### Task 7: Build candidate execution and judge nodes

**Files:**
- Create: `src/llm_evaluator/prompts/judge_output.py`
- Create: `src/llm_evaluator/graph/nodes/run_candidates.py`
- Create: `src/llm_evaluator/graph/nodes/judge_outputs.py`
- Create: `tests/graph/test_judge_outputs.py`

**Step 1: Write the failing test**

```python
from llm_evaluator.graph.nodes.judge_outputs import judge_candidate_output


def test_judge_candidate_output_returns_pass_fail_and_rationale(fake_judgment_response) -> None:
    judgment = judge_candidate_output(fake_judgment_response)
    assert judgment.passed is True
    assert judgment.rationale
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/graph/test_judge_outputs.py -v`
Expected: FAIL because the judge node does not exist.

**Step 3: Write minimal implementation**

```python
def judge_candidate_output(payload: dict) -> JudgmentResult:
    return JudgmentResult.model_validate(payload)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/graph/test_judge_outputs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/prompts/judge_output.py src/llm_evaluator/graph/nodes/run_candidates.py src/llm_evaluator/graph/nodes/judge_outputs.py tests/graph/test_judge_outputs.py
git commit -m "feat: add candidate execution and judging nodes"
```

### Task 8: Implement aggregation, ranking, and cost tie-breaking

**Files:**
- Create: `src/llm_evaluator/services/aggregation.py`
- Create: `tests/services/test_aggregation.py`

**Step 1: Write the failing test**

```python
from llm_evaluator.services.aggregation import rank_models


def test_rank_models_uses_cost_to_break_pass_rate_ties(result_set_with_tie) -> None:
    ranked = rank_models(result_set_with_tie)
    assert ranked[0].model_id == "cheaper-model"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/services/test_aggregation.py -v`
Expected: FAIL because the aggregation service does not exist.

**Step 3: Write minimal implementation**

```python
def rank_models(items: list[ModelAggregate]) -> list[ModelAggregate]:
    return sorted(items, key=lambda item: (-item.pass_rate, item.total_cost))
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/services/test_aggregation.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/services/aggregation.py tests/services/test_aggregation.py
git commit -m "feat: add ranking and aggregation rules"
```

### Task 9: Build JSON and Markdown report writers

**Files:**
- Create: `src/llm_evaluator/reports/write_json.py`
- Create: `src/llm_evaluator/reports/write_markdown.py`
- Create: `templates/report.md.j2`
- Create: `tests/reports/test_write_markdown.py`

**Step 1: Write the failing test**

```python
from llm_evaluator.reports.write_markdown import render_report


def test_render_report_includes_expectation_and_candidate_output(sample_report_context) -> None:
    report = render_report(sample_report_context)
    assert "Expected Output" in report
    assert "Candidate Output" in report
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/reports/test_write_markdown.py -v`
Expected: FAIL because the report writer does not exist.

**Step 3: Write minimal implementation**

```python
def render_report(context: ReportContext) -> str:
    template = Environment(loader=FileSystemLoader("templates")).get_template("report.md.j2")
    return template.render(**context.model_dump())
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/reports/test_write_markdown.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/reports/write_json.py src/llm_evaluator/reports/write_markdown.py templates/report.md.j2 tests/reports/test_write_markdown.py
git commit -m "feat: add evaluation report writers"
```

### Task 10: Wire the LangGraph workflow and CLI command

**Files:**
- Create: `src/llm_evaluator/graph/state.py`
- Create: `src/llm_evaluator/graph/workflow.py`
- Modify: `src/llm_evaluator/cli.py`
- Create: `tests/graph/test_workflow.py`

**Step 1: Write the failing test**

```python
from llm_evaluator.graph.workflow import build_workflow


def test_workflow_contains_expected_nodes() -> None:
    graph = build_workflow()
    assert "generate_benchmark_with_teacher" in graph.nodes
    assert "write_reports" in graph.nodes
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/graph/test_workflow.py -v`
Expected: FAIL because the workflow does not exist.

**Step 3: Write minimal implementation**

```python
def build_workflow() -> CompiledStateGraph:
    graph = StateGraph(EvaluatorState)
    graph.add_node("generate_benchmark_with_teacher", generate_benchmark_with_teacher)
    graph.add_node("write_reports", write_reports)
    return graph.compile()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/graph/test_workflow.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/graph/state.py src/llm_evaluator/graph/workflow.py src/llm_evaluator/cli.py tests/graph/test_workflow.py
git commit -m "feat: wire langgraph evaluation workflow"
```

### Task 11: Add end-to-end fixture coverage and sample config

**Files:**
- Create: `examples/sample-config.yaml`
- Create: `tests/integration/test_evaluate_command.py`
- Modify: `README.md`

**Step 1: Write the failing test**

```python
from typer.testing import CliRunner

from llm_evaluator.cli import app


def test_evaluate_command_writes_reports(tmp_path, monkeypatch) -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["evaluate", "--config", "examples/sample-config.yaml"])
    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_evaluate_command.py -v`
Expected: FAIL because the CLI is not wired to the workflow yet.

**Step 3: Write minimal implementation**

```python
@app.command()
def evaluate(config: Path) -> None:
    workflow = build_workflow()
    workflow.invoke({"config_path": config})
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_evaluate_command.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add examples/sample-config.yaml tests/integration/test_evaluate_command.py README.md src/llm_evaluator/cli.py
git commit -m "feat: add end-to-end evaluation command"
```

### Task 12: Run full verification and document operational usage

**Files:**
- Modify: `README.md`
- Modify: `docs/plans/2026-03-07-agentic-llm-evaluator-design.md`

**Step 1: Write the failing test**

There is no new feature test for this task. Use this task to verify the full test suite, tighten docs, and capture any missing operational notes discovered during execution.

**Step 2: Run test to verify current gaps**

Run: `pytest -v`
Expected: PASS for the full suite. If any test fails, stop and fix the root cause before continuing.

**Step 3: Write minimal implementation**

Document:
- required environment variables
- expected report artifacts
- known V1 limitations
- how to run the CLI locally

**Step 4: Run test to verify it passes**

Run: `pytest -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md docs/plans/2026-03-07-agentic-llm-evaluator-design.md
git commit -m "docs: finalize evaluator usage and verification notes"
```
