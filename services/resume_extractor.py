import re

def clean_resume_text(text: str) -> str:
    # Remove extra whitespace and newlines
    text = text.strip()
    text = re.sub(r'\n+', '\n', text)
    return text
