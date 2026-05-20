def build_certificate_prompt(filename: str, code: str) -> list[dict]:
    system = """You are a cryptography detector.
Return ONLY valid JSON. 
Do NOT return plain text.
Do NOT return markdown.
Do NOT add explanations."""

    user = f"""
Task:
Return 
{{
"CERTIFICATE"
}}
CODE:
{code}
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
