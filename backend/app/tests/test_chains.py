import pytest
from unittest.mock import patch, MagicMock
from app.chains import get_chat_chain, get_qa_chain
from langchain.schema.runnable import RunnableBinding, RunnableParallel
from langchain.memory import ConversationBufferWindowMemory


@pytest.fixture
def mock_openai():
    """Mock OpenAI LLM response."""
    with patch("app.chains.OpenAI") as mock:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "Mock AI response"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_chroma():
    """Mock Chroma vector store."""
    with patch("app.chains.Chroma") as mock:
        mock_instance = MagicMock()
        mock_instance.as_retriever.return_value.invoke.return_value = "Mock QA Retrieval"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_chat_openai():
    """Mock ChatOpenAI model."""
    with patch("app.chains.ChatOpenAI") as mock:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = "Mock QA Model Response"
        mock.return_value = mock_instance
        yield mock_instance


def test_get_chat_chain(mock_openai):
    """Test that get_chat_chain() returns a valid RunnableBinding and mocked response."""
    chat_chain = get_chat_chain()

    # ✅ Ensure the return type is RunnableBinding
    assert isinstance(chat_chain, RunnableBinding)

    # ✅ Check if memory is correctly set
    assert "memory" in chat_chain.config
    assert isinstance(
        chat_chain.config["memory"], ConversationBufferWindowMemory)

    # ✅ Simulate a chat query (mocked)
    response = chat_chain.invoke(
        {"history": "", "human_input": "What are the poker rules?"})

    # ✅ Ensure mocked response is returned
    assert isinstance(response, str)
    assert response == "Mock AI response"

    print("\n🔍 Mocked Chat Chain Response:", response)


def test_get_qa_chain(mock_chroma, mock_chat_openai):
    """Test that get_qa_chain() returns a valid RunnableParallel instance with mocked responses."""
    qa_chain = get_qa_chain()

    # ✅ Ensure it is a RunnableParallel object
    assert isinstance(qa_chain, RunnableParallel)

    # ✅ Simulate a retrieval query
    response = qa_chain.invoke("What happens if a player acts out of turn?")

    # ✅ Ensure response is a dictionary with expected structure
    assert isinstance(response, dict)
    assert "model" in response
    assert "retriever" in response

    # ✅ Ensure mocked outputs are returned
    assert response["model"].invoke() == "Mock QA Model Response"
    assert response["retriever"].invoke() == "Mock QA Retrieval"

    print("\n🔍 Mocked Model Response:", response["model"].invoke())
    print("\n🔍 Mocked Retriever Response:", response["retriever"].invoke())
