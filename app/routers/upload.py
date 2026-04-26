import os
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.services.extractor import extract_text_from_file
from app.utils.validators import validate_file
from app.utils.helpers import count_words
from app.config import settings

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles file upload, validation, and text extraction.
    Returns metadata and a preview of the text.
    """
    try:
        # Validate file format
        validate_file(file)
        
        # Check size limit (by reading the spool max)
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        # Extract text
        text, pages = await extract_text_from_file(file)
        
        if not text:
             raise HTTPException(status_code=400, detail="Could not extract any text from the file.")
             
        word_count = count_words(text)
        
        # Advanced Feature: Generate Keywords & Entities
        from app.services.extractive import extract_top_keywords, extract_entities
        keywords = extract_top_keywords(text)
        entities = extract_entities(text)

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": file_size,
            "pages": pages,
            "word_count": word_count,
            "keywords": keywords,  # Sent to frontend
            "entities": entities,  # Sent to frontend
            "text_preview": text[:500] + ("..." if len(text) > 500 else ""),
            # Send the full text back to the client to hold in memory until generation
            "full_text": text 
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
