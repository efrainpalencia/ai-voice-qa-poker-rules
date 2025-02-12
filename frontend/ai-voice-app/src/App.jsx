import { useRef, useState } from "react";
import RecordRTC from "recordrtc";
import axios from "axios";

function App() {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [finalResponse, setFinalResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [speechUrl, setSpeechUrl] = useState(""); // State for audio URL
  const recorderRef = useRef(null);
  const recognitionRef = useRef(null);
  const audioRef = useRef(null);

  const API_URL = "http://localhost:5000/record"; // Update if deployed
  const TTS_BASE_URL = "http://localhost:5000"; // Ensure full path

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new RecordRTC(stream, { type: "audio" });
      recorder.startRecording();
      recorderRef.current = recorder;
      setRecording(true);
      setError(null);

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
      setLoading(true);

      // ✅ Ensure `getTracks` only runs if stream exists
      if (recorder.stream) {
        const tracks = recorder.stream.getTracks();
        tracks.forEach(track => track.stop());
      }

      try {
        const res = await axios.post(API_URL, formData);
        setFinalResponse(res.data);

        if (res.data.speech_url) {
          const fullSpeechURL = `${TTS_BASE_URL}${res.data.speech_url}`;
          console.log("✅ Speech URL:", fullSpeechURL);

          setSpeechUrl(fullSpeechURL); // ✅ Update speech state

          setTimeout(() => {
            if (audioRef.current) {
              audioRef.current.src = fullSpeechURL;
              audioRef.current.load();
              audioRef.current.play()
                .then(() => console.log("🔊 Audio playing successfully"))
                .catch((err) => {
                  console.warn("⚠️ Audio play error:", err);
                  setError("Failed to play audio. Please check your browser settings.");
                });
            }
          }, 1000); // Slight delay to ensure UI updates
        } else {
          console.warn("⚠️ No speech URL received.");
        }

      } catch (err) {
        console.error("Error sending audio:", err);
        setError("Failed to process audio. Please try again.");
      }

      setLoading(false);
    });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-gray-800">TDA Poker Rules Assistant</h1>

      {error && <p className="mt-3 text-red-500">{error}</p>}

      <button
        onClick={recording ? stopRecording : startRecording}
        className="mt-6 px-6 py-3 text-white font-semibold rounded-lg shadow-md transition 
        bg-blue-600 hover:bg-blue-700 focus:ring focus:ring-blue-300"
      >
        {recording ? "Stop Recording" : "Start Recording"}
      </button>

      {loading && <p className="mt-4 text-blue-600">Processing audio...</p>}

      {finalResponse && (
        <div className="mt-6 p-4 bg-white rounded-lg shadow-lg w-full max-w-lg">
          <p className="text-gray-600"><strong>You:</strong> {finalResponse.input}</p>
          <p className="text-gray-800 font-medium"><strong>AI:</strong> {finalResponse.output}</p>

          {/* ✅ Ensure audio player is properly displayed */}
          {speechUrl && (
            <audio ref={audioRef} className="mt-4 w-full" controls>
              <source src={speechUrl} type="audio/mpeg" />
              Your browser does not support the audio element.
            </audio>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
