import pytest
from unittest.mock import patch
from app.processdata import process_data
from app.indexdata import index_poker_rules

# ✅ Mock PDF Data to Simulate Extracted Rules
MOCK_PDF_DATA = [
    {
        "content": "1: Floor Decisions\nThe best interest of the game and fairness are top priorities...",
        "metadata": {"rule_number": "1", "section": "General Concepts", "title": "Floor Decisions"}
    },
    {
        "content": "2: Player Responsibilities\nPlayers should verify registration data and seat assignments...",
        "metadata": {"rule_number": "2", "section": "General Concepts", "title": "Player Responsibilities"}
    }
]

@pytest.fixture
def vector_store():
    """ Creates and returns a vector store for testing """
    return index_poker_rules(MOCK_PDF_DATA)

def test_query_retrieval(vector_store):
    """ Test that relevant rules are retrieved for a given query """
    query = "What is the role of the floor?"
    expected_rule = "Floor Decisions"

    docs = vector_store.similarity_search(query, k=1)
    assert len(docs) > 0, "No documents found for query"
    assert expected_rule in docs[0].metadata.get("title", ""), "Expected rule not found"

@patch("app.processdata.process_data", return_value=MOCK_PDF_DATA)
def test_process_data(mock_process):
    """ Mocks process_data to verify correct processing """
    extracted_data = process_data("test.pdf")

    assert isinstance(extracted_data, list), "process_data should return a list"
    assert len(extracted_data) == len(MOCK_PDF_DATA), "process_data output size mismatch"
    assert "content" in extracted_data[0], "Missing 'content' key in process_data output"
