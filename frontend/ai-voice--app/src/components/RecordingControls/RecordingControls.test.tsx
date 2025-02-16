import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import RecordingControls from "./RecordingControls";

describe("<RecordingControls />", () => {
  test("it should mount", () => {
    render(
      <RecordingControls
        recording={false}
        startRecording={() => {}}
        stopRecording={() => {}}
      />
    );

    const recordingControls = screen.getByTestId("RecordingControls");

    expect(recordingControls).toBeInTheDocument();
  });
});
