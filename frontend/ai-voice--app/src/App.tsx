import { useRef, useState } from "react";
import RecordRTC from "recordrtc";
import axios from "axios";
import Spinner from "./components/Spinner/Spinner";
import RulebookSelector from "./components/RulebookSelector/RulebookSelector";
import RecordingControls from "./components/RecordingControls/RecordingControls";
import { resetAudioState, handleAudioPlayback } from "./utils/audioUtils";

const App: React.FC = () => {
  const [recording, setRecording] = useState(false);
  const [finalResponse, setFinalResponse] = useState<{
    input: string;
    output: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedRulebook, setSelectedRulebook] = useState("poker_tda");
  const [audioKey, setAudioKey] = useState(0);
  const recorderRef = useRef<RecordRTC | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const BASE_API_URL = import.meta.env.VITE_BASE_API_URL;
  const API_URL = import.meta.env.VITE_API_URL;

  console.log("✅ BASE_API_URL:", import.meta.env.VITE_BASE_API_URL);
  console.log("✅ API_URL:", import.meta.env.VITE_API_URL);

  const startRecording = async () => {
    resetAudioState(setFinalResponse, setAudioKey, audioRef);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new RecordRTC(stream, { type: "audio" });
      recorder.startRecording();
      recorderRef.current = recorder;
      setRecording(true);
      setError(null);

      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        setError(
          "Speech recognition is not supported in this browser. Please use Chrome."
        );
        return;
      }

      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";
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
        console.log("🔍 API Response:", res.data);
        setFinalResponse(res.data);

        if (res.data.speech_url) {
          handleAudioPlayback(audioRef, res.data.speech_url, BASE_API_URL);
        } else {
          console.warn("⚠️ No valid `speech_url` received.");
          setError("Failed to retrieve audio response.");
        }
      } catch (err) {
        console.error("❌ Error sending audio:", err);
        setError("Failed to process audio. Please try again.");
      }

      setLoading(false);
    });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6 dark:bg-slate-800 dark:text-white">
      <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
        Poker Rules Assistant
      </h1>

      <RulebookSelector
        selectedRulebook={selectedRulebook}
        setSelectedRulebook={setSelectedRulebook}
      />

      {error && <p className="mt-3 text-red-500">{error}</p>}

      <RecordingControls
        recording={recording}
        startRecording={startRecording}
        stopRecording={stopRecording}
      />

      {loading && <Spinner />}

      {finalResponse && (
        <div className="mt-6 p-4 bg-white rounded-lg shadow-lg w-full max-w-lg dark:bg-slate-600 dark:text-white">
          <p className="text-gray-600 dark:text-white">
            <strong>You:</strong> {finalResponse.input}
          </p>
          <p className="text-gray-800 font-medium dark:text-white">
            <strong>AI:</strong> {finalResponse.output}
          </p>
          <audio
            ref={audioRef}
            className="mt-4 w-full"
            src={`${BASE_API_URL}${finalResponse.speech_url}?t=${Date.now()}`}
            controls
            autoPlay
          />
        </div>
      )}
    </div>
  );
};

export default App;
