import { useRef, useState } from "react";
import RecordRTC from "recordrtc";
import axios from "axios";

function App() {
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [finalResponse, setFinalResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedRulebook, setSelectedRulebook] = useState("poker_tda");
  const [audioKey, setAudioKey] = useState(0); // Force re-render audio
  const recorderRef = useRef(null);
  const recognitionRef = useRef(null);
  const audioRef = useRef(null);

  const API_URL = "http://localhost:5000/record";

  const resetState = () => {
    setTranscript("");
    setFinalResponse(null);
    setAudioKey((prev) => prev + 1);
    if (audioRef.current) {
      audioRef.current.src = "";
      audioRef.current.load();
    }
  };

  const startRecording = async () => {
    resetState();

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
      formData.append("rulebook", selectedRulebook);

      setRecording(false);
      setLoading(true);

      try {
        const res = await axios.post(API_URL, formData);
        setFinalResponse(res.data);

        if (res.data.speech_url) {
          console.log("✅ New Speech URL:", res.data.speech_url);

          setTimeout(() => {
            if (audioRef.current) {
              // ✅ Reset audio element and ensure proper playback
              audioRef.current.src = `http://localhost:5000${res.data.speech_url}?t=${Date.now()}`;
              audioRef.current.load();

              // ✅ Wait until audio is ready before playing
              audioRef.current.oncanplaythrough = () => {
                audioRef.current.play().catch((err) =>
                  console.error("🔊 Playback failed:", err)
                );
              };
            } else {
              console.warn("⚠️ Audio player not found.");
            }
          }, 500);
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
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6 dark:bg-slate-800 dark:text-white">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Poker Rules Assistant</h1>

      {/* Dropdown to Select Rulebook */}
      <select
        className="mt-4 p-2 border rounded dark:bg-slate-600 dark:text-white"
        value={selectedRulebook}
        onChange={(e) => setSelectedRulebook(e.target.value)}
      >
        <option value="poker_tda">TDA Poker Rulebook</option>
        <option value="poker_hwhr">HWHR Poker Rulebook</option>
      </select>

      {error && <p className="mt-3 text-red-500">{error}</p>}

      <button
        onClick={recording ? stopRecording : startRecording}
        className={`mt-6 px-6 py-3 text-white font-semibold rounded-lg shadow-md transition 
        ${recording ? "bg-red-600 hover:bg-red-700 focus:ring-red-300" : "bg-blue-600 hover:bg-blue-700 focus:ring-blue-300"}`}
      >
        {recording ? "Stop Recording" : "Start Recording"}
      </button>

      {loading && <p className="mt-4 text-blue-600 dark:bg-slate-800 dark:text-white">Processing audio...</p>}

      {transcript && (
        <div className="mt-4 p-4 bg-white rounded-lg shadow-lg w-full max-w-lg dark:bg-slate-600 dark:text-white">
          <h2 className="text-gray-600 font-medium dark:text-white">Live Transcript:</h2>
          <p className="text-gray-800 dark:text-white">{transcript || "Listening..."}</p>
        </div>
      )}

      {finalResponse && (
        <div className="mt-6 p-4 bg-white rounded-lg shadow-lg w-full max-w-lg dark:bg-slate-600 dark:text-white">
          <p className="text-gray-600 dark:text-white"><strong>You:</strong> {finalResponse.input}</p>
          <p className="text-gray-800 font-medium dark:text-white"><strong>AI:</strong> {finalResponse.output}</p>
          <audio ref={audioRef} key={audioKey} className="mt-4 w-full" controls />
        </div>
      )}
    </div>
  );
}

export default App;
