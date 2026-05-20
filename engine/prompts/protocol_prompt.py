def build_protocol_prompt(filename: str, code: str) -> list[dict]:
    system = """You are a cryptography detector.
Return ONLY valid JSON. 
Do NOT return plain text.
Do NOT return markdown.
Do NOT add explanations."""

    user = f"""
Task:
Return:
{{
"PROTOCOL"
}}

CODE:
{code}
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
