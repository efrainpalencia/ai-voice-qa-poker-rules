import pytest
from ai_voice_qa_package.processdata import process_data
from ai_voice_qa_package.indexdata import index_poker_rules

# Mock PDF Data
mock_pdf_data = [
    {
        "content": "1: Floor Decisions\nThe best interest of the game and fairness are top priorities...",
        "metadata": {"rule_number": "1", "section": "General Concepts", "title": "Floor Decisions"}
    },
    {
        "content": "2: Player Responsibilities\nPlayers should verify registration data and seat assignments...",
        "metadata": {"rule_number": "2", "section": "General Concepts", "title": "Player Responsibilities"}
    }
]

# ✅ FIX: Properly Define the `vector_store` Fixture at the Top


@pytest.fixture(scope="module")
def vector_store():
    """ Creates and returns a vector store for testing """
    return index_poker_rules(mock_pdf_data)


@pytest.mark.parametrize("query, expected_rule", [
    ("What is the role of the floor?", "Floor Decisions"),
    ("What are player responsibilities?", "Player Responsibilities")
])
def test_query_retrieval(vector_store, query, expected_rule):
    """ Test that relevant rules are retrieved for a given query """
    docs = vector_store.similarity_search(query, k=1)
    assert len(docs) > 0, "No documents found for query"
    assert expected_rule in docs[0].metadata["title"]
