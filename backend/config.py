import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Ollama (local LLM used to turn a story into image-generation prompts)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))

    # ComfyUI (local image generation backend)
    COMFYUI_BASE_URL = os.getenv("COMFYUI_BASE_URL", "http://localhost:8188")
    COMFYUI_TIMEOUT = int(os.getenv("COMFYUI_TIMEOUT", "300"))
    COMFYUI_POLL_INTERVAL = float(os.getenv("COMFYUI_POLL_INTERVAL", "2"))

    # Where generated images are saved on disk
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs")

    # Request validation
    MIN_STORY_LENGTH = int(os.getenv("MIN_STORY_LENGTH", "20"))
    MAX_IMAGES = int(os.getenv("MAX_IMAGES", "10"))
