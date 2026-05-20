def build_general_prompt(filename: str, code: str) -> list[dict]:
    system = """You are a cryptography detector.
Return ONLY valid JSON. 
Do NOT return plain text.
Do NOT return markdown.
Do NOT add explanations."""

    user = f"""
Task:
Analyze the provided code and detect cryptographic assets explicitly evidenced by cryptographic API calls.

Detect only these top-level asset types:
- algorithm
- certificate
- protocol

Detection rules:
- Create one COMPONENT per unique cryptographic asset
- If multiple API calls refer to the same object, merge them into one COMPONENT
- Different operations of the same asset do NOT create separate COMPONENTs
- Put all explicitly evidenced operations for that asset into cryptoFunctions
- Nested cryptographic API calls must be returned as separate COMPONENTS only if they correspond to different cryptographic assets
- Detect only cryptographic assets directly evidenced by the shown code.
- Do not infer hidden helper algorithms unless their name is explicitly shown.
- Do NOT merge different algorithms into a single COMPONENT
- Only add a cryptoFunction if the corresponding operation is explicitly executed in the code.
- Example: MessageDigest.getInstance(...) alone does NOT prove cryptoFunctions ["digest"].
- MessageDigest.digest(...) DOES prove cryptoFunctions ["digest"].


- COMPONENT = algorithm / certificate / protocol
- RELATED_CRYPTO_MATERIAL = key, signature, digest, ciphertext, iv, nonce, etc.
- Never promote RELATED_CRYPTO_MATERIAL to a top-level COMPONENT

For each finding, use EXACTLY this structure.
All fields must always be present.
If a field does not apply, use null.
Use null when a field is not applicable.
Use "unknown" when the field is applicable, but the value cannot be determined from the code.

COMPONENT.name rules:
- If the exact algorithm name appears as a string literal in the cryptographic API call, use that exact name.
- Otherwise, if the algorithm name comes from a variable, parameter, field, or method call and is not resolved in the shown code, use "unknown".
- COMPONENT.name must be the algorithm/protocol/certificate name, not an API class name.
- Do not use names like MessageDigest, Cipher, or Signature as algorithm names.\
Name priority:
- Prefer an explicit literal algorithm name over "unknown".

[
  {{
    "COMPONENT": {{
      "name": "",
      "assetType": "",
      "primitive": "",
      "parameterSetIdentifier": "",
      "mode": "",
      "padding": "",
      "cryptoFunctions": []
    }},
    "RELATED_CRYPTO_MATERIAL": [
    {{
      "name": "",
      "relatedCryptoMaterialType": "",
      "size": ""
    }}
    ],
    "EVIDENCE": {{
      "additionalContext": []
    }}
  }}
]

Field rules:

- name: name of the cryptographic asset

- assetType must be one of: algorithm, certificate, protocol

- If assetType is not algorithm:
  set primitive, parameterSetIdentifier, mode, padding, cryptoFunctions to null

- primitive describes WHAT the algorithm is (its cryptographic type)
- primitive must be one of:
  drbg, mac, block-cipher, stream-cipher, signature, hash, pke, xof, kdf,
  key-agree, kem, ae, combiner, other, unknown
  
- parameterSetIdentifier is an identifier for the parameter set of the cryptographic algorithm (in bits)

- mode must be one of:
  cbc, ecb, ccm, gcm, cfb, ofb, ctr, other, unknown, null

- padding must be one of:
  pkcs5, pkcs7, pkcs1v15, oaep, raw, other, unknown, null

- cryptoFunctions describes WHAT OPERATION is performed using that algorithm
- cryptoFunctions must contain one or more of:
  null, generate, keygen, encrypt, decrypt, digest, tag, keyderive,
  sign, verify, encapsulate, decapsulate, other, unknown

RELATED_CRYPTO_MATERIAL rules:
- Use this section to list all cryptographic material explicitly produced, returned, derived, signed, encrypted, decrypted, generated, or exported by any API calls associated with this COMPONENT.
Each material entry MUST correspond to a specific API call.
- If no such material is explicitly produced, set:
  name: null
  relatedCryptoMaterialType: null
  size: null
- relatedCryptoMaterialType must be one of:
  private-key, public-key, secret-key, key, ciphertext, signature, digest,
  initialization-vector, nonce, seed, salt, shared-secret, tag,
  additional-data, password, credential, token, other, unknown, null
- size: The size of the cryptographic asset (in bits)

EVIDENCE rules:
- additionalContext must contain the exact cryptographic API call
  that evidences the asset
- If multiple calls correspond to the same asset, include representative call for each cryptoFunctions

Additional rules:
- Detect only assets explicitly evidenced by the code
- Do NOT infer missing information
- If no cryptographic assets are found, return exactly []

Nested helper algorithm rule:
- Padding schemes and padding helper objects must NEVER be returned as separate COMPONENTS. Only in the padding field of the main component
- Any explicitly instantiated or called cryptographic algorithm MUST be returned as a separate COMPONENT,
  even if it appears only as a parameter of another cryptographic API call.
- This includes nested algorithm constructors or factory calls inside another cryptographic call.
- Do NOT merge different explicitly instantiated algorithms into one COMPONENT,
  even when they belong to the same higher-level construction.
  


CODE:
{code}
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
