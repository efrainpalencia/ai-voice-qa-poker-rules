import React from "react";

interface RecordingControlsProps {
  recording: boolean;
  startRecording: () => void;
  stopRecording: () => void;
}

const RecordingControls: React.FC<RecordingControlsProps> = ({
  recording,
  startRecording,
  stopRecording,
}) => {
  return (
    <button
      onClick={recording ? stopRecording : startRecording}
      className={`mt-6 px-6 py-3 text-slate-600 font-semibold rounded-lg shadow-md transition 
        ${
          recording
            ? "bg-red-600 hover:bg-red-700 focus:ring-red-300"
            : "bg-yellow-300 hover:bg-yellow-400 focus:ring-yellow-200"
        }`}
    >
      {recording ? "Stop Recording" : "Start Recording"}
    </button>
  );
};

export default RecordingControls;
