# LLM Evaluator

CLI-first LangGraph evaluation tool for benchmarking OpenRouter models with a teacher model.

## Requirements

- Python 3.12
- `uv` installed locally
- `OPENROUTER_API_KEY` set in the environment or a local `.env` file

## Configuration

Create a YAML file with these required fields:

```yaml
teacher_model: openai/gpt-4o-mini
candidate_models:
  - openai/gpt-4o-mini
  - anthropic/claude-3.5-haiku
problem_statement: Classify each prompt according to the requested label.
benchmark_case_count: 3
output_dir: reports/sample-run
```

See [examples/sample-config.yaml](/workspaces/llm-evaluation/examples/sample-config.yaml).

Create a local `.env` from [`.env.example`](/workspaces/llm-evaluation/.env.example):

```bash
cp .env.example .env
```

## Run Locally

```bash
cd /workspaces/llm-evaluation
uv sync --dev
cp .env.example .env
uv run llm-evaluator evaluate --config examples/sample-config.yaml
```

## Run Tests

```bash
cd /workspaces/llm-evaluation
uv run pytest
```

## Artifacts

Each run writes these files into `output_dir`:

- `config.yaml`
- `benchmark.json`
- `results.json`
- `report.md`

## Current Limitations

- Version 1 uses a single teacher model for both benchmark generation and judgment.
- The workflow fails fast on malformed provider responses instead of retrying.
- Cost accounting depends on OpenRouter returning `usage.cost` in completion responses.
