import re

def clean_job_text(text: str) -> str:
    """
    Cleans raw job description text by removing common boilerplate,
    special characters, and normalizing whitespace.
    """
    text = text.lower()
    
    # Remove common URL patterns
    text = re.sub(r'http\S+', '', text)
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
