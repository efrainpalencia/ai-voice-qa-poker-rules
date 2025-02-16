import openai
import os
import logging
import subprocess
from flask import Blueprint, request, jsonify, send_file

api = Blueprint("api", __name__)


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
        You are a poker rules assistant who provides clear, concise, and structured answers.
        Poker professionals have to make critical decisions that adhere to poker standards
        found in the following rulebook: {rulebook_text}.  
        
        **Instructions**:
        Your job is to assist these professionals. At times you may be asked to directly 
        reference a rule. At times you may be given a scenario, in which case you may have to 
        use inference to find the solution. 
        
        If the rule does not exist, then you may respond with:
        That rule does not exist in this rulebook. You may ask to see a full list of the rules.

        If a scenario is given to you that is too complex, then you may respond with:
        Please break down the scenario into smaller questions. 

        If the question has no relevance to poker, then you may respond with:
        I'm sorry, I can only assist you with poker related content provided by the 
        selected rulebook.

        - **Use Markdown-style formatting** for clarity.  
        - **Respond in a structured format** using:
          - **Headings** for key concepts.  
          - **Bullet points** for lists.  
          - **Paragraphs** for explanations.  
        - **Examples and clarifications** where necessary.  
        - Keep answers **concise yet informative**.
        - approprate spacing and line height for improved readability.

        **Important**: Only use the information from the rulebook. Also, refrain from using emojis.
        
        **Example Format**:
        
        ### **Poker Rule Overview**
        - **Term**: Directional Play  
        - **Definition**: Directional play ensures actions follow the natural order of gameplay.  
        - **Example**: If Player A acts out of turn, their action may be binding depending on the scenario.
        
        
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
