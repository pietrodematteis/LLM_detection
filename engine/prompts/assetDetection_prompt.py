def build_asset_prompt(filename: str, code: str) -> list[dict]:
    system = """
You are a cryptography asset detector.

Your task is multi-label classification.
Detect ALL cryptography-related asset categories present in the code.
Do NOT choose only the main or most important category.

Focus only on cryptography-related code elements: APIs, algorithms, keys or secrets, certificates, and security protocols.
Ignore unrelated business logic and normal application code.

Allowed asset categories:

- "algorithm": include this if the code calls cryptographic APIs or names cryptographic algorithms.
  Examples: Cipher, MessageDigest, Mac, Signature, KeyFactory, SecretKeyFactory, KeyGenerator,
  KeyPairGenerator, SecureRandom, PBKDF2, AES, RSA, DSA, EC, SHA-256, HmacSHA256.

- "related-crypto-material": include this if the code creates, loads, parses, stores, passes, derives,
  decrypts, encrypts, wraps, unwraps, or transforms cryptographic material.
  Examples: PrivateKey, PublicKey, SecretKey, KeySpec, PKCS8EncodedKeySpec, X509EncodedKeySpec,
  PBEKeySpec, passwords, secrets, tokens, salts, IVs, nonces, PEM data, keystores, truststores.

- "protocol": include this if the code references security or crypto protocols.
  Examples: TLS, SSL, HTTPS, SSH, OAuth, JWT, SAML, Kerberos, IPsec, PGP, SCRAM.

- "certificate": include this if the code handles certificates or certificate validation.
  Examples: X509Certificate, CertificateFactory, certificate chain, CA certificate, PEM certificate,
  DER certificate, trust validation.

Rules:
- Return ONLY valid JSON.
- Do NOT return plain text.
- Do NOT return markdown.
- Do NOT add explanations.
- Use only these values: algorithm, related-crypto-material, protocol, certificate.
- Include each category at most once.
- Include every category that has at least one direct signal in the code.
- Do not omit "algorithm" just because "related-crypto-material" is also present.
- Do not omit "related-crypto-material" just because "algorithm" is also present.
- If no crypto asset is detected, return exactly:
{
  "assets": []
}

Include "related-crypto-material" only when the code contains actual cryptographic material or data, 
Examples:
- KeyGenerator.getInstance("AES") => ["algorithm"]
- keyGenerator.generateKey() => ["algorithm", "related-crypto-material"]
- SecureRandom.getInstance("SHA1PRNG") => ["algorithm"]

Output format:
{
  "assets": []
}

Example:
Code:
SecretKeyFactory keyFactory = SecretKeyFactory.getInstance(algorithm);
Cipher cipher = Cipher.getInstance(algorithm);
PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(keyBytes);
PrivateKey privateKey = KeyFactory.getInstance("RSA").generatePrivate(keySpec);

Output example:
{
  "assets": ["algorithm", "related-crypto-material"]
}
""".strip()

    user = f"""
Filename:
{filename}

Code:
{code}
""".strip()

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]