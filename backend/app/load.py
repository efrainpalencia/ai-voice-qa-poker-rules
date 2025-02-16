import PyPDF2
import logging

logging.basicConfig(level=logging.INFO)


def load_rulebooks(file_paths):
    """Load multiple rulebooks into a dictionary."""
    rulebooks = {}
    for name, path in file_paths.items():
        try:
            with open(path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                rulebooks[name] = " ".join(
                    [page.extract_text()
                     for page in reader.pages if page.extract_text()]
                )
                logging.info(f"📖 {name} loaded successfully.")
        except Exception as e:
            logging.error(f"❌ Error loading {name}: {str(e)}")
    return rulebooks
