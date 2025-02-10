import pytest
from unittest.mock import patch, MagicMock
from app.server import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.testing = True
    return app.test_client()


def test_record_endpoint_no_audio(client):
    """Test if the record endpoint returns an error when no audio file is provided."""
    response = client.post("/record", data={})
    assert response.status_code == 400
    assert response.json["error"] == "No audio file provided"


@patch("app.server.openai.Audio.transcribe", return_value={"text": "Test input"})
@patch("app.server.get_qa_chain")
@patch("app.server.openai.Audio.create", return_value={"url": "mock_speech_url"})
def test_record_endpoint_success(mock_tts, mock_qa_chain, mock_transcribe, client):
    """Test successful processing of an audio file."""
    mock_qa_chain.return_value.run.return_value = "Mock AI response"

    data = {
        "audio": ("fake_audio_data".encode(), "recording.webm"),
    }
    response = client.post("/record", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert response.json["input"] == "Test input"
    assert response.json["output"] == "Mock AI response"
    assert response.json["speech_url"] == "mock_speech_url"


@patch("app.server.openai.Audio.transcribe", return_value={"text": ""})
def test_record_transcription_failure(mock_transcribe, client):
    """Test if the endpoint handles transcription failure correctly."""
    data = {
        "audio": ("fake_audio_data".encode(), "recording.webm"),
    }
    response = client.post("/record", data=data, content_type="multipart/form-data")

    assert response.status_code == 500
    assert response.json["error"] == "Transcription failed"


@patch("app.server.get_qa_chain", side_effect=Exception("AI error"))
@patch("app.server.openai.Audio.transcribe", return_value={"text": "Test input"})
def test_record_chat_api_failure(mock_transcribe, mock_qa_chain, client):
    """Test handling when AI response generation fails."""
    data = {
        "audio": ("fake_audio_data".encode(), "recording.webm"),
    }
    response = client.post("/record", data=data, content_type="multipart/form-data")

    assert response.status_code == 500
    assert "Failed to process audio" in response.json["error"]
