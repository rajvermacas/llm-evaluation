"""Prompt text for teacher judging."""

JUDGE_OUTPUT_PROMPT = """
Judge the candidate output against the expected output and evaluation criteria.
Return valid JSON with "passed" and "rationale" fields.
""".strip()
