import { useRef, useState } from "react";
import RecordRTC from "recordrtc";
import axios from "axios";

function App() {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState(""); // Live transcript
  const [finalResponse, setFinalResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false); // Loading state
  const recorderRef = useRef(null);
  const recognitionRef = useRef(null);

  // API Base URL (update for deployment)
  const API_URL = "http://localhost:5000/record"; // Change if deployed

  // Format long responses
  const formatResponse = (text) => {
    return text.length > 500 ? text.substring(0, 500) + "..." : text;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new RecordRTC(stream, { type: "audio" });
      recorder.startRecording();
      recorderRef.current = recorder;
      setRecording(true);
      setError(null); // Clear previous errors

      // Initialize Web Speech API for real-time transcription
      const recognition = new window.webkitSpeechRecognition() || new window.SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";
      recognition.onresult = (event) => {
        const lastResult = event.results[event.results.length - 1];
        if (lastResult.isFinal) {
          setTranscript((prev) => prev + " " + lastResult[0].transcript);
        }
      };
      recognition.start();
      recognitionRef.current = recognition;
    } catch (err) {
      console.error("Error accessing microphone:", err);
      setError("Failed to access microphone. Please check permissions.");
    }
  };

  const stopRecording = async () => {
    if (!recorderRef.current) return;

    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    const recorder = recorderRef.current;
    recorder.stopRecording(async () => {
      const blob = recorder.getBlob();
      const formData = new FormData();
      formData.append("audio", blob, "recording.webm");

      setRecording(false);


      // ✅ Fix: Ensure `getTracks` only runs if recorder.stream exists
      if (recorder.stream) {
        const tracks = recorder.stream.getTracks();
        tracks.forEach(track => track.stop());
      }
      setLoading(true); // Start loading

      try {
        const res = await axios.post(API_URL, formData);
        setFinalResponse(res.data);

        // Handle empty response case
        if (!res.data || !res.data.input.trim()) {
          setError("No speech detected. Try speaking louder or closer to the mic.");
          setFinalResponse(null);
        }
      } catch (err) {
        console.error("Error sending audio:", err);
        let errorMsg = "Failed to process audio. Please try again.";
        if (err.response) {
          errorMsg = err.response.data.error || errorMsg;
        }
        setError(errorMsg);
      }

      setLoading(false); // Stop loading

      const tracks = recorder.stream.getTracks();
      tracks.forEach((track) => track.stop());
    });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-gray-800">Voice Assistant</h1>

      {error && <p className="mt-3 text-red-500">{error}</p>}

      <button
        onClick={recording ? stopRecording : startRecording}
        className="mt-6 px-6 py-3 text-white font-semibold rounded-lg shadow-md transition 
        bg-blue-600 hover:bg-blue-700 focus:ring focus:ring-blue-300"
      >
        {recording ? "Stop Recording" : "Start Recording"}
      </button>

      {loading && <p className="mt-4 text-blue-600">Processing audio...</p>}

      {recording && (
        <div className="mt-4 p-4 bg-white rounded-lg shadow-lg w-full max-w-lg">
          <h2 className="text-gray-600 font-medium">Live Transcript:</h2>
          <p className="text-gray-800">{transcript || "Listening..."}</p>
        </div>
      )}

      {finalResponse && (
        <div className="mt-6 p-4 bg-white rounded-lg shadow-lg w-full max-w-lg">
          <p className="text-gray-600"><strong>You:</strong> {finalResponse.input}</p>
          <p className="text-gray-800 font-medium"><strong>AI:</strong> {formatResponse(finalResponse.output)}</p>
          {finalResponse.speech_url && (
            <audio className="mt-4 w-full" controls src={finalResponse.speech_url} />
          )}
        </div>
      )}
    </div>
  );
}

export default App;
