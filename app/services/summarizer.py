import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import threading
import asyncio
import math
from typing import AsyncGenerator
from app.config import settings, SUMMARIZATION_MODES
from app.services.preprocessor import chunk_text
from app.services.extractive import pre_summarize_extractive

class SummarizerService:
    """Singleton service for the ML model."""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SummarizerService, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        # We load the model synchronously on startup
        self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(settings.MODEL_NAME)
        
        # INT8 Dynamic Quantization for 2x CPU speedup
        self.model = torch.quantization.quantize_dynamic(
            self.model, {torch.nn.Linear}, dtype=torch.qint8
        )
        self.pipe = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=-1,  # Force CPU to ensure it works without GPU
        )

    def _summarize_sync(self, text: str, mode: str) -> str:
        """Synchronous hybrid summarization logic."""
        params = SUMMARIZATION_MODES.get(mode, SUMMARIZATION_MODES["abstract"])
        
        # Determine extraction depth based on mode
        if mode == "brief":
            max_sents = 10
        elif mode == "detailed":
            max_sents = 50
        elif mode == "key_points":
            max_sents = 15
        else:  # abstract and authentic
            max_sents = 30
            
        # 1. EXTRACTIVE PRE-FILTERING (Fast CPU dense extraction)
        dense_text = pre_summarize_extractive(text, max_sentences=max_sents)
        
        # 1.5 FAST AUTHENTIC BYPASS (CPU Optimized, Zero Hallucination)
        if mode == "authentic":
            return dense_text
            
        # 1.6 KEY POINTS BYPASS (Format as bulleted list for 100% accuracy)
        if mode == "key_points":
            import nltk
            sentences = nltk.sent_tokenize(dense_text)
            bullets = [f"• {s.strip()}" for s in sentences if len(s.strip()) > 15]
            return "\n".join(bullets)
        
        # 2. ABSTRACTIVE GENERATION (DistilBART rewriting)
        chunks = chunk_text(dense_text, self.tokenizer)
        
        # Using a single chunk or max 2 chunks since we pre-filtered it.
        # num_beams=2 (down from 4) practically doubles the speed while keeping flow smooth.
        if len(chunks) == 1:
            input_len = len(self.tokenizer.encode(chunks[0], add_special_tokens=False))
            if input_len < 30:
                return chunks[0]  # Too short to summarize meaningfully
                
            safe_max = min(params["max_length"], max(15, int(input_len * 0.85)))
            safe_min = min(params["min_length"], max(5, int(input_len * 0.25)))
            safe_min = min(safe_min, safe_max - 5)

            with torch.inference_mode():
                result = self.pipe(
                    chunks[0],
                    max_length=safe_max,
                    min_length=safe_min,
                    do_sample=False,
                    num_beams=2,  # Dropped from 4 for significant CPU speedup
                    length_penalty=1.0,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                )
            return result[0]["summary_text"]
            
        # Fallback if the extracted dense text is slightly over the 1024 token limit
        chunk_summaries = []
        for chunk in chunks:
            input_len = len(self.tokenizer.encode(chunk, add_special_tokens=False))
            if input_len < 20:
                chunk_summaries.append(chunk)
                continue
                
            c_max = min(math.ceil(params["max_length"] / len(chunks)), max(10, int(input_len * 0.85)))
            c_min = min(math.ceil(params["min_length"] / len(chunks)), max(5, int(input_len * 0.25)))
            c_min = min(c_min, c_max - 2)

            with torch.inference_mode():
                result = self.pipe(
                    chunk, 
                    max_length=c_max, 
                    min_length=c_min, 
                    do_sample=False,
                    num_beams=1  # greedy search for speed on fragments
                )
            chunk_summaries.append(result[0]["summary_text"])
            
        final_text = " ".join(chunk_summaries)
        
        # Clean up the junction of the fragments
        final_len = len(self.tokenizer.encode(final_text, add_special_tokens=False))
        if final_len < 30:
            return final_text
            
        f_max = min(params["max_length"], max(15, int(final_len * 0.85)))
        f_min = min(params["min_length"], max(5, int(final_len * 0.25)))
        f_min = min(f_min, f_max - 5)

        with torch.inference_mode():
            final_result = self.pipe(
                final_text[:4000],  # safety cap
                max_length=f_max,
                min_length=f_min,
                do_sample=False,
                num_beams=2,  # Dropped from 4 for significant CPU speedup
                length_penalty=1.2,
                early_stopping=True,
                no_repeat_ngram_size=3,
            )
        return final_result[0]["summary_text"]

    async def stream_summary(self, text: str, mode: str) -> AsyncGenerator[str, None]:
        """
        Since the transformers pipeline doesn't have a built-in token streamer 
        that works nicely out of the box with the high-level `pipeline` API, 
        we generate the summary in a background thread and then stream the words.
        This provides a smooth UI experience while not blocking the event loop.
        """
        # Run the heavy CPU bound task in a separate thread
        summary_text = await asyncio.to_thread(self._summarize_sync, text, mode)
        
        # Stream the words to the client instantly
        words = summary_text.split(" ")
        for word in words:
            yield word + " "
            # Removed the 0.05s artificial delay to instantly blast text to the screen
            await asyncio.sleep(0.005) 
