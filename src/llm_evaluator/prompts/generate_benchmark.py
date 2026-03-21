"""Prompt text for benchmark generation."""

GENERATE_BENCHMARK_PROMPT = """
Generate benchmark cases for the provided problem statement.
Return valid JSON with a top-level "cases" array.
Each case must include id, input_prompt, expected_output, and evaluation_criteria.
Every field value must be a JSON string.
expected_output must be a concise natural-language reference answer that captures the intended meaning.
Do not reduce expected_output to bare booleans or one-token labels unless the ideal answer is genuinely that short.
evaluation_criteria must instruct the judge to evaluate semantic correctness and meaning, not exact string matching.
""".strip()
