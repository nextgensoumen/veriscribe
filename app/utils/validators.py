from fastapi import HTTPException, UploadFile, status
from app.config import settings

ALLOWED_MIME_TYPES = {
    "text/plain",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

def validate_file(file: UploadFile):
    """
    Validate an uploaded file based on its MIME type and size.
    Raises HTTPException if the file is invalid.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file format: {file.content_type}. Please upload PDF, DOCX, or TXT.",
        )

    # Note: File size limit validation in FastAPI is generally better done 
    # using middleware or reading in chunks to prevent large files from 
    # buffering into memory before validation. See `upload.py` for chunk-based check.
    return True
