"""Prompt text for benchmark generation."""

GENERATE_BENCHMARK_PROMPT = """
Generate benchmark cases for the provided problem statement.
Return valid JSON with a top-level "cases" array.
Each case must include id, input_prompt, expected_output, and evaluation_criteria.
Every field value must be a JSON string.
Use string literals like "true" or "false", never bare booleans.
""".strip()
