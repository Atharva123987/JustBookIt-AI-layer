import os
import time

import requests
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
MAX_ATTEMPTS = 4
RETRY_BACKOFF_SECONDS = 0.5
def generate_embedding(text):
    url = "https://openrouter.ai/api/v1/embeddings"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    }

    payload = {
        "model": EMBEDDING_MODEL,
        "input": text,
        "encodingFormat": "float",
    }

    # The embedding provider intermittently returns 5xx/429, so retry
    # transient failures a few times before giving up.
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60,
            )
        except (requests.ConnectionError, requests.Timeout):
            if attempt == MAX_ATTEMPTS - 1:
                raise
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            continue

        retryable = response.status_code == 429 or response.status_code >= 500
        if retryable and attempt < MAX_ATTEMPTS - 1:
            time.sleep(RETRY_BACKOFF_SECONDS * (attempt + 1))
            continue
        break

    response.raise_for_status()

    data = response.json()

    return data["data"][0]["embedding"]