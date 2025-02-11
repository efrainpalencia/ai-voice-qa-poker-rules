from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from app.processdata import process_data
from app.config import Config

# Load and process the poker rules document
file_path = Config.FILE_PATH
rules = process_data(file_path)


def index_poker_rules(rules, chunk_size=1000, chunk_overlap=150):
    """
    Indexes poker rules into a vector store.

    Args:
        rules (list): List of extracted poker rules from the document.
        chunk_size (int): Maximum size of each text chunk (default: 700 characters).
        chunk_overlap (int): Overlap between chunks to preserve context (default: 100 characters).

    Returns:
        InMemoryVectorStore: The vector store containing indexed embeddings.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    indexed_docs = []
    for rule in rules:
        rule_number = rule.get("rule_number")
        title = rule.get("title")
        content = rule.get("content", "").strip()
        examples = rule.get("examples", [])

        # Skip invalid entries
        if not rule_number or not title or not content:
            print(f"⚠️ Skipping rule due to missing data: {rule}")
            continue

        # Split the main rule content into smaller chunks
        chunks = text_splitter.split_text(content)
        for chunk in chunks:
            indexed_docs.append(
                Document(
                    page_content=chunk,
                    metadata={"rule_number": rule_number, "title": title}
                )
            )

        # Index examples separately
        for example in examples:
            example_chunks = text_splitter.split_text(example)
            for chunk in example_chunks:
                indexed_docs.append(
                    Document(
                        page_content=chunk,
                        metadata={"rule_number": rule_number,
                                  "title": f"{title} - Example"}
                    )
                )

    # Ensure we have indexed documents before creating vector store
    if not indexed_docs:
        print("⚠️ No valid documents found to index. Vector store will be empty.")

    # Indexing documents with OpenAI embeddings
    vector_store = InMemoryVectorStore.from_documents(
        indexed_docs, OpenAIEmbeddings()
    )

    return vector_store


# Create vector store for indexed poker rules
vector_store = index_poker_rules(rules)

# Example Querying
query = "What is the rule for action out of turn?"
docs = vector_store.similarity_search(query, k=5)  # Retrieve top 5 results

# Print results
print("\n--- Query Results ---")
for i, doc in enumerate(docs, start=1):
    print(
        f"{i}. Rule {doc.metadata['rule_number']} - {doc.metadata['title']}\n"
        f"   Content Snippet: {doc.page_content[:300]}\n"
    )
