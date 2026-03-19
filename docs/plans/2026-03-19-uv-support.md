# UV Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add first-class `uv` support to the project configuration and developer workflow without changing runtime behavior.

**Architecture:** Keep setuptools as the build backend and make `uv` the environment manager layered on top of the existing package metadata. Development dependencies move into top-level `dependency-groups`, `uv` defaults are declared explicitly, docs switch to `uv` commands, and a committed `uv.lock` captures the resolved environment.

**Tech Stack:** Python, setuptools, uv, pytest, Typer

---

### Task 1: Update project metadata for uv

**Files:**
- Modify: `pyproject.toml`

**Step 1: Write the failing test**

Inspect `pyproject.toml` and confirm there is no `dependency-groups` table and no `tool.uv` section.

**Step 2: Run test to verify it fails**

Run: `rg -n "dependency-groups|tool\\.uv" pyproject.toml`
Expected: no matches.

**Step 3: Write minimal implementation**

- Move the `pytest` development dependency into a top-level `[dependency-groups]` table.
- Add a `[tool.uv]` section that makes the default `dev` group explicit.

**Step 4: Run test to verify it passes**

Run: `sed -n '1,220p' pyproject.toml`
Expected: the file contains `[dependency-groups]` and `[tool.uv]`.

**Step 5: Commit**

```bash
git add pyproject.toml
git commit -m "build: add uv project metadata"
```

### Task 2: Switch developer documentation to uv

**Files:**
- Modify: `README.md`

**Step 1: Write the failing test**

Inspect `README.md` and confirm setup and execution instructions do not mention `uv`.

**Step 2: Run test to verify it fails**

Run: `rg -n "uv " README.md`
Expected: no matches.

**Step 3: Write minimal implementation**

- Document `uv` as a requirement.
- Replace local setup instructions with `uv sync --dev`.
- Replace execution instructions with `uv run llm-evaluator ...` and `uv run pytest`.

**Step 4: Run test to verify it passes**

Run: `sed -n '1,220p' README.md`
Expected: setup and run sections use `uv`.

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: adopt uv workflow"
```

### Task 3: Generate the uv lockfile and verify the workflow

**Files:**
- Create: `uv.lock`

**Step 1: Write the failing test**

Confirm that `uv.lock` does not exist.

**Step 2: Run test to verify it fails**

Run: `test -f uv.lock`
Expected: exit code `1`.

**Step 3: Write minimal implementation**

Run `uv sync --dev` to create the lockfile and install the project environment.

**Step 4: Run test to verify it passes**

Run: `uv run llm-evaluator --help`
Expected: exit code `0` and help output for the CLI.

Run: `uv run pytest`
Expected: exit code `0`.

**Step 5: Commit**

```bash
git add uv.lock
git commit -m "build: lock uv environment"
```
