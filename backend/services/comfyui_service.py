import json
import time
import uuid
from pathlib import Path

import requests

from config import Config

WORKFLOW_PATH = Path(__file__).resolve().parent.parent / "workflows" / "image_z_image_turbo_int8.json"

# Node IDs inside image_z_image_turbo_int8.json
PROMPT_NODE_ID = "57:27"  # CLIPTextEncode (Prompt) - "text" input gets overwritten per request
SAVE_IMAGE_NODE_ID = "9"  # SaveImage - where the generated image comes from


class ComfyUIError(Exception):
    pass


def _load_workflow():
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _build_workflow(prompt_text):
    workflow = _load_workflow()
    workflow[PROMPT_NODE_ID]["inputs"]["text"] = prompt_text
    return workflow


def _queue_prompt(prompt_text):
    payload = {"prompt": _build_workflow(prompt_text), "client_id": str(uuid.uuid4())}

    try:
        response = requests.post(f"{Config.COMFYUI_BASE_URL}/prompt", json=payload, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ComfyUIError(f"Failed to reach ComfyUI at {Config.COMFYUI_BASE_URL}: {exc}") from exc

    data = response.json()
    if data.get("node_errors"):
        raise ComfyUIError(f"ComfyUI rejected the workflow: {data['node_errors']}")

    return data["prompt_id"]


def _wait_for_result(prompt_id):
    deadline = time.time() + Config.COMFYUI_TIMEOUT
    while time.time() < deadline:
        response = requests.get(f"{Config.COMFYUI_BASE_URL}/history/{prompt_id}", timeout=10)
        response.raise_for_status()
        history = response.json()
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(Config.COMFYUI_POLL_INTERVAL)

    raise ComfyUIError(f"Timed out waiting for ComfyUI (prompt_id={prompt_id})")


def _extract_image_ref(history_entry):
    status = history_entry.get("status", {})
    if status.get("status_str") == "error":
        raise ComfyUIError(f"ComfyUI reported an error while generating the image: {status}")

    images = history_entry.get("outputs", {}).get(SAVE_IMAGE_NODE_ID, {}).get("images")
    if not images:
        raise ComfyUIError("ComfyUI finished but returned no image output")

    return images[0]


def _download_image(image_ref):
    params = {
        "filename": image_ref["filename"],
        "subfolder": image_ref.get("subfolder", ""),
        "type": image_ref.get("type", "output"),
    }
    response = requests.get(f"{Config.COMFYUI_BASE_URL}/view", params=params, timeout=60)
    response.raise_for_status()
    return response.content


def generate_image(prompt_text, output_dir, file_name):
    """Runs the z-image-turbo workflow with `prompt_text` and saves the result to
    `output_dir/file_name`. Returns the saved file's path."""
    prompt_id = _queue_prompt(prompt_text)
    history_entry = _wait_for_result(prompt_id)
    image_ref = _extract_image_ref(history_entry)
    image_bytes = _download_image(image_ref)

    output_path = Path(output_dir) / file_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)

    return str(output_path)
