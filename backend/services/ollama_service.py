import re

import requests

from config import Config

SYSTEM_PROMPT_TEMPLATE = (
    "You are a storybook illustrator. Read the story below and write exactly {num_images} "
    "image-generation prompt(s) describing key scenes from it, one per line, with no numbering "
    "or extra commentary. Each prompt must be a single, richly descriptive sentence in English "
    "suitable for an AI image generator (subject, setting, mood, lighting)."
)


class OllamaError(Exception):
    pass


def _strip_list_markers(line):
    line = line.strip(" \t-*")
    return re.sub(r"^\d+[.)]\s*", "", line)


def generate_image_prompts(story, num_images):
    """Ask the local Ollama LLM to turn a story into `num_images` image prompt(s)."""
    payload = {
        "model": Config.OLLAMA_MODEL,
        "prompt": story,
        "system": SYSTEM_PROMPT_TEMPLATE.format(num_images=num_images),
        "stream": False,
    }

    try:
        response = requests.post(
            f"{Config.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=Config.OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise OllamaError(f"Failed to reach Ollama at {Config.OLLAMA_BASE_URL}: {exc}") from exc

    text = response.json().get("response", "").strip()
    if not text:
        raise OllamaError("Ollama returned an empty response")

    prompts = [_strip_list_markers(line) for line in text.splitlines() if line.strip()]
    prompts = [p for p in prompts if p]

    if not prompts:
        raise OllamaError("Could not parse any prompts from Ollama's response")

    return prompts[:num_images]
