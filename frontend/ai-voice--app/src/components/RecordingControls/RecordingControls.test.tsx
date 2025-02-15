import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import RecordingControls from './RecordingControls';

describe('<RecordingControls />', () => {
  test('it should mount', () => {
    render(<RecordingControls />);

    const recordingControls = screen.getByTestId('RecordingControls');

    expect(recordingControls).toBeInTheDocument();
  });
});