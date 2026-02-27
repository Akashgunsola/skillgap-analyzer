import pdfplumber
from pathlib import Path

def parse_resume(file_path: str) -> str:
    path = Path(file_path)

    if path.suffix.lower() == ".pdf":
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

    elif path.suffix.lower() in [".txt"]:
        return path.read_text(encoding="utf-8")

    else:
        raise ValueError("Unsupported resume format")
