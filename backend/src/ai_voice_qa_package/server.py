import openai
import os
from flask import Flask, render_template, request
from chains import get_qa_chain, get_chat_chain

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

server = Flask(__name__)


@server.route('/')
def landing():
    return render_template('index.html')


@server.route('/record', methods=['POST'])
def record():
    # Save uploaded audio file
    file = request.files['audio']
    file_path = "recording.webm"
    file.save(file_path)

    # Use OpenAI Whisper API for transcription
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",  # OpenAI's Whisper API model
            file=audio_file
        )

    text = transcript["text"]

    # Get AI-generated response
    output = get_qa_chain().run(text)

    # Use OpenAI TTS for speech output
    speech_response = openai.Audio.create(
        model="tts-1",
        voice="alloy",
        input=output
    )

    return {"input": text, "output": output, "speech_url": speech_response["url"]}
