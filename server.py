"""
Dolce Colore - Local API Server (FastAPI)
Connects the frontend UI to the ONNX Runtime colorization engine and AI vision guidance.
"""

import os
import sys
import uuid
import json
import base64
import tempfile
import asyncio
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
import logging
logger = logging.getLogger("DolceColore")
logger.info("server.py: loading modules...")

# Ensure PyInstaller includes python-multipart for FastAPI Form/File request body handling
try:
    import multipart
except ImportError:
    pass

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np

logger.info("server.py: importing dolce_engine...")
import dolce_engine
logger.info("server.py: importing ai_vision...")
import ai_vision
logger.info("server.py: importing license_manager...")
import license_manager
from app_version import __version__
import webbrowser

if getattr(sys, "frozen", False):
    _ROOT = sys._MEIPASS
else:
    _ROOT = os.path.dirname(os.path.abspath(__file__))

TEMP_DIR = os.path.join(tempfile.gettempdir(), "dolce_colore_media")
os.makedirs(TEMP_DIR, exist_ok=True)

logger.info("server.py: creating FastAPI app...")
app = FastAPI(title="Dolce Colore API", version=__version__)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("server.py: instantiating DolceEngine...")
engine = dolce_engine.DolceEngine()
logger.info("server.py: initialization complete!")
video_jobs = {}


def img_to_base64_jpeg(img_rgb: np.ndarray, quality: int = 90) -> str:
    """Helper to convert RGB numpy image to base64 JPEG data URL."""
    if img_rgb is None:
        return ""
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return ""
    b64 = base64.b64encode(buf).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


@app.get("/api/system/status")
def get_system_status():
    """Return hardware accelerator, available models, and current AI config."""
    cfg = ai_vision.load_ai_config()
    active_hw = dolce_engine.PROVIDER_LABEL
    if "ddcolor-tiny" in engine.sessions:
        active_hw = engine.sessions["ddcolor-tiny"][2]
    return {
        "version": __version__,
        "hardware": active_hw,
        "providers_available": dolce_engine.PROVIDERS,
        "models": dolce_engine.AVAILABLE_MODELS,
        "ai_config": {
            "enabled": cfg.get("enabled", False),
            "provider": cfg.get("provider", "Google Gemini"),
            "has_key": bool(cfg.get("api_key")),
            "model": cfg.get("model", "gemini-2.0-flash"),
        },
        "ffmpeg": os.path.basename(engine.ffmpeg_path),
        "license": license_manager.get_license_status()
    }


@app.get("/api/license/status")
def get_license():
    """Get active license status and tier."""
    return license_manager.get_license_status()


@app.post("/api/license/activate")
def activate_license(key: str = Form(...)):
    """Validate and activate an algorithmic license key."""
    result = license_manager.activate_key(key)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Invalid license key"))
    return result


@app.post("/api/license/deactivate")
def deactivate_license():
    """Deactivate license and revert to Community Edition."""
    return license_manager.deactivate_key()


@app.post("/api/system/open-url")
def open_system_url(url: str = Form(...)):
    """Open an external link (e.g. Revisited Labs) in the user's default browser."""
    if url.startswith("https://") or url.startswith("http://"):
        webbrowser.open_new_tab(url)
        return {"success": True, "url": url}
    raise HTTPException(status_code=400, detail="Invalid URL protocol")


@app.post("/api/config/ai")
def save_config(
    enabled: bool = Form(...),
    provider: str = Form(...),
    api_key: str = Form(""),
    model: str = Form("")
):
    saved = ai_vision.save_ai_config(enabled, provider, api_key, model)
    return {"status": "ok", "saved": {"enabled": saved["enabled"], "provider": saved["provider"], "has_key": bool(saved["api_key"])}}


@app.post("/api/colorize/photo")
async def colorize_photo(
    file: Optional[UploadFile] = File(None),
    model_key: str = Form("ddcolor-tiny"),
    saturation: float = Form(1.0),
    contrast: float = Form(1.0),
    brightness: float = Form(0.0),
    temperature: int = Form(0),
    use_ai: bool = Form(False),
    ai_context: str = Form("")
):
    if file is None:
        raise HTTPException(status_code=400, detail="No image file provided.")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Could not decode image.")

    eff_sat = float(saturation)
    eff_contrast = float(contrast)
    eff_temp = int(temperature)
    ai_analysis = None

    # Optional Vision AI Historical Guidance
    cfg = ai_vision.load_ai_config()
    if use_ai and cfg.get("api_key"):
        res = ai_vision.analyze_historical_scene(
            img_bgr,
            provider=cfg.get("provider", "Google Gemini"),
            api_key=cfg["api_key"],
            model=cfg.get("model", "gemini-2.0-flash"),
            context_hint=ai_context.strip()
        )
        if "error" not in res:
            ai_analysis = res
            eff_sat *= float(res.get("saturation_bias", 1.0))
            eff_contrast *= float(res.get("contrast_bias", 1.0))
            eff_temp += int(res.get("color_temperature", 0))

    result = engine.colorize_image(
        img_bgr,
        model_key=model_key,
        saturation=eff_sat,
        contrast=eff_contrast,
        brightness=brightness,
        temperature=eff_temp
    )

    # Save high-res PNG for 1-click download
    file_id = str(uuid.uuid4())
    out_filename = f"colorized_{file_id}.png"
    out_path = os.path.join(TEMP_DIR, out_filename)
    cv2.imwrite(out_path, cv2.cvtColor(result["colorized_rgb"], cv2.COLOR_RGB2BGR))

    # Also save original for client-side comparison slider
    orig_filename = f"original_{file_id}.png"
    orig_path = os.path.join(TEMP_DIR, orig_filename)
    cv2.imwrite(orig_path, img_bgr)

    return {
        "id": file_id,
        "colorized_url": f"/media/{out_filename}",
        "original_url": f"/media/{orig_filename}",
        "split_preview": img_to_base64_jpeg(result["split_rgb"], quality=85),
        "metrics": {
            "elapsed_ms": result["elapsed_ms"],
            "width": result["width"],
            "height": result["height"],
            "hardware": result["hardware"],
        },
        "ai_analysis": ai_analysis,
        "applied_adjustments": {
            "saturation": round(eff_sat, 2),
            "contrast": round(eff_contrast, 2),
            "temperature": eff_temp
        }
    }


@app.post("/api/adjust")
def quick_adjust(
    saturation: float = Form(1.0),
    contrast: float = Form(1.0),
    brightness: float = Form(0.0),
    temperature: int = Form(0)
):
    """Real-time instant color grading of last cached photo."""
    result = engine.quick_tune_cache(
        saturation=saturation,
        contrast=contrast,
        brightness=brightness,
        temperature=temperature
    )
    if result is None:
        raise HTTPException(status_code=400, detail="No active image in cache.")

    file_id = str(uuid.uuid4())
    out_filename = f"adjusted_{file_id}.png"
    out_path = os.path.join(TEMP_DIR, out_filename)
    cv2.imwrite(out_path, cv2.cvtColor(result["colorized_rgb"], cv2.COLOR_RGB2BGR))

    return {
        "colorized_url": f"/media/{out_filename}",
        "split_preview": img_to_base64_jpeg(result["split_rgb"], quality=85)
    }


@app.post("/api/ai/analyze")
def trigger_ai_analysis(context_hint: str = Form("")):
    """Analyze the currently cached image with AI Vision."""
    if engine.last_cache["orig_bgr"] is None:
        raise HTTPException(status_code=400, detail="No image loaded.")
    cfg = ai_vision.load_ai_config()
    if not cfg.get("api_key"):
        raise HTTPException(status_code=400, detail="No Vision API key configured.")

    res = ai_vision.analyze_historical_scene(
        engine.last_cache["orig_bgr"],
        provider=cfg.get("provider", "Google Gemini"),
        api_key=cfg["api_key"],
        model=cfg.get("model", "gemini-2.0-flash"),
        context_hint=context_hint
    )
    return res


@app.post("/api/ai/critique")
def trigger_ai_critique():
    """Critique the colorized output skin tones and vibrancy."""
    if engine.last_cache["orig_bgr"] is None or engine.last_cache["raw_color_bgr"] is None:
        raise HTTPException(status_code=400, detail="No colorized image available.")
    cfg = ai_vision.load_ai_config()
    if not cfg.get("api_key"):
        raise HTTPException(status_code=400, detail="No Vision API key configured.")

    res = ai_vision.critique_and_refine(
        engine.last_cache["orig_bgr"],
        engine.last_cache["raw_color_bgr"],
        provider=cfg.get("provider", "Google Gemini"),
        api_key=cfg["api_key"],
        model=cfg.get("model", "gemini-2.0-flash")
    )
    return res


@app.post("/api/colorize/video")
async def start_video_colorization(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_key: str = Form("ddcolor-tiny"),
    mode: str = Form("preview-5s"),
    custom_duration: float = Form(5.0),
    resolution: str = Form("original"),
    side_by_side: bool = Form(False),
    saturation: float = Form(1.0),
    contrast: float = Form(1.0),
    temperature: int = Form(0)
):
    job_id = str(uuid.uuid4())
    input_video_path = os.path.join(TEMP_DIR, f"input_{job_id}_{file.filename}")
    output_video_path = os.path.join(TEMP_DIR, f"colorized_{job_id}.mp4")

    contents = await file.read()
    with open(input_video_path, "wb") as f:
        f.write(contents)

    video_jobs[job_id] = {
        "status": "processing",
        "progress": 0.0,
        "frame": 0,
        "total": 0,
        "fps": 0.0,
        "eta_s": 0.0,
        "output_url": None,
        "error": None
    }

    def run_job():
        def progress_cb(pct, info):
            if job_id in video_jobs:
                video_jobs[job_id].update({
                    "progress": round(pct * 100, 1),
                    "frame": info.get("frame", 0),
                    "total": info.get("total", 0),
                    "fps": info.get("fps", 0.0),
                    "eta_s": info.get("eta_s", 0.0),
                    "elapsed_s": info.get("elapsed_s", 0.0)
                })

        try:
            res = engine.colorize_video(
                video_path=input_video_path,
                output_path=output_video_path,
                model_key=model_key,
                mode=mode,
                custom_duration=custom_duration,
                resolution_mode=resolution,
                side_by_side=side_by_side,
                saturation=saturation,
                contrast=contrast,
                temperature=temperature,
                progress_callback=progress_cb
            )
            video_jobs[job_id]["status"] = "completed"
            video_jobs[job_id]["output_url"] = f"/media/{os.path.basename(output_video_path)}"
        except Exception as e:
            video_jobs[job_id]["status"] = "failed"
            video_jobs[job_id]["error"] = str(e)

    background_tasks.add_task(run_job)
    return {"job_id": job_id}


@app.get("/api/video/status/{job_id}")
def get_video_job_status(job_id: str):
    if job_id not in video_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return video_jobs[job_id]


@app.get("/media/{filename}")
def serve_media(filename: str):
    path = os.path.join(TEMP_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    media_type = "video/mp4" if filename.endswith(".mp4") else "image/png"
    return FileResponse(path, media_type=media_type)


# Static frontend hosting (when frontend build exists)
FRONTEND_DIST = os.path.join(_ROOT, "frontend", "dist")
if os.path.isdir(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
