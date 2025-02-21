import React from "react";

interface RulebookSelectorProps {
  selectedRulebook: string;
  setSelectedRulebook: (rulebook: string) => void;
}

const RulebookSelector: React.FC<RulebookSelectorProps> = ({
  selectedRulebook,
  setSelectedRulebook,
}) => {
  return (
    <div className="justify-items-center">
      <label
        htmlFor="rulebook"
        className="block text-lg text-gray-700 dark:text-white font-semibold mb-4 mt-8"
      >
        Select a Rulebook:
      </label>
      <select
        id="rulebook"
        className="p-2 mb-12 border rounded dark:bg-slate-600 dark:text-white"
        value={selectedRulebook}
        onChange={(e) => setSelectedRulebook(e.target.value)}
      >
        <option value="poker_tda">TDA Poker Rulebook</option>
        <option value="poker_hwhr" disabled={true}>
          Hollywood Hard Rock Poker Rulebook
        </option>
      </select>
      <div className="text-red-500 italic p-4">
        Hollywood Hard Rock Poker Rulebook temporarily unavailable
      </div>
    </div>
  );
};

export default RulebookSelector;
