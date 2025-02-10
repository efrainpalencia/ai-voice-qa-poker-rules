import openai
import os
import logging
from app import app
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.chains import get_qa_chain
from app.config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set OpenAI API key
openai.api_key = Config.OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)


@app.route("/record", methods=["POST"])
def record():
    """Handles audio file upload, transcribes, and generates AI response."""
    if not openai.api_key:
        return jsonify({"error": "Missing OpenAI API key"}), 500

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    file = request.files["audio"]
    file_path = "recording.webm"

    try:
        file.save(file_path)

        # Transcribe using OpenAI Whisper API
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1", file=audio_file)

        text = transcript.get("text", "").strip()
        if not text:
            return jsonify({"error": "Transcription failed"}), 500

        # Get AI-generated response
        output = get_qa_chain().run(text)

        # Convert AI response to speech using OpenAI TTS
        speech_response = openai.Audio.create(
            model="tts-1",
            voice="alloy",
            input=output
        )

        response_data = {
            "input": text,
            "output": output,
            "speech_url": speech_response["url"]
        }
        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error processing audio: {str(e)}")
        return jsonify({"error": "Failed to process audio"}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
