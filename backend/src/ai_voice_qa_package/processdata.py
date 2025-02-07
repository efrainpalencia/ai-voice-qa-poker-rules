from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma


def process_data(file_path):
    """
    Loads a PDF file, extracts text content and metadata, 
    and returns structured data for storage in Chroma.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        List[dict]: A list of dictionaries with 'content' and 'metadata' keys.
    """
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        processed_pages = []
        for page in pages:
            processed_pages.append({
                "content": page.page_content,
                "metadata": page.metadata
            })

        # Debug output to verify extraction
        # print(f"Processed Pages: {processed_pages}")
        # print(f"Extracted Metadata from first 5 pages:\n")
        # for i in range(min(5, len(processed_pages))):  # Limit preview to first 5 pages
        #     print(f"Page {i + 1} Metadata: {processed_pages[i]['metadata']}")
        #     # Print first 200 characters
        #     print(
        #         f"Page {i + 1} Content Snippet: {processed_pages[i]['content'][:200]}\n")

        return processed_pages

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []
