from flask import Blueprint, jsonify, request

from controllers import image_controller
from controllers.image_controller import ValidationError
from services.comfyui_service import ComfyUIError
from services.ollama_service import OllamaError

image_bp = Blueprint("images", __name__, url_prefix="/api/images")


@image_bp.route("/generate", methods=["POST"])
def generate_images():
    data = request.get_json(silent=True) or {}
    story = data.get("story", "")
    num_images = int(data.get("num_images", 1))

    try:
        results = image_controller.generate_images_from_story(story, num_images)
    except ValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except OllamaError as exc:
        return jsonify({"error": f"Ollama error: {exc}"}), 502
    except ComfyUIError as exc:
        return jsonify({"error": f"ComfyUI error: {exc}"}), 502

    return jsonify({"images": results}), 200


@image_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200
