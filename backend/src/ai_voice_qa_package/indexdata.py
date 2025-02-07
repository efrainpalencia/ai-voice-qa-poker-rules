from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from config import Config
from processdata import process_data

file_path = Config.FILE_PATH
pdf_data = process_data(file_path)


def index_poker_rules(pages, chunk_size=500, chunk_overlap=50):
    """
    Processes and indexes poker rules document into an embedded vector store (Chroma).

    Args:
        pages (List[dict]): List of extracted pages with 'content' and 'metadata'.
        chunk_size (int): Maximum size of each chunk (default: 500 characters).
        chunk_overlap (int): Overlap to preserve context (default: 50 characters).

    Returns:
        InMemoryVectorStore: The vector store containing indexed embeddings.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    indexed_docs = []
    for page in pages:
        content = page["content"]
        metadata = page["metadata"]

        # Extracting section and rule numbers from metadata
        rule_number = metadata.get("rule_number", "Unknown Rule")
        section = metadata.get("section", "Uncategorized")
        title = metadata.get("title", "Untitled Rule")

        # Splitting content into smaller chunks
        chunks = text_splitter.split_text(content)

        for chunk in chunks:
            indexed_docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "rule_number": rule_number,
                        "section": section,
                        "title": title
                    }
                )
            )

    # Indexing documents with OpenAI embeddings
    vector_store = InMemoryVectorStore.from_documents(
        indexed_docs, OpenAIEmbeddings())

    return vector_store


# Example Usage
# `pdf_data` is from `process_data()`
vector_store = index_poker_rules(pdf_data)

# Querying the vector store
query = "What is the official terminology in poker?"
docs = vector_store.similarity_search(query, k=2)
for doc in docs:
    print(
        f'Rule {doc.metadata["rule_number"]} - {doc.metadata["title"]}\nContent: {doc.page_content[:300]}\n')
