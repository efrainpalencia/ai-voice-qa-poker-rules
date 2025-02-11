import openai
import os
import logging
import subprocess
import PyPDF2
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config

# 🔥 Initialize Flask App
app = Flask(__name__)
CORS(app)

# ✅ Set OpenAI API Key
openai.api_key = Config.OPENAI_API_KEY

# 🔍 Configure Logging
logging.basicConfig(level=logging.INFO)

# 📖 Load Poker TDA Rules PDF at Startup
PDF_PATH = Config.FILE_PATH
pdf_text = ""

try:
    with open(PDF_PATH, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        pdf_text = " ".join(
            [page.extract_text() for page in reader.pages if page.extract_text()]
        )
        logging.info("📖 Poker TDA Rules PDF loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading PDF: {str(e)}")


@app.route("/record", methods=["POST"])
def record():
    """Handles audio file upload, converts, transcribes, and generates AI response."""

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
        # 🔥 Save the uploaded audio file
        file.save(file_path)
        logging.info("✅ Audio file saved successfully")

        # 🎙️ Convert WebM to WAV
        subprocess.run(
            ["ffmpeg", "-i", file_path, "-ac", "1",
                "-ar", "16000", wav_path, "-y"],
            check=True,
        )
        logging.info("🔄 Converted WebM to WAV")

        # 📝 Transcribe using OpenAI Whisper API
        with open(wav_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )

        text = transcript.text.strip()
        if not text:
            logging.error("❌ Transcription failed: Empty text")
            return jsonify({"error": "Transcription failed"}), 500

        logging.info(f"📝 Transcription: {text}")

        # 🎯 Ask OpenAI, using both the question and PDF context
        prompt = f"""
        You are an expert in poker tournament rules, specifically the 2024 Poker TDA Rules.
        You will answer questions based **only** on the official TDA rulebook.

        🃏 **User's Question**: "{text}"
        
        📖 **Relevant Poker Rules (from the PDF)**:
        "{pdf_text[:4000]}"  # Sending only a chunk to fit OpenAI's context limit.

        🎯 **Provide a clear, rule-based answer using only official TDA rules**.
        """

        openai_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a poker rules assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        ai_answer = openai_response.choices[0].message.content.strip()
        logging.info(f"🤖 AI Response: {ai_answer}")

        response_data = {"input": text, "output": ai_answer}
        return jsonify(response_data), 200

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ FFmpeg conversion error: {str(e)}")
        return jsonify({"error": "Audio conversion failed"}), 500

    except Exception as e:
        logging.error(f"❌ Error processing audio: {str(e)}")
        return jsonify({"error": "Failed to process audio"}), 500

    finally:
        # 🔥 Safe file cleanup
        for file in [file_path, wav_path]:
            if os.path.exists(file):
                os.remove(file)
                logging.info(f"🗑️ Deleted temporary file: {file}")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
