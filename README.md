# Story Image Generator

## Motivation
Our group understands the pains of creating eye-catching illustrations to accompany literary masterpieces. The process of transforming words into compelling visuals is both time-consuming and often requires a high level of artistic skill. For authors and content creators, this can be a significant barrier, potentially limiting the impact and reach of their work.

We believe that every story deserves to be brought to life with stunning visuals that captivate the audience and enhance the narrative experience. Our project aims to simplify the creation of illustrations, enabling writers to effortlessly generate beautiful images that complement and elevate their literary creations.

## Functionality
This application generates images from a user-provided story using two locally-hosted models:

- **Story to prompt(s)**: a local [Ollama](https://ollama.com) LLM reads the story and writes short, descriptive image-generation prompt(s) capturing its key scenes.
- **Prompt to image**: each prompt is injected into a [ComfyUI](https://github.com/comfyanonymous/ComfyUI) workflow (`backend/app/workflows/image_z_image_turbo_int8.json`, using the z-image-turbo-int8 model) and rendered by your local ComfyUI instance.
- **Saving results**: generated images are downloaded from ComfyUI and saved to a local `outputs/` directory, grouped per request.

## Architecture

```
backend/
  app.py                 Flask app + entrypoint
  config.py              Environment-driven configuration
  routes/                Flask blueprints (HTTP layer)
  controllers/           Request orchestration / validation
  services/
    ollama_service.py      Calls the local Ollama API to turn a story into prompt(s)
    comfyui_service.py     Queues the ComfyUI workflow, polls for results, saves images
  workflows/              ComfyUI workflow JSON template(s)
  outputs/                Generated images (git-ignored, mounted as a volume in Docker)
  Dockerfile / docker-compose.yml
```

Only the backend is containerized. **ComfyUI and Ollama are expected to already be running locally** (ComfyUI on port `8188`, Ollama on port `11434`) — the backend just calls out to them over HTTP.

## Prerequisites

- Python 3.10+ (if running without Docker) or Docker
- [Ollama](https://ollama.com) running locally with a model pulled (e.g. `ollama pull llama3`)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) running locally on port `8188`, with the models referenced in `image_z_image_turbo_int8.json` installed (`qwen_3_4b_fp8_mixed.safetensors`, `ae.safetensors`, `z_image_turbo_int8_convrot.safetensors`)

## Running locally (no Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # adjust OLLAMA_BASE_URL / COMFYUI_BASE_URL if needed
python app.py
```

The API will be available at `http://localhost:5000`.

## Running with Docker

Only the backend is dockerized — start ComfyUI and Ollama on the host first.

```bash
cd backend
docker compose up --build
```

The compose file points the container at `http://host.docker.internal:8188` (ComfyUI) and `http://host.docker.internal:11434` (Ollama) so it can reach services running on your host machine. Generated images are written to `backend/outputs/` on the host via a mounted volume.

## API

### `POST /api/images/generate`

Request body:

```json
{
  "story": "On a stormy night, Lily found an old, dusty key hidden in her grandmother's attic...",
  "num_images": 3
}
```

- `story` (string, required): must be at least `MIN_STORY_LENGTH` characters (default 20).
- `num_images` (int, optional): number of scenes/images to generate (default 1, max `MAX_IMAGES`, default 10).

Response:

```json
{
  "images": [
    { "prompt": "...", "file_path": "outputs/20260723_143000_ab12cd34/image_1.png" }
  ]
}
```

### `GET /api/images/health`

Simple health check, returns `{"status": "ok"}`.

## Configuration

All configuration is via environment variables (see `backend/.env.example`):

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Base URL of the local Ollama server |
| `OLLAMA_MODEL` | `llama3` | Ollama model used to generate prompts |
| `OLLAMA_TIMEOUT` | `120` | Timeout (seconds) for Ollama requests |
| `COMFYUI_BASE_URL` | `http://localhost:8188` | Base URL of the local ComfyUI server |
| `COMFYUI_TIMEOUT` | `300` | Max time (seconds) to wait for ComfyUI to finish an image |
| `COMFYUI_POLL_INTERVAL` | `2` | Seconds between polls of ComfyUI's `/history` endpoint |
| `OUTPUT_DIR` | `outputs` | Directory generated images are saved to |
| `MIN_STORY_LENGTH` | `20` | Minimum accepted story length |
| `MAX_IMAGES` | `10` | Maximum images allowed per request |
