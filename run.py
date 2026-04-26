import sys
import subprocess
import os
import webbrowser
import time

def print_step(step_num, message):
    print(f"\n[Step {step_num}/4] {message}...")

def check_python_version():
    print_step(1, "Checking Python version")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Error: Python 3.11 or higher is required. Found {version.major}.{version.minor}")
        sys.exit(1)
    print("✅ Python version looks good.")

def pre_download_model():
    print_step(2, "Checking/pre-downloading ML model")
    print("   This might take a moment if it's the first run (~1.2 GB download).")
    
    # Tiny script to force transformers to cache the model
    script = """
import logging
import nltk
import spacy
from spacy.cli import download
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

print("   ⌛ Ensuring NLTK tokenizers are downloaded...")
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

logging.getLogger("transformers").setLevel(logging.ERROR)

print("   ⌛ Ensuring DistilBART model is downloaded to cache...")
model_name = "sshleifer/distilbart-cnn-12-6"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

print("   ⌛ Ensuring Sentence-Transformer is downloaded to cache...")
SentenceTransformer('all-MiniLM-L6-v2')

print("   ⌛ Ensuring spaCy small english model is downloaded...")
try:
    spacy.load('en_core_web_sm')
except OSError:
    download('en_core_web_sm')

print("   ✅ All Models are ready!")
"""
    
    try:
        subprocess.run([sys.executable, "-c", script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading model: {e}")
        print("Please ensure you have internet access and have run: pip install -r requirements.txt")
        sys.exit(1)

def start_server():
    print_step(3, "Starting FastAPI server")
    print("   Press Ctrl+C to stop.")
    
    # Start the server as a subprocess so we can open the browser
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait half a second for startup, then open browser
    time.sleep(1.5)
    
    # Check if process died immediately
    if server_process.poll() is not None:
        print("❌ Server failed to start. View output above.")
        out, _ = server_process.communicate()
        print(out)
        sys.exit(1)
        
    print_step(4, "Opening web browser")
    webbrowser.open("http://127.0.0.1:8000")
    
    # Stream the output so the user sees Uvicorn logs
    try:
        for line in server_process.stdout:
            print(f"   [Server] {line.strip()}")
    except KeyboardInterrupt:
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    print("✍️  Starting VeriScribe — Academic Intelligence Engine")
    print("="*50)
    
    if not os.path.exists("app"):
        print("❌ Error: You must run this script from the root project directory.")
        sys.exit(1)
        
    check_python_version()
    pre_download_model()
    start_server()


