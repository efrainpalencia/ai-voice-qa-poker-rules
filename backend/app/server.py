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
        logging.error("❌ Missing OpenAI API key")
        return jsonify({"error": "Missing OpenAI API key"}), 500

    # Log request headers & files for debugging
    logging.info(
        f"📩 Received request: headers={dict(request.headers)}, files={request.files.keys()}")

    file = request.files.get("audio")  # Safely get file

    if not file:
        logging.error("❌ No audio file received")
        return jsonify({"error": "No audio file provided"}), 400

    logging.info(f"✅ Received file: {file.filename}")

    if file.filename == "":
        logging.error("❌ Empty file uploaded")
        return jsonify({"error": "Empty file uploaded"}), 400

    file_path = "recording.webm"

    try:
        file.save(file_path)
        logging.info("✅ Audio file saved successfully")

        # Transcribe using OpenAI Whisper API
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(
                model="whisper-1", file=audio_file)

        logging.info(f"📝 Transcription: {transcript}")

        text = transcript.get("text", "").strip()
        if not text:
            logging.error("❌ Transcription failed: Empty text")
            return jsonify({"error": "Transcription failed"}), 500

        # Get AI-generated response
        output = get_qa_chain().run(text)
        logging.info(f"🤖 AI Response: {output}")

        # Convert AI response to speech using OpenAI TTS
        speech_url = None
        try:
            speech_response = openai.Audio.create(
                model="tts-1",
                voice="alloy",
                input=output
            )
            speech_url = speech_response["url"]
            logging.info(f"🔊 TTS Generation successful: {speech_url}")
        except Exception as tts_error:
            logging.error(f"❌ TTS Generation failed: {tts_error}")

        response_data = {
            "input": text,
            "output": output,
            "speech_url": speech_url
        }
        return jsonify(response_data), 200

    except Exception as e:
        logging.error(f"❌ Error processing audio: {str(e)}")
        return jsonify({"error": "Failed to process audio"}), 500

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info("🗑️ Temporary audio file deleted")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
