import re
from langchain_community.document_loaders import PyPDFLoader
from app.config import Config


def extract_rules_from_text(text):
    """
    Extracts rules from the raw text using regex, capturing rule numbers, titles, and content.
    Handles sub-rules like 53-A, 53-B, and examples.
    """
    rule_pattern = re.compile(
        r'(?P<rule_number>\d{1,2}(-[A-Z])?): (?P<title>.*?)\n(?P<content>.*?)(?=\n\d{1,2}(-[A-Z])?:|$)',
        re.DOTALL
    )
    rules = []

    for match in rule_pattern.finditer(text):
        rule_number = match.group("rule_number").strip()
        title = match.group("title").strip()
        content = match.group("content").strip()

        # Identify and separate examples
        example_pattern = re.compile(
            r'(Example \d+: .*?)(?=\nExample \d+:|\Z)', re.DOTALL)
        examples = [ex.group(1).strip()
                    for ex in example_pattern.finditer(content)]

        # Remove examples from content
        for ex in examples:
            content = content.replace(ex, "").strip()

        if not content or len(content) < 20:  # Ensure valid content
            continue

        rules.append({
            "rule_number": rule_number,
            "title": title,
            "content": content,
            "examples": examples
        })

    return rules


def process_data(file_path):
    """
    Loads the PDF, extracts structured rule data, and returns a list of rules.
    """
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        full_text = "\n".join([page.page_content for page in pages])
        structured_rules = extract_rules_from_text(full_text)

        return structured_rules  # Ensure this returns a list of dicts with 'rule_number'

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []


# Debugging
# file_path = Config.FILE_PATH
# rules = process_data(file_path)
# for rule in rules[:5]:  # Print first 5 rules to verify structure
#     print(rule)
# print(f"Total extracted rules: {len(rules)}")
