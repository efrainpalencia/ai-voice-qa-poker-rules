import pytest
from io import BytesIO
from flask.testing import FlaskClient


@pytest.fixture
def client():
    from app.server import app
    return app.test_client()


def test_record_success(client, mocker):
    """Test successful audio upload and AI response."""
    mock_transcription = {"text": "What are the poker rules?"}
    mock_response = "The poker rules require players to act in turn."

    # Mock OpenAI Whisper API
    mocker.patch("openai.Audio.transcribe", return_value=mock_transcription)

    # Mock AI response
    mock_qa_chain = mocker.patch("app.server.get_qa_chain")
    mock_qa_chain().run.return_value = mock_response

    # Mock OpenAI TTS response
    mock_tts_response = {"url": "https://test.speech.url"}
    mocker.patch("openai.Audio.create", return_value=mock_tts_response)

    # Simulate file upload with BytesIO
    data = {"audio": (BytesIO(b"fake_audio_data"), "test_audio.webm")}
    response = client.post("/record", data=data,
                           content_type="multipart/form-data")

    # Assertions
    assert response.status_code == 200, f"Unexpected response: {response.data.decode()}"
    json_data = response.get_json()
    assert json_data["input"] == mock_transcription["text"]
    assert json_data["output"] == mock_response
    assert json_data["speech_url"] == mock_tts_response["url"]
