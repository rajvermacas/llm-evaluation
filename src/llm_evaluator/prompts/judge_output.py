"""Prompt text for teacher judging."""

JUDGE_OUTPUT_PROMPT = """
Judge the candidate output against the expected output and evaluation criteria.
Evaluate semantic correctness, relevance, and completeness.
Do not require exact wording or exact string matching.
Pass outputs that communicate the expected meaning even when phrasing differs.
Return valid JSON with "passed" and "rationale" fields.
""".strip()
