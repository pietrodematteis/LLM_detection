import json
from pathlib import Path

# from .prompts.general_prompt import build_general_prompt
from .ollama_client import call_ollama
from .prompt_router import build_prompt_router
from .prompts.assetDetection_prompt import build_asset_prompt


def detect_crypto_report(
        input_path: str,
        code: str,
        ollama_base: str,
        model: str,
        temperature: float = 0,
        timeout: int = 180,
        num_ctx: int = 4096,
) -> str:

    filename = Path(input_path).name

    # general prompt
    # code = Path(input_path).read_text(encoding="utf-8")
    # messages = build_general_prompt(Path(input_path).name, code)
    # return call_ollama(ollama_base, model, messages, temperature=temperature, timeout=timeout, num_ctx=num_ctx)


    # 1. Asset detection
    asset_messages = build_asset_prompt(filename, code)
    raw_asset_results = call_ollama(ollama_base, model, asset_messages, temperature, timeout, num_ctx)
    asset_results_text = raw_asset_results.strip().replace("```json", "").replace("```", "").strip()
    print(asset_results_text)
    asset_results = json.loads(asset_results_text)
    assets = asset_results.get("assets", [])

    print("ASSET RESULTS: ", assets)

    # 2. crypto detection
    reports = []
    for asset in assets:
        prompt_builder = build_prompt_router(asset)

        if prompt_builder is None:
            continue

        messages = prompt_builder(filename, code)
        report = call_ollama(ollama_base, model, messages, temperature, timeout, num_ctx)

        reports.append(report)

    return reports
