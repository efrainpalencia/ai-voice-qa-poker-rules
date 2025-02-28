import openai
import os
import logging
import subprocess
from flask import Blueprint, request, jsonify, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

api = Blueprint("api", __name__)

limiter = Limiter(get_remote_address, app=api, default_limits=["5 per minute"])


@api.record
def record_setup(state):
    """Access RULEBOOKS and AUDIO_DIR from app.config."""
    global RULEBOOKS, AUDIO_DIR
    RULEBOOKS = state.app.config.get("RULEBOOKS")
    AUDIO_DIR = state.app.config.get("AUDIO_DIR")

    # Ensure audio directory exists
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR, exist_ok=True)
        logging.info(f"📂 Created audio directory: {AUDIO_DIR}")


@api.route("/record", methods=["POST"])
@limiter.limit("3 per minute")  # Limits users to 3 requests per minute
@api.route("/record", methods=["POST"])
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

        # **Generate AI Response**
        prompt = f"""
        You are a poker rules assistant who provides clear and concise answers
        found in the following rulebook: {rulebook_text}.
        (Note: When there is a raise on the table, if a player's amount to call the bet is less 
        than the previous raise, then that player does not have the option to re-raise.
        Therefore, that player may call or fold.) 

        - **Use Markdown-style formatting** for clarity and do not use emojis.
        - If you are asked a question that is not strictly related to the rulebook,
          kindly inform the user that you can only answer questions related to the rulebook.
        
        Please answer the user's question below:  
         📖 **User's Question**: "{text}"
        """

        openai_response = openai.chat.completions.create(
            model="ft:gpt-4o-2024-08-06:efrain-palencia::B22o3u69",
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


@api.route("/tts/<filename>", methods=["GET"])
def serve_tts_audio(filename):
    """Serve the generated TTS audio file."""
    audio_path = os.path.join(AUDIO_DIR, filename)

    if os.path.exists(audio_path):
        logging.info(f"✅ Serving TTS file: {audio_path}")
        return send_file(audio_path, mimetype="audio/mpeg")

    else:
        logging.error(f"❌ TTS file not found: {audio_path}")
        return jsonify({"error": "Audio file not found"}), 404
