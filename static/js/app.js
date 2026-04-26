// =========================================================================
// STATE MANAGEMENT
// =========================================================================
const AppState = {
    file: null,
    text: "",
    mode: "abstract",
    extractedData: null,
    isGenerating: false,
    startTime: 0,
    timerInterval: null
};

// =========================================================================
// DOM ELEMENTS
// =========================================================================
const Screens = {
    upload: document.getElementById('screen-upload'),
    preview: document.getElementById('screen-preview'),
    generating: document.getElementById('screen-generating'),
    result: document.getElementById('screen-result')
};

// Upload
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const browseBtn = document.getElementById('browse-btn');
const uploadError = document.getElementById('upload-error');

// Preview
const btnBack = document.getElementById('btn-back');
const fileName = document.getElementById('file-name');
const fileSize = document.getElementById('file-size');
const filePages = document.getElementById('file-pages');
const wordCount = document.getElementById('word-count');
const previewText = document.getElementById('preview-text');
const btnExpandPreview = document.getElementById('btn-expand-preview');
const previewContentWrap = document.querySelector('.preview-content-wrap');
const btnGenerate = document.getElementById('btn-generate');
const modePills = document.querySelectorAll('.mode-pill');

// Generating
const streamingText = document.getElementById('streaming-text');
const generationTimer = document.getElementById('generation-timer');
const progressBar = document.getElementById('generation-progress');
const btnCancel = document.getElementById('btn-cancel');

// Result
const finalSummaryText = document.getElementById('final-summary-text');
const resultWordCount = document.getElementById('result-word-count');
const resultTime = document.getElementById('result-time');
const resultMode = document.getElementById('result-mode');
const btnCopy = document.getElementById('btn-copy');
const btnDownload = document.getElementById('btn-download');
const btnNew = document.getElementById('btn-new');
const keywordsContainer = document.getElementById('keywords-container');
const resultSavedTime = document.getElementById('result-saved-time');

// Toast
const toast = document.getElementById('toast');

// Controller for aborting API requests
let abortController = null;

// =========================================================================
// INITIALIZATION AND EVENT LISTENERS
// =========================================================================
document.addEventListener('DOMContentLoaded', () => {
    setupUploadListeners();
    setupPreviewListeners();
    setupGeneratingListeners();
    setupResultListeners();
});

function switchScreen(screenName) {
    Object.values(Screens).forEach(screen => {
        screen.classList.remove('view-active');
        // wait for fade out before hiding completely
        setTimeout(() => {
            if(!screen.classList.contains('view-active')) screen.classList.add('hidden');
        }, 400); 
    });
    
    setTimeout(() => {
        Screens[screenName].classList.remove('hidden');
        // prompt reflow
        void Screens[screenName].offsetWidth;
        Screens[screenName].classList.add('view-active');
    }, 400);
}

function showToast(message) {
    document.getElementById('toast-message').textContent = message;
    toast.classList.add('show');
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

// =========================================================================
// UPLOAD LOGIC
// =========================================================================
function setupUploadListeners() {
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // prevent double click if inside drop zone
        fileInput.click();
    });
    
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    ['dragleave', 'dragend'].forEach(type => {
        dropZone.addEventListener(type, () => {
            dropZone.classList.remove('dragover');
        });
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });
}

async function handleFile(file) {
    uploadError.classList.add('hidden');
    
    // Validate size client side (50MB)
    if(file.size > 50 * 1024 * 1024) {
        uploadError.textContent = "File is too large. Max size is 50MB.";
        uploadError.classList.remove('hidden');
        return;
    }
    
    // UI state change to uploading...
    const cta = dropZone.querySelector('.upload-cta');
    const originalText = cta.innerHTML;
    cta.innerHTML = `<strong>Uploading & Extracting text...</strong>`;
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Upload failed");
        }

        const data = await response.json();
        AppState.file = file;
        AppState.extractedData = data;
        AppState.text = data.full_text;
        
        populatePreviewScreen(data);
        switchScreen('preview');
        
    } catch (err) {
        uploadError.textContent = err.message;
        uploadError.classList.remove('hidden');
    } finally {
        cta.innerHTML = originalText;
        fileInput.value = ""; // reset
    }
}

// =========================================================================
// PREVIEW LOGIC
// =========================================================================
function setupPreviewListeners() {
    btnBack.addEventListener('click', () => {
        AppState.file = null;
        AppState.text = "";
        switchScreen('upload');
    });

    btnExpandPreview.addEventListener('click', () => {
        previewContentWrap.classList.toggle('expanded');
        const icon = previewContentWrap.classList.contains('expanded') ? 'minimize-2' : 'maximize-2';
        btnExpandPreview.innerHTML = `<i data-lucide="${icon}"></i>`;
        lucide.createIcons();
    });

    modePills.forEach(pill => {
        pill.addEventListener('click', () => {
            modePills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            AppState.mode = pill.dataset.mode;
        });
    });

    btnGenerate.addEventListener('click', generateSummary);
}

function populatePreviewScreen(data) {
    fileName.textContent = data.filename;
    fileName.title = data.filename;
    fileSize.textContent = formatBytes(data.size_bytes);
    filePages.textContent = `${data.pages} Page${data.pages > 1 ? 's' : ''}`;
    
    // Animate word count
    const targetCount = data.word_count;
    let count = 0;
    const interval = setInterval(() => {
        count += Math.ceil(targetCount / 20); // reach target in ~20 frames
        if (count >= targetCount) {
            count = targetCount;
            clearInterval(interval);
        }
        wordCount.textContent = count.toLocaleString();
    }, 20);

    previewText.textContent = data.text_preview;
    
    // Update icon color based on type
    const icon = document.getElementById('file-icon');
    icon.className = '';
    if(data.content_type.includes('pdf')) icon.classList.add('hot-pink-text');
    else if(data.content_type.includes('document') || data.content_type.includes('word')) icon.classList.add('cyan-text');
    else icon.classList.add('violet-text');
}

// =========================================================================
// GENERATION (STREAMING) LOGIC
// =========================================================================
function setupGeneratingListeners() {
    btnCancel.addEventListener('click', () => {
        if(abortController) {
            abortController.abort();
        }
        clearInterval(AppState.timerInterval);
        switchScreen('preview');
    });
}

function startTimer() {
    AppState.startTime = Date.now();
    generationTimer.textContent = `⏱ 0.0s elapsed`;
    
    AppState.timerInterval = setInterval(() => {
        const elapsed = ((Date.now() - AppState.startTime) / 1000).toFixed(1);
        generationTimer.textContent = `⏱ ${elapsed}s elapsed`;
        
        // Fake progress bar that approaches 95% asymptotically
        const progress = 95 - (95 / (1 + (elapsed / 5)));
        progressBar.style.width = `${progress}%`;
    }, 100);
}

async function generateSummary() {
    switchScreen('generating');
    streamingText.innerHTML = '';
    const cursor = document.getElementById('cursor');
    cursor.classList.remove('hidden');
    startTimer();
    
    abortController = new AbortController();
    
    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: AppState.text,
                mode: AppState.mode
            }),
            signal: abortController.signal
        });

        if (!response.ok) {
            const errorData = await response.json().catch(()=>({}));
            throw new Error(errorData.detail || "Server error occurred");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let fullSummary = "";
        
        // Progress stage change
        document.getElementById('generation-stage').textContent = "Generating summary...";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.substring(6).trim();
                    if (!dataStr) continue;
                    
                    try {
                        const payload = JSON.parse(dataStr);
                        if(payload.word) {
                            // Append word with fade-in animation wrap
                            if (payload.word.includes('\n')) {
                                const parts = payload.word.split('\n');
                                parts.forEach((part, index) => {
                                    if (index > 0) streamingText.appendChild(document.createElement('br'));
                                    if (part) {
                                        const span = document.createElement('span');
                                        span.className = 'word';
                                        span.textContent = part;
                                        streamingText.appendChild(span);
                                    }
                                });
                            } else {
                                const span = document.createElement('span');
                                span.className = 'word';
                                span.textContent = payload.word;
                                streamingText.appendChild(span);
                            }
                            fullSummary += payload.word;
                            
                            // Scroll to bottom
                            const wrap = document.querySelector('.streaming-content-wrap');
                            wrap.scrollTop = wrap.scrollHeight;
                        }
                    } catch(e) { /* ignore parse errors for partial chunks boundaries */ }
                } else if (line.startsWith('event: complete')) {
                    // done
                } else if (line.startsWith('event: error')) {
                    throw new Error("Stream closed with error");
                }
            }
        }
        
        clearInterval(AppState.timerInterval);
        progressBar.style.width = `100%`;
        cursor.classList.add('hidden');
        
        // Move to result screen
        setTimeout(() => {
            populateResultScreen(fullSummary.trim());
            switchScreen('result');
        }, 500);

    } catch (err) {
        if(err.name === 'AbortError') return; // Expected cancellation
        clearInterval(AppState.timerInterval);
        alert(`Error generating summary: ${err.message}`);
        switchScreen('preview');
    }
}

// =========================================================================
// RESULT LOGIC
// =========================================================================
function setupResultListeners() {
    btnCopy.addEventListener('click', () => {
        navigator.clipboard.writeText(finalSummaryText.textContent).then(() => {
            // Visual feedback
            const originalHtml = btnCopy.innerHTML;
            btnCopy.innerHTML = `<i data-lucide="check"></i> <span class="emerald-text">Copied!</span>`;
            lucide.createIcons();
            showToast("Copied to clipboard!");
            
            setTimeout(() => {
                btnCopy.innerHTML = originalHtml;
                lucide.createIcons();
            }, 2000);
        });
    });

    btnDownload.addEventListener('click', () => {
        const textToSave = finalSummaryText.innerText;
        const fn = AppState.file ? AppState.file.name.replace(/\.[^/.]+$/, "") : "document";
        
        // Advanced Feature: Generate PDF natively
        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            doc.setFontSize(14);
            doc.setFont("helvetica", "bold");
            doc.text("VeriScribe Intelligence Report", 20, 20);
            
            doc.setFontSize(14);
            doc.setTextColor(100);
            doc.text(`Source Document: ${AppState.file ? AppState.file.name : 'Unknown'}`, 20, 30);
            
            if(AppState.extractedData && AppState.extractedData.keywords) {
                doc.setFontSize(10);
                doc.setTextColor(6, 182, 212); // Cyan tag
                doc.text(`Keywords: ${AppState.extractedData.keywords.join(" | ")}`, 20, 40);
            }
            
            doc.setFont("helvetica", "normal");
            doc.setFontSize(12);
            doc.setTextColor(0);
            // Split text to fit page width
            const splitText = doc.splitTextToSize(textToSave, 170);
            doc.text(splitText, 20, 50);
            
            doc.save(`Report_${fn}.pdf`);
            showToast("PDF Downloaded successfully!");
        } catch(e) {
            // Fallback to text if jsPDF didn't load
            console.error("PDF generation failed, falling back to TXT", e);
            const blob = new Blob([textToSave], { type: "text/plain" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `Summary_${fn}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    });

    btnNew.addEventListener('click', () => {
        AppState.file = null;
        AppState.text = "";
        switchScreen('upload');
    });
}

function populateResultScreen(summaryHtml) {
    // Basic formatting: convert all newlines to <br> for bullet points
    finalSummaryText.innerHTML = summaryHtml.replace(/\n/g, '<br>');
    
    // Stats
    const elapsed = ((Date.now() - AppState.startTime) / 1000).toFixed(1);
    const wc = summaryHtml.split(/\s+/).filter(x => x.length > 0).length;
    
    resultWordCount.textContent = `${wc} words`;
    resultTime.textContent = `Generated in ${elapsed}s`;
    
    // Analytics Feature: Reading Time Saved
    const originalWc = AppState.extractedData ? AppState.extractedData.word_count : 0;
    const wordsSaved = Math.max(0, originalWc - wc);
    // Avg human reads at 200 WPM
    let timeSaved = (wordsSaved / 200).toFixed(1);
    if(timeSaved < 1) {
        timeSaved = `< 1 min`;
    } else {
        timeSaved = `${Math.ceil(timeSaved)} mins`;
    }
    resultSavedTime.innerHTML = `<i data-lucide="clock"></i> Saved ${timeSaved}`;
    
    // Keywords Rendering
    keywordsContainer.innerHTML = '';
    if(AppState.extractedData && AppState.extractedData.keywords && AppState.extractedData.keywords.length > 0) {
        AppState.extractedData.keywords.forEach(kw => {
            const span = document.createElement('span');
            span.className = 'tag-keyword';
            span.textContent = kw;
            keywordsContainer.appendChild(span);
        });
    }

    // Entities Rendering
    const entitiesContainer = document.getElementById('entities-container');
    if (entitiesContainer) {
        entitiesContainer.innerHTML = '';
        if(AppState.extractedData && AppState.extractedData.entities) {
            const orgs = AppState.extractedData.entities.organizations || [];
            const people = AppState.extractedData.entities.people || [];
            const allEntities = [...orgs.map(e => `🏢 ${e}`), ...people.map(p => `👤 ${p}`)];
            
            allEntities.slice(0, 8).forEach(ent => {
                const span = document.createElement('span');
                span.className = 'tag-keyword';
                span.style.background = 'rgba(139, 92, 246, 0.1)';
                span.style.color = '#c4b5fd';
                span.style.border = '1px solid rgba(139, 92, 246, 0.2)';
                span.textContent = ent;
                entitiesContainer.appendChild(span);
            });
        }
    }

    const modeNameMap = {
        abstract: "Abstract mode",
        brief: "Brief outline",
        key_points: "Key points",
        detailed: "Detailed mode",
        authentic: "Authentic Extraction"
    };
    resultMode.textContent = modeNameMap[AppState.mode] || "Summarized";
    lucide.createIcons();
}
