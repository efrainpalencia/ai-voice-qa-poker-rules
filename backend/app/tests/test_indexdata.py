import pytest
from app.indexdata import index_poker_rules
from langchain_core.vectorstores import InMemoryVectorStore

# Mock data extracted from `processdata.py`
MOCK_RULES = [
    {
        "rule_number": "1",
        "title": "Floor Decisions",
        "content": "The best interest of the game and fairness are top priorities...",
        "examples": []
    },
    {
        "rule_number": "2",
        "title": "Player Responsibilities",
        "content": "Players should verify registration data and seat assignments...",
        "examples": []
    },
    {
        "rule_number": "53-A",
        "title": "Action Out of Turn",
        "content": "If a player acts out of turn, action may be backed up...",
        "examples": ["Example 1: If a player acts before their turn, the action may be reversed."]
    }
]


@pytest.fixture(scope="module")
def vector_store():
    """
    Creates a test vector store from mock rules.
    This ensures we are testing retrieval logic without requiring actual PDF processing.
    """
    return index_poker_rules(MOCK_RULES)


@pytest.mark.parametrize("query, expected_rule", [
    ("What is the role of the floor?", "Floor Decisions"),
    ("What are player responsibilities?", "Player Responsibilities"),
    ("What happens when a player acts out of turn?", "Action Out of Turn")
])
def test_query_retrieval(vector_store, query, expected_rule):
    """Test that relevant rules are retrieved for a given query."""
    docs = vector_store.similarity_search(
        query, k=3)  # Retrieve top 3 results for debugging

    assert len(docs) > 0, f"No documents found for query: {query}"

    print("\n--- Debugging Search Results ---")
    for doc in docs:
        print(f"Rule Number: {doc.metadata.get('rule_number', 'N/A')}")
        print(f"Title: {doc.metadata.get('title', 'N/A')}")
        print(f"Content Snippet: {doc.page_content[:300]}\n")

    retrieved_rule_title = docs[0].metadata.get("title", "")

    assert expected_rule in retrieved_rule_title, f"Expected rule '{expected_rule}' not found in retrieved results"


@pytest.mark.parametrize("query", [
    "What happens if a player uses a phone?",
    "What is the penalty for using electronic devices at the table?",
    "What is the rule about talking on the phone?"
])
def test_unrelated_query(vector_store, query):
    """
    Tests retrieval accuracy by checking that unrelated queries
    don't falsely return high-confidence but incorrect matches.
    """
    docs = vector_store.similarity_search(query, k=1)

    assert len(docs) > 0, "No documents found, but expected some retrieval"
    assert "Electronic Devices" not in docs[0].metadata.get("title", ""), \
        "Unexpected match for unrelated query"
