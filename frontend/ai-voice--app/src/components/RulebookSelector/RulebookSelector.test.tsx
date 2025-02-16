import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import RulebookSelector from "./RulebookSelector";

describe("<RulebookSelector />", () => {
  test("it should mount", () => {
    render(
      <RulebookSelector
        selectedRulebook="poker_tda"
        setSelectedRulebook={() => {}}
      />
    );

    const rulebookSelector = screen.getByTestId("RulebookSelector");

    expect(rulebookSelector).toBeInTheDocument();
  });
});
