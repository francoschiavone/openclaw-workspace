/**
 * StemSplit — Frontend Application
 */

// ── State ────────────────────────────────────────────────────────────────
let currentJobId = null;
let ws = null;
let currentAudio = null;
let currentPlayBtn = null;

// ── DOM ──────────────────────────────────────────────────────────────────
const uploadZone = document.getElementById('uploadZone');
const uploadInner = document.getElementById('uploadInner');
const fileInput = document.getElementById('fileInput');
const processingCard = document.getElementById('processingCard');
const resultsCard = document.getElementById('resultsCard');
const fileName = document.getElementById('fileName');
const fileStatus = document.getElementById('fileStatus');
const progressPercent = document.getElementById('progressPercent');
const progressFill = document.getElementById('progressFill');
const processingTip = document.getElementById('processingTip');
const stemsGrid = document.getElementById('stemsGrid');
const resultFilename = document.getElementById('resultFilename');
const resultTime = document.getElementById('resultTime');
const downloadAllBtn = document.getElementById('downloadAllBtn');
const newSplitBtn = document.getElementById('newSplitBtn');

// ── Processing Tips ──────────────────────────────────────────────────────
const tips = [
    'Analyzing audio structure...',
    'Identifying vocal patterns...',
    'Separating drum transients...',
    'Isolating bass frequencies...',
    'Extracting harmonic content...',
    'Applying neural network masks...',
    'Refining stem boundaries...',
    'Optimizing separation quality...',
    'Almost there — finalizing stems...',
];

let tipIndex = 0;
let tipInterval = null;

function cycleTips() {
    tipIndex = (tipIndex + 1) % tips.length;
    processingTip.textContent = tips[tipIndex];
}

// ── Stem Icons (SVG) ────────────────────────────────────────────────────
const stemIcons = {
    vocals: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" y1="19" x2="12" y2="23"/>
        <line x1="8" y1="23" x2="16" y2="23"/>
    </svg>`,
    drums: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10"/>
        <circle cx="12" cy="12" r="4"/>
        <line x1="12" y1="2" x2="12" y2="8"/>
        <line x1="12" y1="16" x2="12" y2="22"/>
        <line x1="2" y1="12" x2="8" y2="12"/>
        <line x1="16" y1="12" x2="22" y2="12"/>
    </svg>`,
    bass: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 18V5l12-2v13"/>
        <circle cx="6" cy="18" r="3"/>
        <circle cx="18" cy="16" r="3"/>
    </svg>`,
    other: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 18V5l12-2v13"/>
        <circle cx="6" cy="18" r="3"/>
        <circle cx="18" cy="16" r="3"/>
    </svg>`,
};

// ── Upload Handling ─────────────────────────────────────────────────────

// Click to upload
uploadZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
    if (e.target.files[0]) handleFile(e.target.files[0]);
});

// Drag & drop
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragging');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('dragging');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragging');
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
});

async function handleFile(file) {
    // Validate
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    const allowed = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma'];
    if (!allowed.includes(ext)) {
        alert(`Unsupported format: ${ext}\nSupported: ${allowed.join(', ')}`);
        return;
    }

    if (file.size > 50 * 1024 * 1024) {
        alert('File too large. Maximum: 50MB');
        return;
    }

    // Show processing card
    uploadZone.classList.add('hidden');
    resultsCard.classList.add('hidden');
    processingCard.classList.remove('hidden');

    fileName.textContent = file.name;
    fileStatus.textContent = 'Uploading...';
    progressPercent.textContent = '0%';
    progressFill.style.width = '0%';

    // Start tip cycling
    tipIndex = 0;
    processingTip.textContent = tips[0];
    tipInterval = setInterval(cycleTips, 4000);

    // Upload
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Upload failed');
        }

        const data = await response.json();
        currentJobId = data.job_id;

        fileStatus.textContent = 'Processing with AI...';

        // Connect WebSocket for progress
        connectWebSocket(data.job_id);

    } catch (err) {
        showError(err.message);
    }
}

// ── WebSocket ───────────────────────────────────────────────────────────

function connectWebSocket(jobId) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/${jobId}`);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.ping) return;

        // Update progress
        if (data.progress !== undefined) {
            progressPercent.textContent = `${data.progress}%`;
            progressFill.style.width = `${data.progress}%`;
        }

        // Update status text
        if (data.status === 'processing') {
            fileStatus.textContent = 'Separating stems...';
        }

        // Completed
        if (data.status === 'completed') {
            clearInterval(tipInterval);
            showResults(data);
        }

        // Failed
        if (data.status === 'failed') {
            clearInterval(tipInterval);
            showError(data.error || 'Processing failed');
        }
    };

    ws.onerror = () => {
        // Fallback to polling
        pollJob(jobId);
    };

    ws.onclose = () => {
        // If not completed, poll
        if (currentJobId && !resultsCard.classList.contains('hidden') === false) {
            pollJob(jobId);
        }
    };
}

async function pollJob(jobId) {
    const poll = async () => {
        try {
            const resp = await fetch(`/api/jobs/${jobId}`);
            const data = await resp.json();

            progressPercent.textContent = `${data.progress}%`;
            progressFill.style.width = `${data.progress}%`;

            if (data.status === 'completed') {
                clearInterval(tipInterval);
                showResults(data);
                return;
            }

            if (data.status === 'failed') {
                clearInterval(tipInterval);
                showError(data.error);
                return;
            }

            // Continue polling
            setTimeout(poll, 3000);
        } catch (err) {
            setTimeout(poll, 5000);
        }
    };

    poll();
}

// ── Results ──────────────────────────────────────────────────────────────

function showResults(data) {
    processingCard.classList.add('hidden');
    resultsCard.classList.remove('hidden');

    resultFilename.textContent = data.filename;
    resultTime.textContent = `Processed in ${data.duration}s`;

    // Build stems grid
    stemsGrid.innerHTML = '';

    data.stems.forEach(stem => {
        const card = document.createElement('div');
        card.className = 'stem-card';

        const stemClass = stem.name.toLowerCase();
        const icon = stemIcons[stemClass] || stemIcons.other;
        const size = formatSize(stem.size);

        card.innerHTML = `
            <div class="stem-icon ${stemClass}">
                ${icon}
            </div>
            <div class="stem-info">
                <div class="stem-name">${stem.name}</div>
                <div class="stem-size">${size} • MP3 320kbps</div>
            </div>
            <div class="stem-actions">
                <button class="stem-btn play-btn" data-stem="${stem.name}" title="Play/Pause">
                    <svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                        <polygon points="5,3 19,12 5,21"/>
                    </svg>
                </button>
                <a class="stem-btn" href="/api/jobs/${currentJobId}/stems/${stem.name}" download title="Download">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="7 10 12 15 17 10"/>
                        <line x1="12" y1="15" x2="12" y2="3"/>
                    </svg>
                </a>
            </div>
        `;

        stemsGrid.appendChild(card);
    });

    // Setup play buttons
    document.querySelectorAll('.play-btn').forEach(btn => {
        btn.addEventListener('click', () => togglePlay(btn));
    });
}

function togglePlay(btn) {
    const stemName = btn.dataset.stem;
    const url = `/api/jobs/${currentJobId}/stems/${stemName}`;

    // If clicking same button that's playing, pause
    if (currentAudio && currentPlayBtn === btn) {
        if (currentAudio.paused) {
            currentAudio.play();
            btn.classList.add('playing');
            btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <rect x="6" y="4" width="4" height="16"/>
                <rect x="14" y="4" width="4" height="16"/>
            </svg>`;
        } else {
            currentAudio.pause();
            btn.classList.remove('playing');
            btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <polygon points="5,3 19,12 5,21"/>
            </svg>`;
        }
        return;
    }

    // Stop previous
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
        if (currentPlayBtn) {
            currentPlayBtn.classList.remove('playing');
            currentPlayBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <polygon points="5,3 19,12 5,21"/>
            </svg>`;
        }
    }

    // Play new
    currentAudio = new Audio(url);
    currentPlayBtn = btn;
    currentAudio.play();
    btn.classList.add('playing');
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
        <rect x="6" y="4" width="4" height="16"/>
        <rect x="14" y="4" width="4" height="16"/>
    </svg>`;

    currentAudio.addEventListener('ended', () => {
        btn.classList.remove('playing');
        btn.innerHTML = `<svg viewBox="0 0 24 24" fill="currentColor" stroke="none">
            <polygon points="5,3 19,12 5,21"/>
        </svg>`;
        currentAudio = null;
        currentPlayBtn = null;
    });
}

// ── Error ────────────────────────────────────────────────────────────────

function showError(message) {
    processingCard.classList.add('hidden');
    uploadZone.classList.remove('hidden');

    // Brief error display
    const zone = uploadInner;
    const original = zone.innerHTML;
    zone.innerHTML = `
        <div class="error-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
        </div>
        <p style="color: var(--stem-vocals); font-weight: 600;">Error</p>
        <p style="color: var(--text-secondary); font-size: 14px;">${message}</p>
        <p style="color: var(--text-muted); font-size: 13px; margin-top: 8px;">Click to try again</p>
    `;

    setTimeout(() => {
        zone.innerHTML = original;
    }, 5000);
}

// ── Download All ────────────────────────────────────────────────────────

downloadAllBtn.addEventListener('click', () => {
    if (currentJobId) {
        window.location.href = `/api/jobs/${currentJobId}/download-all`;
    }
});

// ── New Split ───────────────────────────────────────────────────────────

newSplitBtn.addEventListener('click', () => {
    // Stop audio
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }

    // Reset state
    currentJobId = null;
    resultsCard.classList.add('hidden');
    processingCard.classList.add('hidden');
    uploadZone.classList.remove('hidden');
    fileInput.value = '';
});

// ── Helpers ─────────────────────────────────────────────────────────────

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
