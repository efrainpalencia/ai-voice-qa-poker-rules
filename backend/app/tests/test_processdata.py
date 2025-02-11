import pytest
from langchain_community.document_loaders import PyPDFLoader
from app.processdata import extract_rules_from_text, process_data


@pytest.mark.parametrize("text, expected_output", [
    # Basic rule extraction
    (
        "1: Floor Decisions\nThe best interest of the game and fairness are top priorities...",
        [
            {
                "rule_number": "1",
                "title": "Floor Decisions",
                "content": "The best interest of the game and fairness are top priorities...",
                "examples": []
            }
        ]
    ),
    # Rule with sub-rules and examples
    (
        "53-A: Action Out of Turn (OOT)\nIf a player acts out of turn, action may be backed up...\n"
        "Example 1: Player bets out of turn...",
        [
            {
                "rule_number": "53-A",
                "title": "Action Out of Turn (OOT)",
                "content": "If a player acts out of turn, action may be backed up...",
                "examples": ["Example 1: Player bets out of turn..."]
            }
        ]
    ),
    # Multiple rules
    (
        "2: Player Responsibilities\nPlayers should verify registration data...\n"
        "3: Official Terminology\nUse clear terms like bet, raise, call.",
        [
            {
                "rule_number": "2",
                "title": "Player Responsibilities",
                "content": "Players should verify registration data...",
                "examples": []
            },
            {
                "rule_number": "3",
                "title": "Official Terminology",
                "content": "Use clear terms like bet, raise, call.",
                "examples": []
            }
        ]
    )
])
def test_extract_rules_from_text(text, expected_output):
    """Tests that extract_rules_from_text correctly identifies rules and content."""
    extracted_rules = extract_rules_from_text(text)
    assert extracted_rules == expected_output, f"Expected {expected_output} but got {extracted_rules}"


def test_process_data_with_mock(mocker):
    """Tests that process_data correctly loads a mock PDF and extracts rules."""
    mock_pages = [
        type("MockPage", (object,), {
            "page_content": "1: Floor Decisions\nThe best interest of the game and fairness are top priorities in decision-making. "
                            "Unusual circumstances occasionally dictate that common-sense decisions in the interest of fairness take "
                            "priority over technical rules. Floor decisions are final."
        })(),
        type("MockPage", (object,), {
            "page_content": "2: Player Responsibilities\nPlayers should verify registration data and seat assignments, "
                            "verify they’re dealt the correct number of cards before SA occurs, protect their hands, make their "
                            "intentions clear, follow the action, act in turn with proper terminology and gestures, defend their "
                            "right to act, keep cards visible and chips correctly stacked, remain at the table with a live hand, "
                            "table all cards properly when competing at showdown, speak up if they see a mistake, play in a timely "
                            "manner, call for a clock when warranted, transfer tables promptly, follow one player to a hand, "
                            "know and comply with the rules, practice proper etiquette, inform the house if they see or experience "
                            "discriminatory or offensive behavior, and generally contribute to an orderly event where all players "
                            "feel welcome."
        })(),
        type("MockPage", (object,), {
            "page_content": "3: Official Terminology and Gestures\nOfficial betting terms are simple, unmistakable, "
                            "time-honored declarations like bet, raise, call, fold, check, all-in, complete, and pot (pot-limit only). "
                            "Regional terms may also meet this test. Also, players must use gestures with caution when facing action; "
                            "tapping the table is a check. It is the responsibility of players to make their intentions clear: using "
                            "non-standard terms or gestures is at player’s risk and may result in a ruling other than what the player intended. "
                            "See also Rules 2 and 42."
        })()
    ]

    # ✅ Mock PyPDFLoader to bypass file reading
    mocker.patch.object(PyPDFLoader, "__init__", return_value=None)
    mocker.patch.object(PyPDFLoader, "load", return_value=mock_pages)

    processed_rules = process_data("mock.pdf")

    # ✅ Assertions to verify the output
    assert isinstance(
        processed_rules, list), "process_data should return a list"
    assert len(
        processed_rules) == 3, f"Expected 3 extracted rules, got {len(processed_rules)}"

    expected_rules = [
        {
            "rule_number": "1",
            "title": "Floor Decisions",
            "content": "The best interest of the game and fairness are top priorities in decision-making. "
                       "Unusual circumstances occasionally dictate that common-sense decisions in the interest of fairness take "
                       "priority over technical rules. Floor decisions are final.",
            "examples": []
        },
        {
            "rule_number": "2",
            "title": "Player Responsibilities",
            "content": "Players should verify registration data and seat assignments, verify they’re dealt the correct number of cards "
                       "before SA occurs, protect their hands, make their intentions clear, follow the action, act in turn with proper "
                       "terminology and gestures, defend their right to act, keep cards visible and chips correctly stacked, remain at the "
                       "table with a live hand, table all cards properly when competing at showdown, speak up if they see a mistake, play in a "
                       "timely manner, call for a clock when warranted, transfer tables promptly, follow one player to a hand, know and comply "
                       "with the rules, practice proper etiquette, inform the house if they see or experience discriminatory or offensive behavior, "
                       "and generally contribute to an orderly event where all players feel welcome.",
            "examples": []
        },
        {
            "rule_number": "3",
            "title": "Official Terminology and Gestures",
            "content": "Official betting terms are simple, unmistakable, time-honored declarations like bet, raise, call, fold, check, all-in, "
                       "complete, and pot (pot-limit only). Regional terms may also meet this test. Also, players must use gestures with caution when "
                       "facing action; tapping the table is a check. It is the responsibility of players to make their intentions clear: using "
                       "non-standard terms or gestures is at player’s risk and may result in a ruling other than what the player intended. "
                       "See also Rules 2 and 42.",
            "examples": []
        }
    ]

    for i, expected_rule in enumerate(expected_rules):
        assert processed_rules[i]["rule_number"] == expected_rule[
            "rule_number"], f"Rule number mismatch for rule {i+1}"
        assert processed_rules[i]["title"] == expected_rule[
            "title"], f"Title mismatch for rule {i+1}"
        assert processed_rules[i]["content"].startswith(
            expected_rule["content"][:50]), f"Content mismatch for rule {i+1}"
        assert processed_rules[i]["examples"] == expected_rule[
            "examples"], f"Examples mismatch for rule {i+1}"


def test_process_data_handles_empty_pdf(mocker):
    """Tests process_data handles an empty PDF gracefully."""
    mocker.patch("app.processdata.PyPDFLoader.load", return_value=[])

    processed_rules = process_data("empty.pdf")

    assert isinstance(
        processed_rules, list), "process_data should return a list"
    assert len(processed_rules) == 0, "Expected no extracted rules for empty PDF"


def test_process_data_handles_exceptions(mocker):
    """Tests process_data returns an empty list on an error."""
    mocker.patch("app.processdata.PyPDFLoader.load",
                 side_effect=Exception("File error"))

    processed_rules = process_data("invalid.pdf")

    assert processed_rules == [], "Expected an empty list on exception"
