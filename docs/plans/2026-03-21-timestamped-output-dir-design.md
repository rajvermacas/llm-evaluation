# Timestamped Output Directory Design

**Date:** 2026-03-21

## Goal

Change artifact writing so `config.output_dir` is treated as a parent directory and each evaluation run writes its artifacts into a new timestamped subdirectory in IST.

## Current State

- The workflow loads `output_dir` directly from config in `src/llm_evaluator/graph/workflow.py`.
- The workflow immediately creates that directory and copies the input config into it as `config.yaml`.
- `benchmark.json`, `results.json`, and `report.md` are written directly into that same directory.
- The README and integration test currently describe `output_dir` as the final artifact directory.

## Decision

- Interpret `config.output_dir` as the base directory for evaluation runs.
- Create a human-readable timestamped subdirectory using `Asia/Kolkata` and a format like `2026-03-21_08-45-12_IST`.
- Persist `config.yaml`, `benchmark.json`, `results.json`, and `report.md` inside that timestamped run directory.
- Keep the timestamp creation logic in run-context setup so the rest of the workflow can continue using a single resolved `output_dir`.
- Fail fast with a clear exception if the timestamped directory already exists instead of silently reusing or renaming it.

## Non-Goals

- No new config fields for timestamp formatting or timezone.
- No changes to benchmark generation, model execution, aggregation, or report content.
- No fallback timestamp names or collision-handling suffixes.

## Validation

- Update integration tests to assert artifacts are written inside one timestamped child directory beneath the configured base path.
- Run targeted tests for the evaluate command.
- Run the full test suite to confirm the workflow still passes end to end.
