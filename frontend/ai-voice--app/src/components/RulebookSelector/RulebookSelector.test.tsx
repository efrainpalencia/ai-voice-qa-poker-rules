import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import RulebookSelector from './RulebookSelector';

describe('<RulebookSelector />', () => {
  test('it should mount', () => {
    render(<RulebookSelector />);

    const rulebookSelector = screen.getByTestId('RulebookSelector');

    expect(rulebookSelector).toBeInTheDocument();
  });
});