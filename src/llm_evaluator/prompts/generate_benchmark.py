"""Prompt text for benchmark generation."""

BENCHMARK_CASE_REQUIREMENTS = """
Each case must include id, input_prompt, expected_output, and evaluation_criteria.
Every field value must be a JSON string.
input_prompt must be a fully self-contained instruction for the candidate model.
input_prompt must be derived from the provided problem statement and must not assume hidden context.
input_prompt must include the case-specific content to analyze.
input_prompt must specify the expected response format, including the exact task output requested by the problem statement and any required supporting explanation.
expected_output must be a concise natural-language reference answer that captures the intended meaning.
Do not reduce expected_output to bare booleans or one-token labels unless the ideal answer is genuinely that short.
evaluation_criteria must instruct the judge to evaluate semantic correctness and meaning, not exact string matching.
""".strip()

GENERATE_BENCHMARK_PROMPT = """
Generate benchmark cases for the provided problem statement.
Return valid JSON with a top-level "cases" array.
""".strip()
