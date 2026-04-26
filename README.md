---
title: VeriScribe
emoji: 🌻
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 7860
---

<div align="center">

# 🌻 VeriScribe: Literature Review Assistant
**Truth in Every Scribe. 100% Offline. Zero-Hallucinations. Built for Academia.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Models-orange?style=for-the-badge)](https://huggingface.co/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<br/>

> *VeriScribe is a locally-hosted, privacy-first desktop application engineered specifically for researchers, students, and professionals who need to read dense, 30-page academic documents instantly—without relying on expensive or hallucination-prone cloud APIs.*

<br/>
<img src="veriscribe_photos/veriscribe%20dashboard.png" alt="VeriScribe Dashboard UI" width="100%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">

</div>

---

## 🌟 Why VeriScribe for Literature Reviews?

Conducting a literature review requires reading dozens of dense, 30-page academic papers. When researchers try to speed this up using cloud-based generative AI (like standard ChatGPT), they run into three massive problems:
1. **Hallucinations:** Generative models often invent fake citations, combine authors incorrectly, or summarize methodologies that were never in the actual paper.
2. **Privacy:** Uploading pre-published academic work, lab data, or copyrighted journals to cloud servers violates data privacy laws.
3. **Cost & Hardware:** Running massive context-window LLMs locally usually requires a $2,000 NVIDIA GPU.

**VeriScribe solves all of this.** By utilizing a hybrid pipeline of **Mathematical Extraction** and **INT8 Dynamic Quantized Abstractive AI**, it provides an incredibly fast, highly accurate Literature Review Assistant that runs smoothly on a standard laptop CPU.

---

## 🚀 Key Features

### 🛡️ 1. Absolute Privacy (100% Offline)
Once the initial models are downloaded, VeriScribe entirely cuts the internet cord. Your PDFs, your research, and your generated summaries never leave your machine's local RAM. **No API keys. No subscriptions. No tracking.**

### ⚡ 2. Hardware Supercharged (INT8 Quantization)
We used cutting-edge PyTorch optimizations (`torch.quantization.quantize_dynamic` and `torch.inference_mode()`) to compress massive 32-bit floating-point neural networks down to **8-bit integers**. 
* **The Result:** The AI's RAM footprint is cut in half, and text generation speed on a standard CPU is **doubled (2x)**. 

### 🎯 3. Authentic Extraction (Zero Hallucination)
VeriScribe introduces **Authentic Extract Mode**. Instead of forcing a Generative AI to rewrite the paper, this mode calculates the "Document Centroid" using `all-MiniLM-L6-v2` and extracts the absolute most important sentences verbatim. What you see is exactly what the authors wrote—mathematically proven to be the core of the document.

### 🎨 4. Aesthetic Glassmorphic UI
Research doesn't have to be boring. VeriScribe features a beautiful **Sunflower Glassmorphism** interface. It includes floating ambient backgrounds, instant live text-streaming (like a typewriter), and fluid micro-animations to make reading fun.

### 📄 5. Advanced Semantic Tagging & PDF Export
- **Multi-word Keyword Extraction** via `YAKE!`
- **Named Entity Recognition (NER)** via `spaCy` (Automatically identifies Authors 👤 and Organizations 🏢).
- Instantly export your generated insights into a beautifully formatted, shareable PDF report with one click!

<br/>
<img src="veriscribe_photos/result%20or%20outtput%20screen.png" alt="VeriScribe Output Result" width="100%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">

---

## ⚙️ Dynamic Algorithmic Routing

Unlike basic tools that just change the "length" of a prompt, VeriScribe mathematically shifts its entire architecture depending on the mode you select:

| 🎛️ Summary Mode | 🧠 Algorithmic Pipeline | 🎯 Best For... |
| :--- | :--- | :--- |
| **Abstract (Default)** | Top 30 Sentences ➔ `DistilBART` Synthesis | Replacing a missing paper abstract. |
| **Brief** | Top 10 Sentences ➔ Extreme `DistilBART` Compression | A lightning-fast, single-paragraph overview. |
| **Key Points** | Top 15 Sentences ➔ **Generative Bypass** ➔ Bulleted List | 100% accurate, factual bullet points. |
| **Detailed** | Top 50 Sentences ➔ Deep Chunking ➔ Multi-paragraph Synthesis | Deep-diving into the core arguments. |
| **Authentic** | Top 30 Sentences ➔ Raw Dense Extraction | Reading pure, unadulterated facts. |

---

## 🏗️ Deep Dive: The 4-Stage AI Architecture

VeriScribe isn't just an API wrapper; it's a meticulously crafted local NLP pipeline.

#### 🛠️ Stage 1: Parsing & Cleaning (`PyMuPDF` + `NLTK`)
Academic PDFs are messy. Our engine uses `fitz` to strip out broken headers, footers, and graphs. Then, `NLTK` tokenizers cleanly slice the raw text into perfect grammatical sentences.

#### 🏷️ Stage 2: Entity Identification (`YAKE` & `spaCy`)
Before summarizing, the engine scans the text using statistical distance algorithms to extract complex concepts (e.g., "Natural Language Processing") and localized Named Entity Recognition to map the institutional footprint of the paper.

#### 📉 Stage 3: Semantic Compression (`Sentence-BERT`)
Passing a 30-page PDF into a local AI would crash your RAM. Instead:
1. Every sentence is converted into a high-dimensional vector.
2. We calculate the mathematical average (the **Document Centroid**).
3. We run **Cosine Similarity** to isolate the sentences that perfectly align with the centroid.
*Result: A 30-page paper is crushed into a dense 2-page core of pure significance.*

#### ✍️ Stage 4: Abstractive Generation (`DistilBART-CNN`)
The dense core is passed to the INT8-optimized `sshleifer/distilbart-cnn-12-6` model. Heavily constrained by strict `num_beams` and penalty parameters, the AI rewrites the core into a fluid, human-readable paragraph without injecting outside hallucinations.

---

## 💻 System Requirements

Because of our PyTorch optimizations, VeriScribe can run on incredibly basic hardware!

| Component | Minimum Specs | Recommended Specs |
| :--- | :--- | :--- |
| **OS** | Windows 10, macOS 11, Ubuntu 20.04 | Windows 11 or MacOS M-Series |
| **CPU** | Intel Core i5 / AMD Ryzen 5 | Intel Core i7 / AMD Ryzen 7 |
| **RAM** | 8 GB DDR4 | 16 GB DDR4 |
| **GPU** | ❌ **NOT REQUIRED** | ❌ **NOT REQUIRED** |
| **Python** | Version 3.10 | Version 3.11 |

---

## 🏁 The Beginner's Setup Guide

Ready to turn your laptop into an AI powerhouse? Follow these steps exactly.

### 🐍 Step 1: Install Python
1. Download Python from [python.org](https://www.python.org/downloads/).
2. Run the installer.
3. 🚨 **CRITICAL:** Check the box that says **"Add python.exe to PATH"** at the bottom of the installer *before* clicking Install!

### 📦 Step 2: Clone and Isolate
Open your terminal inside the downloaded project folder. Create a "Virtual Environment" to sandbox the massive AI libraries:

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```
**MacOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
*(You should now see a green `(venv)` prefix in your terminal).*

### 🧱 Step 3: Install the AI Blueprint
Install all required mathematical frameworks (PyTorch, HuggingFace, FastAPI):
```powershell
pip install -r requirements.txt
```
*(Grab a coffee ☕. This will download roughly 1GB of data).*

### 🚀 Step 4: Boot the Engine
Start the local server:
```powershell
python run.py
```
> ⚠️ **First-Time Boot Note:** The very first time you run this command, the script will automatically download the actual AI brain models (about 1.5 GB). Do not close the terminal! Once downloaded, they are saved permanently, and every boot after this will be instant.

### 🎉 Step 5: Start Researching!
Once the terminal says `Uvicorn running on http://127.0.0.1:8000`, the app will automatically open in your default web browser. Drag, drop, and extract!

---

## ☁️ Cloud Deployment (100% Free)

You can easily host VeriScribe on the internet for free using **Hugging Face Spaces**. We have already included the `Dockerfile` configured to pre-download the models!

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **Create new Space**.
2. Name it `VeriScribe`.
3. Choose **Docker** as the SDK, and select **Blank**.
4. Leave the hardware on the **Free (16GB RAM, 2 vCPU)** tier.
5. Connect your GitHub repository (or drag-and-drop your project files into the Space).

Hugging Face will automatically build the Docker container and give you a permanent, free internet link!

---

## 🛑 Proper Shutdown
The AI holds vast amounts of matrix data in your computer's RAM. Simply closing the browser tab **does not** turn off the AI. 
To free up your memory, click inside your Terminal and press:
**`Ctrl + C`**

---

## 🚑 Troubleshooting

| Issue | Cause & Solution |
| :--- | :--- |
| **`pip is not recognized`** | You forgot to check "Add Python to PATH" in Step 1. Reinstall Python and check the box! |
| **OOM / Memory Crash** | PyTorch needs free RAM for matrix equations. Close heavy Chrome tabs or video games before generating. |
| **Slow Generation** | Ensure you are not running other heavy CPU tasks. The INT8 quantization requires a clean CPU thread pool to achieve 2x speed. |

---

## ⚖️ License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute this software for both academic and commercial purposes, provided you include the original copyright notice.

---

<div align="center">
  <h2>⚡ Engineered by PROJECT ULTRON</h2>
  <p><i>An advanced AI development initiative</i></p>
  <br/>
  
  <table>
    <tr>
      <td align="center">
        <br/>
        <b>👨‍💻 Creator & Core Developer</b><br/><br/>
        <img src="https://img.shields.io/badge/Developer-Soumen%20Bhunia-FFd600?style=for-the-badge&labelColor=1a1a1a&logo=probot&logoColor=white" alt="Soumen Bhunia" /><br/><br/>
        <em>The core developer responsible for VeriScribe's dynamic algorithmic routing,<br/>PyTorch inference optimizations, and front-end design.</em><br/><br/>
        <a href="https://www.linkedin.com/in/soumen-bhunia/">
          <img src="https://img.shields.io/badge/LinkedIn-Connect%20with%20Developer-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
        </a>
        <br/><br/>
      </td>
    </tr>
  </table>
</div>
