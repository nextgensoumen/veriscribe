import requests
import json
import httpx
import asyncio

URL = "http://127.0.0.1:8000/api/summarize"

# Test 1: Extremely short text
short_text = "The user is concerned about AI hallucinations."
print(f"--- TEST 1: SHORT TEXT ({len(short_text.split())} words) ---")
res1 = requests.post(URL, json={"text": short_text, "mode": "detailed"})

def parse_sse(response_text):
    words = []
    lines = response_text.strip().split('\n')
    for line in lines:
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                if "word" in data:
                    words.append(data["word"])
            except:
                pass
    return "".join(words)

print("Short result:", parse_sse(res1.text))

# Test 2: Standard Paragraph 
med_text = "Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning. Learning can be supervised, semi-supervised or unsupervised. Artificial neural networks (ANNs) were inspired by information processing and distributed communication nodes in biological systems. ANNs have various differences from biological brains. Specifically, neural networks tend to be static and symbolic, while the biological brain of most living organisms is dynamic (plastic) and analogue."
print(f"--- TEST 2: MED TEXT ({len(med_text.split())} words) ---")
res2 = requests.post(URL, json={"text": med_text, "mode": "abstract"})
print("Med result:", parse_sse(res2.text))
