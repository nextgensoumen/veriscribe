from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
import json

from app.services.summarizer import SummarizerService
from app.config import SUMMARIZATION_MODES
from app.services.extractive import extract_top_keywords, extract_entities

router = APIRouter()

class SummarizeRequest(BaseModel):
    text: str
    mode: str = "abstract"

class AnalyzeRequest(BaseModel):
    text: str

async def event_generator(summarizer: SummarizerService, text: str, mode: str) -> AsyncGenerator[str, None]:
    """Generates Server-Sent Events from the summarizer stream."""
    try:
        async for word in summarizer.stream_summary(text, mode):
            # The exact SSE format
            yield f"data: {json.dumps({'word': word})}\n\n"
        
        # Signal completion
        yield "event: complete\ndata: {}\n\n"
    except Exception as e:
        # Send error through stream
        yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"


@router.post("/summarize")
async def summarize(request: SummarizeRequest):
    """
    Endpoint that accepts text and mode, and returns a stream of words (SSE format).
    """
    if request.mode not in SUMMARIZATION_MODES:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Choose from {list(SUMMARIZATION_MODES.keys())}")
        
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="No text provided to summarize.")

    try:
        # Get the singleton summarizer service
        summarizer = SummarizerService()
        
        return StreamingResponse(
            event_generator(summarizer, request.text, request.mode),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Fast, synchronous endpoint returning Keywords and Entities without streaming.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="No text provided to analyze.")

    try:
        # Extract metadata
        keywords = extract_top_keywords(request.text, map_count=12)
        entities = extract_entities(request.text)
        
        return {
            "keywords": keywords,
            "entities": entities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
