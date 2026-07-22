import os

from flask import Flask

from config import Config
from routes.image_routes import image_bp

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

app.register_blueprint(image_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
