# Timestamped Output Directory Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Write each evaluation run into a human-readable IST timestamp subdirectory beneath the configured `output_dir`.

**Architecture:** Keep the workflow contract unchanged after run-context initialization by resolving the configured base directory into a concrete run directory once. Add a small output-path helper for timestamp generation and directory creation, update the workflow to use it, and adjust tests and docs to reflect the new artifact location.

**Tech Stack:** Python, pathlib, zoneinfo, LangGraph, Typer, pytest

---

### Task 1: Add failing coverage for timestamped artifact output

**Files:**
- Modify: `tests/integration/test_evaluate_command.py`

**Step 1: Write the failing test**

- Replace the direct artifact path assertions with expectations that the configured base directory contains exactly one timestamped child directory.
- Assert that `config.yaml`, `benchmark.json`, `results.json`, and `report.md` exist inside that child directory.

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_evaluate_command.py -v`
Expected: FAIL because the workflow still writes artifacts directly into the base directory.

**Step 3: Write minimal implementation**

- Keep the test focused on externally visible behavior instead of internal helper functions.

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_evaluate_command.py -v`
Expected: PASS after the workflow change is implemented.

**Step 5: Commit**

```bash
git add tests/integration/test_evaluate_command.py
git commit -m "test: cover timestamped artifact output"
```

### Task 2: Add a run-directory helper and wire it into the workflow

**Files:**
- Create: `src/llm_evaluator/services/output_paths.py`
- Modify: `src/llm_evaluator/graph/workflow.py`

**Step 1: Write the failing test**

- Use the integration test from Task 1 as the failing behavior check.

**Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_evaluate_command.py -v`
Expected: FAIL until the workflow uses a timestamped run directory.

**Step 3: Write minimal implementation**

- Add a helper that builds the IST timestamp string with `ZoneInfo("Asia/Kolkata")`.
- Create a timestamped child directory under the configured base directory.
- Raise `FileExistsError` if the target run directory already exists.
- Update `load_run_context` to copy `config.yaml` into the timestamped run directory and store that directory in state as `output_dir`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/integration/test_evaluate_command.py -v`
Expected: PASS and logs show the resolved timestamped output directory.

**Step 5: Commit**

```bash
git add src/llm_evaluator/services/output_paths.py src/llm_evaluator/graph/workflow.py
git commit -m "feat: write artifacts to timestamped run directories"
```

### Task 3: Update user-facing docs and run full verification

**Files:**
- Modify: `README.md`
- Modify: `examples/sample-config.yaml`

**Step 1: Write the failing test**

- Inspect the README and sample config and confirm they still imply that artifacts are written directly into `output_dir`.

**Step 2: Run test to verify it fails**

Run: `rg -n "writes these files into `output_dir`|reports/sample-run" README.md examples/sample-config.yaml`
Expected: Matches that need to be updated.

**Step 3: Write minimal implementation**

- Describe `output_dir` as the parent directory for timestamped run folders.
- Update the sample path and output description accordingly.

**Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: PASS.

**Step 5: Commit**

```bash
git add README.md examples/sample-config.yaml
git commit -m "docs: describe timestamped output directories"
```
