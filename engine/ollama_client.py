import requests


def call_ollama(ollama_base: str, model: str, messages, temperature: float = 0, timeout: int = 180, num_ctx: int = 4096) -> str:

    # 1) /api/chat
    chat_url = f"{ollama_base}/api/chat"
    chat_payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "top_k": 1,
        },
    }

    try:
        r = requests.post(chat_url, json=chat_payload, timeout=timeout)
        if r.status_code == 200:
            return r.json()["message"]["content"]
        if r.status_code not in (400, 404):
            raise RuntimeError(f"/api/chat error {r.status_code}: {r.text}")
    except requests.RequestException:
        pass

