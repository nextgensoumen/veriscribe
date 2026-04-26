import re
import unicodedata
from app.config import settings

def clean_text(text: str) -> str:
    """
    Normalizes encoding, removes redundant whitespace, and cleans up noise.
    """
    if not text:
        return ""
        
    # Unicode normalize
    text = unicodedata.normalize('NFKD', text)
    
    # Remove multiple instances of hyphens or underscores (e.g., page separators)
    text = re.sub(r'[-_]{3,}', ' ', text)
    
    # Remove citation markers like [1], [1, 2]
    text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
    
    # Collapse multiple newlines to max 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

from nltk.tokenize import sent_tokenize

def chunk_text(text: str, tokenizer) -> list[str]:
    """
    Splits text into chunks strictly based on the model's tokenizer.
    Uses map-reduce strategy for inputs larger than max model bounds.
    """
    cleaned_text = clean_text(text)
    
    # Estimate token count. Using the model's precise tokenizer.
    tokens = tokenizer.encode(cleaned_text, add_special_tokens=False)
    
    max_tokens = settings.CHUNK_SIZE_TOKENS
    overlap = settings.CHUNK_OVERLAP_TOKENS
    
    # If the text fits in a single chunk, return it as one element
    if len(tokens) <= max_tokens:
        return [cleaned_text]
        
    chunks = []
    start = 0
    while start < len(tokens):
        # Determine the end token index for this chunk
        end = min(start + max_tokens, len(tokens))
        
        # Decode these tokens back into text
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)
        
        # Move the start forward by (max_tokens - overlap)
        if end == len(tokens):
            break
        start += (max_tokens - overlap)
        
    return chunks
