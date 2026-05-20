from engine.prompts.algorithm_prompt import build_algorithm_prompt
from engine.prompts.cryptoMaterial_prompt import build_cryptoMaterial_prompt
from engine.prompts.certificate_prompt import build_certificate_prompt
from engine.prompts.protocol_prompt import build_protocol_prompt

CRYPTO_ASSET_PROMPT = {
    "algorithm": build_algorithm_prompt,
    "related-crypto-material": build_cryptoMaterial_prompt,
    "certificate": build_certificate_prompt,
    "protocol": build_protocol_prompt,
}

def build_prompt_router(asset: str):
    return CRYPTO_ASSET_PROMPT.get(asset)