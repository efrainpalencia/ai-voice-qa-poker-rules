from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from app.processdata import process_data

# Load and process the poker rules document
file_path = "2024 Poker TDA Rules PDF Longform Vers 1.0 FINAL.pdf"
rules = process_data(file_path)


def index_poker_rules(rules, chunk_size=500, chunk_overlap=50):
    """
    Indexes poker rules into a vector store.

    Args:
        rules (list): List of extracted poker rules from the document.
        chunk_size (int): Maximum size of each text chunk (default: 500 characters).
        chunk_overlap (int): Overlap between chunks to preserve context (default: 50 characters).

    Returns:
        InMemoryVectorStore: The vector store containing indexed embeddings.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    indexed_docs = []
    for rule in rules:
        if "rule_number" not in rule or "title" not in rule:
            print(f"⚠️ Skipping rule due to missing data: {rule}")
            continue  # Skip rules missing necessary metadata

        rule_number = rule["rule_number"]
        title = rule["title"]
        content = rule["content"]
        examples = rule.get("examples", [])

        if not content.strip():
            print(f"Skipping rule {rule_number} due to missing content")
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

    # Indexing documents with OpenAI embeddings
    vector_store = InMemoryVectorStore.from_documents(
        indexed_docs, OpenAIEmbeddings()
    )

    return vector_store


# Create vector store for indexed poker rules
vector_store = index_poker_rules(rules)

# Example Querying
query = "What is the rule for action out of turn?"
docs = vector_store.similarity_search(query, k=2)

# Print results
for doc in docs:
    print(
        f'Rule {doc.metadata["rule_number"]} - {doc.metadata["title"]}\nContent: {doc.page_content[:300]}\n'
    )
