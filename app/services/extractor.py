import io
import fitz  # PyMuPDF
from docx import Document
from fastapi import UploadFile
from typing import Tuple
from app.utils.helpers import detect_encoding

async def extract_text_from_file(file: UploadFile) -> Tuple[str, int]:
    """
    Extracts text from the uploaded file asynchronously.
    Returns a tuple of (extracted_text, page_count).
    """
    # Read the file contents. For large files, doing this in-memory
    # requires enough RAM. Fast API limits UploadFile to keep memory usage safe.
    content = await file.read()
    text = ""
    pages = 1

    if file.content_type == "application/pdf":
        text, pages = _extract_from_pdf(content)
    elif file.content_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        text, pages = _extract_from_docx(content)
    elif file.content_type == "text/plain":
        text, pages = _extract_from_txt(content)
    else:
        # Fallback (validation should catch this before it happens)
        text, pages = _extract_from_txt(content)

    return text.strip(), pages

def _extract_from_pdf(content: bytes) -> Tuple[str, int]:
    doc = fitz.open(stream=content, filetype="pdf")
    text_blocks = []
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text_blocks.append(page.get_text("text"))
        
    page_count = doc.page_count
    doc.close()
    return "\n\n".join(text_blocks), page_count

def _extract_from_docx(content: bytes) -> Tuple[str, int]:
    doc = Document(io.BytesIO(content))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n\n".join(paragraphs), 1  # DOCX doesn't easily expose reliable page count

def _extract_from_txt(content: bytes) -> Tuple[str, int]:
    encoding = detect_encoding(content)
    try:
        text = content.decode(encoding)
    except UnicodeDecodeError:
        # Fallback if chardet was wrong
        text = content.decode("utf-8", errors="replace")
    return text, 1
