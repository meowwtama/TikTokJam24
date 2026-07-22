import os
import uuid
from datetime import datetime

from config import Config
from services import comfyui_service, ollama_service


class ValidationError(Exception):
    pass


def generate_images_from_story(story, num_images):
    story = (story or "").strip()
    if len(story) < Config.MIN_STORY_LENGTH:
        raise ValidationError(f"Story must be at least {Config.MIN_STORY_LENGTH} characters long.")

    if not (1 <= num_images <= Config.MAX_IMAGES):
        raise ValidationError(f"num_images must be between 1 and {Config.MAX_IMAGES}.")

    prompts = ollama_service.generate_image_prompts(story, num_images)

    batch_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    batch_dir = os.path.join(Config.OUTPUT_DIR, batch_id)

    results = []
    for index, prompt in enumerate(prompts, start=1):
        file_name = f"image_{index}.png"
        file_path = comfyui_service.generate_image(prompt, batch_dir, file_name)
        results.append({"prompt": prompt, "file_path": file_path})

    return results
