import math
import spacy
import yake
import torch
import nltk
from sentence_transformers import SentenceTransformer, util

# Initialize lazy loaded models to save memory until first use
_st_model = None
_spacy_model = None

def get_sentence_transformer():
    global _st_model
    if _st_model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        # INT8 Dynamic Quantization for 2x CPU speedup
        _st_model = torch.quantization.quantize_dynamic(
            model, {torch.nn.Linear}, dtype=torch.qint8
        )
    return _st_model

def get_spacy():
    global _spacy_model
    if _spacy_model is None:
        try:
            _spacy_model = spacy.load('en_core_web_sm')
        except OSError:
            from spacy.cli import download
            download('en_core_web_sm')
            _spacy_model = spacy.load('en_core_web_sm')
    return _spacy_model

def pre_summarize_extractive(text: str, max_sentences: int = 30) -> str:
    """
    Extracts the most important semantic sentences using Sentence-BERT embeddings
    and cosine similarity scoring.
    """
    if not text or len(text.split()) < 400:
        return text

    # We need to split text into sentences. NLTK handles this well.
    try:
        sentences = nltk.sent_tokenize(text)
    except:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        sentences = nltk.sent_tokenize(text)

    total_sentences = len(sentences)
    sentences_to_keep = min(max_sentences, max(10, math.ceil(total_sentences * 0.2)))

    if total_sentences <= sentences_to_keep:
        return text

    model = get_sentence_transformer()

    # Get embeddings for all sentences (optimized with inference mode)
    with torch.inference_mode():
        embeddings = model.encode(sentences, convert_to_tensor=True)

    # Compute a simple semantic importance score based on connection to the "global document meaning"
    # Average of sentence embeddings works as a fast document centroid.
    doc_embedding = embeddings.mean(dim=0, keepdim=True)

    # Calculate cosine similarity of each sentence to the document centroid
    cosine_scores = util.cos_sim(embeddings, doc_embedding).squeeze(-1)

    # Get indices of top sentences
    top_results = torch.topk(cosine_scores, k=sentences_to_keep)
    top_indices = top_results.indices.tolist()

    # Sort indices so sentences appear in their original chronological order
    top_indices.sort()
    
    extracted_text = " ".join([sentences[i] for i in top_indices])
    return extracted_text

def extract_top_keywords(text: str, map_count: int = 10) -> list:
    """
    Uses YAKE! to extract high-accuracy, multi-word academic keywords statistically.
    """
    if not text:
        return []
    
    language = "en"
    max_ngram_size = 2
    deduplication_threshold = 0.9
    numOfKeywords = map_count
    
    custom_kw_extractor = yake.KeywordExtractor(
        lan=language, 
        n=max_ngram_size, 
        dedupLim=deduplication_threshold, 
        top=numOfKeywords, 
        features=None
    )
    
    keywords = custom_kw_extractor.extract_keywords(text)
    
    # YAKE returns (keyword, score) where lower score is better.
    # We just want the words capitalized nicely.
    top_words = [kw[0].title() for kw in keywords]
    return top_words

def extract_entities(text: str) -> dict:
    """
    Uses spaCy NER to identify important organizations, people, and metrics/dates.
    """
    if not text:
        return {"organizations": [], "people": [], "concepts": []}

    nlp = get_spacy()
    # Spacy has a max length limit, we only need the first chunk (abstract/intro) for entity extraction
    docs = nlp(text[:10000])

    orgs = set()
    persons = set()
    concepts = set()

    for ent in docs.ents:
        clean_text = ent.text.strip().title()
        if len(clean_text) < 3:
            continue
            
        if ent.label_ == "ORG":
            orgs.add(clean_text)
        elif ent.label_ == "PERSON":
            persons.add(clean_text)
        elif ent.label_ in ["GPE", "NORP", "FAC"]:
            concepts.add(clean_text)
            
    # Convert sets to lists and limit
    return {
        "organizations": list(orgs)[:7],
        "people": list(persons)[:5],
        "concepts": list(concepts)[:5]
    }
