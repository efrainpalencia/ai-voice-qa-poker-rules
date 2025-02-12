import openai
import os
import logging
import subprocess
import PyPDF2
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from config import Config

# Initialize Flask App
app = Flask(__name__)
CORS(app)

openai.api_key = Config.OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

# ✅ Ensure 'static/' Directory Exists
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

# 🔥 **Load Poker TDA Rules PDF at Startup**
PDF_PATH = Config.FILE_PATH
pdf_text = ""

try:
    with open(PDF_PATH, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        pdf_text = " ".join([page.extract_text()
                            for page in reader.pages if page.extract_text()])
        logging.info("📖 Poker TDA Rules PDF loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading PDF: {str(e)}")


@app.route("/record", methods=["POST"])
def record():
    """Handles audio file upload, converts, transcribes, and generates AI response with TTS."""
    if not openai.api_key:
        logging.error("❌ Missing OpenAI API key")
        return jsonify({"error": "Missing OpenAI API key"}), 500

    file = request.files.get("audio")
    if not file:
        logging.error("❌ No audio file received")
        return jsonify({"error": "No audio file provided"}), 400

    file_path = "recording.webm"
    wav_path = "recording.wav"

    try:
        file.save(file_path)
        logging.info("✅ Audio file saved successfully")

        # 🔄 Convert WebM to WAV
        subprocess.run(["ffmpeg", "-i", file_path, "-ac", "1",
                       "-ar", "16000", wav_path, "-y"], check=True)
        logging.info("🔄 Converted WebM to WAV")

        # 📝 **Transcribe the Audio**
        with open(wav_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )

        text = transcript.text.strip()
        logging.info(f"📝 Transcription: {text}")

        if not text:
            logging.error("❌ Transcription failed: Empty text")
            return jsonify({"error": "Transcription failed"}), 500

        # 🎯 **Step 2: Generate AI Response Using PDF Data**
        prompt = f"""
        You are a poker rules assistant. Professional poker supervisors will make decisions
        based on your recommendations. Answer the user's question based on the 2024 Poker TDA Rules.
        Be concise, accurate, and professional. If a specific rule applies, cite it directly.

        User's Question: "{text}"

        📖 **Relevant Poker Rules (from the Official TDA Rulebook):**
        "{pdf_text}"

        💡 Provide an answer based on the above rulebook. You may interpret the rule based on the question
        given to you.
        """
        openai_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a poker rules assistant. Use the provided rules strictly."},
                      {"role": "user", "content": prompt}]
        )
        ai_answer = openai_response.choices[0].message.content.strip()
        logging.info(f"🤖 AI Response: {ai_answer}")

        # 🔊 **Step 3: Generate TTS Audio**
        speech_filename = "response.mp3"
        speech_path = os.path.join(STATIC_DIR, speech_filename)

        try:
            tts_response = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=ai_answer
            )

            with open(speech_path, "wb") as audio_file:
                audio_file.write(tts_response.content)

            logging.info(f"🔊 TTS Audio saved: {speech_path}")

        except Exception as tts_error:
            logging.error(f"❌ TTS Generation failed: {tts_error}")
            speech_path = None

        response_data = {
            "input": text,
            "output": ai_answer,
            "speech_url": f"/tts/{speech_filename}" if speech_path else None
        }
        return jsonify(response_data), 200

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ FFmpeg conversion error: {str(e)}")
        return jsonify({"error": "Audio conversion failed"}), 500

    except Exception as e:
        logging.error(f"❌ Error processing audio: {str(e)}")
        return jsonify({"error": "Failed to process audio"}), 500

    finally:
        os.remove(file_path) if os.path.exists(file_path) else None
        os.remove(wav_path) if os.path.exists(wav_path) else None


# ✅ **Serve the TTS Audio File**
@app.route("/tts/<filename>", methods=["GET"])
def serve_tts_audio(filename):
    """Serve the generated TTS audio file."""
    audio_path = os.path.join(STATIC_DIR, filename)
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype="audio/mpeg")
    else:
        logging.error(f"❌ TTS file not found: {audio_path}")
        return jsonify({"error": "Audio file not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
