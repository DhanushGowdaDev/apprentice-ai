import json

import httpx


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "gemma4:e2b"


def generate_json(prompt: str) -> dict:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        },
    }

    response = httpx.post(
        OLLAMA_URL,
        json=payload,
        timeout=180.0,
    )

    response.raise_for_status()

    data = response.json()

    text = data.get("response", "").strip()

    if not text:
        raise RuntimeError("Gemma returned an empty response.")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Gemma returned invalid JSON: {text[:500]}"
        ) from exc