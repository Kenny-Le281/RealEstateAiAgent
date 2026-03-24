import requests
from requests.exceptions import ReadTimeout, RequestException

from config import OLLAMA_URL, MODEL_NAME, OLLAMA_TIMEOUT_SECONDS


def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT_SECONDS)
        response.raise_for_status()
    except ReadTimeout as exception:
        raise RuntimeError(f"Ollama request timed out after {OLLAMA_TIMEOUT_SECONDS} seconds.") from exception
    except RequestException as exception:
        raise RuntimeError(f"Ollama request failed: {exception}") from exception

    data = response.json()
    return data["message"]["content"]