# UV Support Design

**Date:** 2026-03-19

## Goal

Add first-class `uv` support to the project by declaring uv-compatible development metadata in `pyproject.toml`, documenting `uv` as the primary local workflow, and committing a `uv.lock` file for reproducible environments.

## Current State

- The project already uses a standard setuptools build backend.
- Development dependencies are defined under `project.optional-dependencies.dev`.
- The README documents direct `python` execution instead of `uv sync` and `uv run`.
- There is no `uv.lock` file in the repository.

## Decision

- Keep setuptools as the build backend.
- Move development dependencies to top-level `dependency-groups`, which is the current `uv`-native format.
- Add a small `tool.uv` section to make the default sync behavior explicit for the `dev` group.
- Update the README so setup and execution use `uv`.
- Generate and commit `uv.lock`.

## Non-Goals

- No application behavior changes.
- No dependency upgrades beyond what `uv` resolves from the current version constraints.
- No packaging backend migration.

## Validation

- `uv sync --dev`
- `uv run llm-evaluator --help`
- `uv run pytest`
