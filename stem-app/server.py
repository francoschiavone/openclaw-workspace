"""
StemSplit — AI Audio Stem Separator
FastAPI backend with Demucs v4 (HTDemucs)
"""

import os

# ── Redirect cache dirs to writable locations (read-only root fs) ────────
CACHE_DIR = "/home/node/.openclaw/workspace/.cache"
os.makedirs(CACHE_DIR, exist_ok=True)
os.environ["TORCH_HOME"] = os.path.join(CACHE_DIR, "torch")
os.environ["XDG_CACHE_HOME"] = CACHE_DIR
os.environ["HOME"] = "/tmp/stemsplit-home"  # For any other ~/.cache writes
os.makedirs("/tmp/stemsplit-home", exist_ok=True)
import sys
import uuid
import time
import json
import shutil
import asyncio
import logging
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import aiofiles

# ── Config ──────────────────────────────────────────────────────────────────
UPLOAD_DIR = Path("/tmp/stemsplit/uploads")
OUTPUT_DIR = Path("/tmp/stemsplit/output")
VENV_PYTHON = Path("/home/node/.openclaw/workspace/.venv-stem/bin/python3")
DEMUCS_CMD = Path("/home/node/.openclaw/workspace/.venv-stem/bin/demucs")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"}

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stemsplit")

# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(title="StemSplit", version="1.0.0")

# Serve static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ── State ───────────────────────────────────────────────────────────────────
jobs: dict = {}
ws_connections: dict = {}


class Job:
    def __init__(self, job_id: str, filename: str, filepath: Path):
        self.id = job_id
        self.filename = filename
        self.filepath = filepath
        self.status = "uploaded"  # uploaded, processing, completed, failed
        self.progress = 0
        self.stems = []
        self.error = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
        self.duration = None

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status,
            "progress": self.progress,
            "stems": self.stems,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "duration": self.duration,
        }


# ── Helpers ─────────────────────────────────────────────────────────────────
def get_audio_duration(filepath: Path) -> Optional[float]:
    """Get audio duration in seconds using ffprobe"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(filepath)],
            capture_output=True, text=True, timeout=10
        )
        return float(result.stdout.strip())
    except Exception:
        return None


async def notify_ws(job_id: str, data: dict):
    """Send update to WebSocket client"""
    if job_id in ws_connections:
        try:
            await ws_connections[job_id].send_json(data)
        except Exception:
            pass


async def process_stems(job: Job):
    """Run Demucs separation in a subprocess"""
    job.status = "processing"
    job.progress = 5
    await notify_ws(job.id, job.to_dict())

    output_path = OUTPUT_DIR / job.id
    output_path.mkdir(parents=True, exist_ok=True)

    start_time = time.time()

    try:
        # Get audio duration for progress estimation
        duration = get_audio_duration(job.filepath)

        # Run demucs as subprocess
        cmd = [
            str(VENV_PYTHON), "-m", "demucs",
            "-n", "htdemucs",
            "--mp3", "--mp3-bitrate", "320",
            "-o", str(output_path),
            str(job.filepath)
        ]

        logger.info(f"Running: {' '.join(cmd)}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Monitor progress by reading stderr (demucs outputs progress there)
        progress_task = asyncio.create_task(
            _monitor_progress(process, job, duration)
        )

        stdout, stderr = await process.communicate()
        await progress_task

        if process.returncode != 0:
            error_msg = stderr.decode()[-500:] if stderr else "Unknown error"
            raise Exception(f"Demucs failed: {error_msg}")

        # Find output stems
        # Demucs outputs to: output_path/htdemucs/<filename_without_ext>/
        stem_dir = None
        for model_dir in output_path.iterdir():
            if model_dir.is_dir():
                for song_dir in model_dir.iterdir():
                    if song_dir.is_dir():
                        stem_dir = song_dir
                        break

        if not stem_dir:
            raise Exception("No output stems found")

        stems = []
        for stem_file in sorted(stem_dir.iterdir()):
            if stem_file.suffix in (".mp3", ".wav"):
                stems.append({
                    "name": stem_file.stem,
                    "filename": stem_file.name,
                    "path": str(stem_file),
                    "size": stem_file.stat().st_size,
                })

        elapsed = time.time() - start_time
        job.status = "completed"
        job.progress = 100
        job.stems = stems
        job.completed_at = datetime.now().isoformat()
        job.duration = round(elapsed, 1)

        logger.info(f"Job {job.id} completed in {elapsed:.1f}s with {len(stems)} stems")

    except Exception as e:
        job.status = "failed"
        job.error = str(e).replace('\n', ' ').replace('\r', '')[:200]
        logger.error(f"Job {job.id} failed: {e}")

    await notify_ws(job.id, job.to_dict())


async def _monitor_progress(process, job: Job, duration: Optional[float]):
    """Monitor demucs stderr for progress updates"""
    estimated_time = (duration * 1.5) if duration else 300  # ~1.5x audio duration on CPU
    start = time.time()

    while process.returncode is None:
        await asyncio.sleep(3)
        elapsed = time.time() - start
        # Estimate progress based on elapsed time vs estimated total
        progress = min(95, int((elapsed / estimated_time) * 100))
        if progress > job.progress:
            job.progress = progress
            await notify_ws(job.id, job.to_dict())


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main page"""
    html_path = STATIC_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text())


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload an audio file and start processing"""

    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported format: {ext}. Supported: {', '.join(ALLOWED_EXTENSIONS)}")

    # Generate job ID
    job_id = str(uuid.uuid4())[:8]

    # Save file
    filepath = UPLOAD_DIR / f"{job_id}{ext}"
    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large. Maximum: {MAX_FILE_SIZE // (1024*1024)}MB")

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    # Create job
    job = Job(job_id, file.filename, filepath)
    jobs[job_id] = job

    # Start processing in background
    asyncio.create_task(process_stems(job))

    return JSONResponse({"job_id": job_id, "status": "uploaded", "filename": file.filename})


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")
    return JSONResponse(jobs[job_id].to_dict())


@app.get("/api/jobs/{job_id}/stems/{stem_name}")
async def download_stem(job_id: str, stem_name: str):
    """Download a specific stem"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    job = jobs[job_id]
    if job.status != "completed":
        raise HTTPException(400, "Job not completed yet")

    for stem in job.stems:
        if stem["name"] == stem_name:
            return FileResponse(
                stem["path"],
                media_type="audio/mpeg",
                filename=f"{Path(job.filename).stem}_{stem_name}.mp3"
            )

    raise HTTPException(404, f"Stem '{stem_name}' not found")


@app.get("/api/jobs/{job_id}/download-all")
async def download_all(job_id: str):
    """Download all stems as ZIP"""
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    job = jobs[job_id]
    if job.status != "completed":
        raise HTTPException(400, "Job not completed yet")

    # Create ZIP
    zip_path = OUTPUT_DIR / f"{job_id}_stems"
    stem_dir = Path(job.stems[0]["path"]).parent
    shutil.make_archive(str(zip_path), "zip", str(stem_dir))

    return FileResponse(
        f"{zip_path}.zip",
        media_type="application/zip",
        filename=f"{Path(job.filename).stem}_stems.zip"
    )


@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket for real-time progress updates"""
    await websocket.accept()
    ws_connections[job_id] = websocket

    try:
        # Send current state immediately
        if job_id in jobs:
            await websocket.send_json(jobs[job_id].to_dict())

        # Keep connection alive
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=60)
            except asyncio.TimeoutError:
                await websocket.send_json({"ping": True})
    except WebSocketDisconnect:
        pass
    finally:
        ws_connections.pop(job_id, None)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
