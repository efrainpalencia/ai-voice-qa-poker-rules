import openai
import os
import logging
from flask import Flask
from flask_cors import CORS
from config import Config
from poker_routes import api
from load import load_rulebooks

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {"origins": ["https://ai-voice-qa-poker-rules.up.railway.app"]}})

# Allow all origins or specify the frontend domain explicitly
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# OpenAI API Key
openai.api_key = Config.OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

# Prepare file paths
file_paths = {
    "poker_tda": Config.TDA_FILE_PATH,
    "poker_hwhr": Config.HWHR_FILE_PATH,
}

# Load rulebooks
RULEBOOKS = load_rulebooks(file_paths)

# Define audio directory
AUDIO_DIR = "static/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Pass RULEBOOKS and AUDIO_DIR via app.config
app.config["RULEBOOKS"] = RULEBOOKS
app.config["AUDIO_DIR"] = AUDIO_DIR

# Register blueprint
app.register_blueprint(api, url_prefix="/api")

# Debug mode
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
