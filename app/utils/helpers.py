import chardet
from typing import Optional

def detect_encoding(raw_bytes: bytes) -> str:
    """
    Detects the encoding of an array of bytes using chardet.
    Defaults to utf-8 if detection fails.
    """
    result = chardet.detect(raw_bytes)
    encoding = result.get('encoding')
    if encoding is None:
        encoding = "utf-8"
        
    return encoding

def count_words(text: str) -> int:
    """A simplistic word counter based on split."""
    if not text:
        return 0
    return len(text.split())
