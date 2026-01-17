import os
import base64
import PyPDF2
import docx
import requests

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

def is_image(file_path: str) -> bool:
    return os.path.splitext(file_path)[1].lower() in IMAGE_EXTENSIONS

def image_to_base64(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def extract_file_text(file_path: str) -> str | None:
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".txt":
            return open(file_path, "r", encoding="utf-8").read()

        if ext == ".pdf":
            text = ""
            reader = PyPDF2.PdfReader(open(file_path, "rb"))
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        if ext == ".docx":
            doc = docx.Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs)

    except Exception as e:
        return f"Error reading file: {e}"

    return None






