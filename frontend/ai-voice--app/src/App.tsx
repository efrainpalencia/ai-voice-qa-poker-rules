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
    <div className="flex flex-col items-center justify-center w-full h-auto min-h-screen bg-gray-100 pb-0 pl-0 pr-0 pt-0 dark:bg-slate-800 dark:text-white px-4 overflow-x-hidden">
      {/* Hero Image */}
      <div className="w-full h-auto flex justify-center mb-4">
        <img
          src="/hero_img.png"
          alt="Poker Logo"
          className="w-full h-auto  rounded"
        />
      </div>

      {/* Rulebook Selector */}
      <RulebookSelector
        selectedRulebook={selectedRulebook}
        setSelectedRulebook={setSelectedRulebook}
      />

      {/* Instructions */}
      <div className="mt-6 p-4 w-full max-w-xl">
        {error ? (
          <p className="mt-3 text-red-500 text-center text-sm sm:text-base">
            {error}
          </p>
        ) : (
          <div className="mt-3 w-full max-w-xl text-sm sm:text-base">
            <p>
              You can ask about a specific rule by number, term, or category.
              Poker Rules Assistant will provide you with the definition along
              with an example. Ask for a list of the content if you are unsure
              of what to search for.
            </p>
            <br />
            <p>
              Try describing a scenario and Poker Rules Assistant will do its
              best to provide you with the proper ruling. It may help to include
              relevant information such as:
            </p>
            <br />
            <ol className="list-disc list-inside">
              <li>The poker game along with the stakes </li>
              <li>A detailed order of events</li>
              <li>The question to be answered</li>
            </ol>
            <br />
            <p>
              <strong className="mr-2">NOTE:</strong>
            </p>
            <span className="italic">
              Complex scenarios may need to be focused down into separate
              questions.
            </span>

            <br />
            <br />
            <p>
              To ask a question, simply press the "Start Recording" button
              below. Then, press the "Stop Recording" button after you are
              finished.
            </p>
          </div>
        )}
      </div>

      {/* Recording Controls (Centered) */}
      <div className="mt-4 w-full flex justify-center">
        <RecordingControls
          recording={recording}
          startRecording={startRecording}
          stopRecording={stopRecording}
        />
      </div>

      {/* Loading Spinner */}
      {loading && (
        <div className="mt-4">
          <Spinner />
        </div>
      )}

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
      <div className="mt-12 p-4 max-w-full bg-white box-lg shadow-lg w-full text-center dark:bg-slate-600 dark:text-white">
        <span>©2024 EFSOLVES</span>
      </div>
    </div>
  );
};

export default App;
