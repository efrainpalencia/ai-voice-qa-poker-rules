import openai
import os
import logging
import subprocess
import PyPDF2
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from config import Config

app = Flask(__name__)
CORS(app)

openai.api_key = Config.OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

# ✅ Ensure 'static/' Directory Exists
AUDIO_DIR = "audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# ✅ Load Multiple Rulebooks
RULEBOOKS = {}


def load_rulebook(name, path):
    """Loads a rulebook from a PDF file."""
    try:
        with open(path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            RULEBOOKS[name] = " ".join(
                [page.extract_text() for page in reader.pages if page.extract_text()])
            logging.info(f"📖 {name} loaded successfully.")
    except Exception as e:
        logging.error(f"❌ Error loading {name}: {str(e)}")


# 🔥 Load Rulebooks at Startup
load_rulebook("poker_tda", Config.TDA_FILE_PATH)
# Path to alternate rulebook
load_rulebook("poker_hwhr", Config.HWHR_FILE_PATH)


@app.route("/record", methods=["POST"])
def record():
    """Handles audio file upload, transcribes it, generates AI response, and returns TTS audio."""
    rulebook_key = request.form.get("rulebook", "poker_tda")
    rulebook_text = RULEBOOKS.get(rulebook_key, "")

    file = request.files.get("audio")
    file_path, wav_path = "recording.webm", "recording.wav"

    try:
        file.save(file_path)
        subprocess.run(["ffmpeg", "-i", file_path, "-ac", "1",
                        "-ar", "16000", wav_path, "-y"], check=True)

        with open(wav_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )

        text = transcript.text.strip()

        # 🎯 **Generate AI Response**
        prompt = f"""
        You are a poker rules assistant who provides clear, concise, and structured answers.
        Poker professionals have to make critical decisions that adhere to poker standards
        found in the following rulebook: {rulebook_text}.  
        
        💡 **Instructions**:
        Your job is to assist these professionals. At times you may be asked to directly 
        reference a rule. At times you may be given a scenario, in which case you may have to 
        use inference to find the solution.

        - **Use Markdown-style formatting** for clarity.  
        - **Respond in a structured format** using:
          - **Headings** for key concepts.  
          - **Bullet points** for lists.  
          - **Paragraphs** for explanations.  
        - **Examples and clarifications** where necessary.  
        - Keep answers **concise yet informative**.
        - approprate spacing and line height for improved readability.
        
        🎯 **Example Format**:
        
        ### 🃏 **Poker Rule Overview**
        - **Term**: Directional Play  
        - **Definition**: Directional play ensures actions follow the natural order of gameplay.  
        - **Example**: If Player A acts out of turn, their action may be binding depending on the scenario.
        
        🔔 **Important**: Only use the information from the rulebook.
        
        Please answer the user's question below:  
         📖 **User's Question**: "{text}"
        """

        openai_response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a poker rules assistant."},
                      {"role": "user", "content": prompt}]
        )
        ai_answer = openai_response.choices[0].message.content.strip()
        logging.info(f"🤖 AI Response: {ai_answer}")

        # 🔊 **Generate TTS Audio**
        speech_filename = "response.mp3"
        speech_path = os.path.join(AUDIO_DIR, speech_filename)

        try:
            tts_response = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=ai_answer
            )

            # ✅ Save the TTS audio file
            with open(speech_path, "wb") as audio_file:
                audio_file.write(tts_response.content)

            logging.info(f"🔊 TTS Audio saved: {speech_path}")

        except Exception as tts_error:
            logging.error(f"❌ TTS Generation failed: {tts_error}")
            speech_path = None

        # ✅ **Send the Correct Audio URL to Frontend**
        speech_url = f"/tts/{speech_filename}" if speech_path else None

        response_data = {
            "input": text,
            "output": ai_answer,
            "speech_url": speech_url
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
    audio_path = os.path.join(AUDIO_DIR, filename)

    if os.path.exists(audio_path):
        logging.info(f"✅ Serving TTS file: {audio_path}")
        return send_file(audio_path, mimetype="audio/mpeg")

    else:
        logging.error(f"❌ TTS file not found: {audio_path}")
        return jsonify({"error": "Audio file not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
