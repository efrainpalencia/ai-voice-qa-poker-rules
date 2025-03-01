import { useRef, useState } from "react";
import RecordRTC from "recordrtc";
import axios from "axios";
import Spinner from "./components/Spinner/Spinner";
import RulebookSelector from "./components/RulebookSelector/RulebookSelector";
import RecordingControls from "./components/RecordingControls/RecordingControls";
import { resetAudioState, handleAudioPlayback } from "./utils/audioUtils";
import ReactMarkdown from "react-markdown";

const App: React.FC = () => {
  const [recording, setRecording] = useState(false);
  const [finalResponse, setFinalResponse] = useState<{
    input: string;
    output: string;
    speech_url?: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedRulebook, setSelectedRulebook] = useState("poker_tda");

  const recorderRef = useRef<RecordRTC | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null!);

  const BASE_API_URL = import.meta.env.VITE_BASE_API_URL;
  const API_URL = import.meta.env.VITE_API_URL;

  const startRecording = async () => {
    resetAudioState(setFinalResponse, audioRef);
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
        setFinalResponse(res.data);

        if (res.data.speech_url) {
          handleAudioPlayback(audioRef, res.data.speech_url, BASE_API_URL);
        } else {
          setError("Failed to retrieve audio response.");
        }
      } catch (err) {
        setError("Failed to process audio. Please try again.");
      }

      setLoading(false);
    });
  };

  return (
    <div className="flex flex-col items-center justify-center w-full h-auto min-h-screen px-0 bg-gray-100 pb-0 dark:bg-slate-800 dark:text-white overflow-x-hidden">
      {/* Hero Image */}
      <div className="w-full h-auto flex justify-center mb-4">
        <img
          src="/ai-poker-hero-img.png"
          alt="Poker Logo"
          className="w-full h-auto rounded"
        />
      </div>

      {/* Instructions */}
      <div className="mt-6 p-4 w-full max-w-xl">
        {error ? (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
            <strong>Error:</strong> {error}
          </div>
        ) : (
          <div className="mt-3 w-full max-w-xl text-sm sm:text-base">
            <p>
              <strong className="text-yellow-300 text-lg">
                Are you unsure about a poker rule or procedure?
              </strong>
            </p>
            <p>
              <br />
              Pocket Poker Pal will provide you with the answer directly from
              the selected rulebook.
            </p>
            <br />
            <p>
              All you have to do is ask a question or describe a scenario and
              Pocket Poker Pal will provide you with the appropriate rule
              definition along with how it applies to your scenario. It may help
              to include relevant information such as:
            </p>
            <br />
            <ul className="list-disc list-inside">
              <li>The poker game along with the stakes if applicable</li>
              <li>A detailed order of events</li>
              <li>The question to be answered</li>
            </ul>
            <br />
            <p className="italic">
              (e.g.) Can you show me a list of the content in this rulebook?
            </p>
            <br />
            <p>
              <strong className="text-yellow-300 text-lg">
                To get started:
              </strong>
            </p>
            <br />
            <ol className="list-decimal list-inside">
              <li>Press "Star Recording"</li>
              <li>Ask a question</li>
              <li>Press "Stop Recording"</li>
            </ol>
          </div>
        )}
      </div>
      {/* Rulebook Selector */}
      <RulebookSelector
        selectedRulebook={selectedRulebook}
        setSelectedRulebook={setSelectedRulebook}
      />

      {/* Recording Controls */}
      <div className="mt-10 w-full flex justify-center">
        <RecordingControls
          recording={recording}
          startRecording={startRecording}
          stopRecording={stopRecording}
        />
      </div>

      {/* Loading Spinner */}
      {loading && <Spinner />}

      {/* Display Response */}
      {finalResponse && (
        <div className="mt-6 p-4 bg-white rounded-lg shadow-lg w-full max-w-xl dark:bg-slate-600 dark:text-white">
          <p className="text-gray-700 dark:text-white text-sm sm:text-base mb-2">
            <strong>You:</strong> {finalResponse.input}
          </p>
          <div className="text-gray-800 font-medium dark:text-white prose dark:prose-invert text-sm sm:text-base">
            <ReactMarkdown>{finalResponse.output}</ReactMarkdown>
          </div>
          {finalResponse.speech_url && (
            <audio
              ref={audioRef}
              className="mt-4 w-full"
              src={`${BASE_API_URL}${finalResponse.speech_url}?t=${Date.now()}`}
              controls
              autoPlay
            />
          )}
        </div>
      )}

      <div className="mt-12 max-w-full bg-white box-lg shadow-lg w-full text-center dark:bg-teal-800 dark:text-white">
        <span>©2025 EFAITECH SOLUTIONS</span>
      </div>
    </div>
  );
};

export default App;
