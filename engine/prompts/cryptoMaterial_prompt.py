def build_cryptoMaterial_prompt(filename: str, code: str) -> list[dict]:
    system = """You are a cryptography detector.
Task:
Analyse the provided code and detect cryptographic materials explicitly evidenced by cryptographic API calls.
Detect only concrete cryptographic VALUES produced or output by the shown cryptographic API call.
Do not detect API objects or algorithm configuration.

Detection rules:
- Create one COMPONENT per unique cryptographic material
- Detect crypto material only when the code explicitly creates, returns, derives, obtains, exports, or outputs a concrete cryptographic material object or value.
- A crypto material COMPONENT must represent only the concrete material value produced, returned, derived, exported, or output by the evidenced API call.
- If the API call only initializes or configures an algorithm, and no material value is produced or returned by that call, do not report crypto material.


Field rules:
- type must be one of:
  private-key, public-key, secret-key, key, ciphertext, signature, digest,
  initialization-vector, nonce, seed, salt, shared-secret, tag,
  additional-data, password, credential, token, other, unknown, null
- size: The size of the cryptographic asset (in bits) 
- Set size only when it is explicitly evidenced by the code or directly implied by the produced material’s known byte length in the shown code.

Negative detection rule:
- Do NOT report crypto material for getInstance(...), init(...), update(...), or constructor/configuration


EVIDENCE rules:
- additionalContext must contain the exact cryptographic API call
  that produces the material
    
Output format:
[
  {
    "COMPONENT": {
      "name": "",
      "type": "",
      "size": ""
    },
    "EVIDENCE": {
      "additionalContext": []
    }
  }
]

If no crypto material is found, return exactly []

    
Return ONLY valid JSON. 
Do NOT return plain text.
Do NOT return markdown.
Do NOT add explanations."""

    user = f"""
Task:

CODE:
{code}
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
