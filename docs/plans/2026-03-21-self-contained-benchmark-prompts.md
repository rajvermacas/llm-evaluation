# Self-Contained Benchmark Prompts Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make every teacher-generated benchmark `input_prompt` a standalone candidate-facing instruction derived from the configured `problem_statement`, including the case-specific text and expected response shape.

**Architecture:** Keep the schema unchanged and fix the contract at the benchmark-generation prompt layer. The teacher model will be instructed to synthesize complete `input_prompt` values from the generic `problem_statement`, while tests verify that the generated request explicitly requires standalone prompts and a classification-plus-reason style answer without hardcoding any domain wording.

**Tech Stack:** Python 3.12, pytest, Pydantic, OpenRouter client prompt builder

---

### Task 1: Strengthen benchmark-generation prompt contract

**Files:**
- Modify: `src/llm_evaluator/prompts/generate_benchmark.py`
- Modify: `src/llm_evaluator/providers/openrouter_client.py`
- Test: `tests/providers/test_openrouter_client.py`

**Step 1: Write the failing test**

```python
def test_generate_benchmark_requires_self_contained_input_prompts(monkeypatch) -> None:
    ...
    assert "input_prompt must be a fully self-contained instruction" in message
    assert "derived from the provided problem statement" in message
    assert "expected response format" in message
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/providers/test_openrouter_client.py::test_generate_benchmark_requires_self_contained_input_prompts -v`
Expected: FAIL because the current prompt does not require standalone candidate-facing prompts.

**Step 3: Write minimal implementation**

```python
GENERATE_BENCHMARK_PROMPT = """
...
input_prompt must be a fully self-contained instruction for the candidate model.
It must be derived from the provided problem statement.
It must include the case-specific content and define the expected response format.
...
""".strip()
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/providers/test_openrouter_client.py::test_generate_benchmark_requires_self_contained_input_prompts -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/llm_evaluator/prompts/generate_benchmark.py src/llm_evaluator/providers/openrouter_client.py tests/providers/test_openrouter_client.py
git commit -m "fix: require self-contained benchmark prompts"
```

### Task 2: Add benchmark payload coverage for the new prompt shape

**Files:**
- Modify: `tests/graph/test_generate_benchmark.py`

**Step 1: Write the failing test**

```python
def test_build_benchmark_cases_accepts_self_contained_input_prompt() -> None:
    payload = {
        "cases": [
            {
                "id": "case-1",
                "input_prompt": "Task... Text... Answer with classification and brief reason.",
                ...
            }
        ]
    }
    cases = build_benchmark_cases(payload, expected_count=1)
    assert cases[0].input_prompt.startswith("Task")
```

**Step 2: Run test to verify it fails if needed**

Run: `uv run pytest tests/graph/test_generate_benchmark.py::test_build_benchmark_cases_accepts_self_contained_input_prompt -v`
Expected: PASS or FAIL. If it already passes, keep the test as regression coverage and continue.

**Step 3: Keep implementation minimal**

```python
# No schema change is expected.
```

**Step 4: Run the graph tests**

Run: `uv run pytest tests/graph/test_generate_benchmark.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/graph/test_generate_benchmark.py
git commit -m "test: cover self-contained benchmark prompts"
```

### Task 3: Verify the full prompt-related surface

**Files:**
- Verify: `tests/providers/test_openrouter_client.py`
- Verify: `tests/graph/test_generate_benchmark.py`

**Step 1: Run targeted verification**

Run: `uv run pytest tests/providers/test_openrouter_client.py tests/graph/test_generate_benchmark.py -v`
Expected: PASS

**Step 2: Review changed files**

Run: `git diff -- src/llm_evaluator/prompts/generate_benchmark.py src/llm_evaluator/providers/openrouter_client.py tests/providers/test_openrouter_client.py tests/graph/test_generate_benchmark.py`
Expected: Diff shows only prompt-contract and regression-test updates.

**Step 3: Commit**

```bash
git add src/llm_evaluator/prompts/generate_benchmark.py src/llm_evaluator/providers/openrouter_client.py tests/providers/test_openrouter_client.py tests/graph/test_generate_benchmark.py
git commit -m "fix: generate self-contained benchmark prompts"
```
