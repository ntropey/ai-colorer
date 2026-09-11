import os
import sys
import time
import zipfile
import tempfile
import subprocess
import numpy as np
import cv2
import torch
import gradio as gr
from huggingface_hub import PyTorchModelHubMixin

# Ensure app directory is on sys.path for DDColor imports
_root = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.join(_root, "app")
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from ddcolor import DDColor, ColorizationPipeline
import ai_assistant



class DDColorHF(DDColor, PyTorchModelHubMixin):
    def __init__(self, config=None, **kwargs):
        if isinstance(config, dict):
            kwargs = {**config, **kwargs}
        super().__init__(**kwargs)


# Hardware detection
def detect_device():
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else "CUDA"
        return torch.device("cuda"), f"NVIDIA GPU ({name})", "cuda"
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        return torch.device("xpu"), "Intel GPU (XPU Accelerated)", "xpu"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps"), "Apple Silicon (MPS Accelerated)", "mps"
    return torch.device("cpu"), "CPU (Intel / Multi-core)", "cpu"


DEVICE, DEVICE_LABEL, DEVICE_TYPE = detect_device()

MODEL_MAP = {
    "DDColor-L ModelScope (Best for General Photos & Movies)": "piddnad/ddcolor_modelscope",
    "DDColor-L Artistic (Vibrant & Rich Colors, Low Artifacts)": "piddnad/ddcolor_artistic",
    "DDColor-T Tiny (Fast & Lightweight - Recommended for CPU/Intel)": "piddnad/ddcolor_paper_tiny",
    "DDColor-Paper (Original Research Benchmark)": "piddnad/ddcolor_paper",
}

DEFAULT_IMAGE_MODEL = "DDColor-L ModelScope (Best for General Photos & Movies)"
DEFAULT_VIDEO_MODEL = "DDColor-T Tiny (Fast & Lightweight - Recommended for CPU/Intel)"

# In-memory model and pipeline cache
_model_cache = {}
_pipeline_cache = {}
_last_colorized_cache = {"raw_bgr": None, "orig_rgb": None, "orig_bgr": None}
_saved_ai_config = ai_assistant.load_saved_config()


def get_pipeline(model_choice: str, input_size: int = 512, progress=None):
    model_id = MODEL_MAP.get(model_choice, "piddnad/ddcolor_modelscope")
    if model_id not in _model_cache:
        if progress:
            progress(0.1, desc=f"Loading model weights ({model_id})...")
        model = DDColorHF.from_pretrained(model_id).to(DEVICE).eval()
        _model_cache[model_id] = model
    else:
        model = _model_cache[model_id]

    pipe_key = (model_id, int(input_size))
    if pipe_key not in _pipeline_cache:
        pipeline = ColorizationPipeline(model, input_size=int(input_size), device=DEVICE)
        _pipeline_cache[pipe_key] = pipeline
    return _pipeline_cache[pipe_key]


def apply_adjustments(img_rgb: np.ndarray, saturation: float = 1.0, contrast: float = 1.0, brightness: float = 0.0, temperature: int = 0) -> np.ndarray:
    if img_rgb is None:
        return None
    res = img_rgb.astype(np.float32)
    # Color temperature
    if temperature != 0:
        res[:, :, 0] = np.clip(res[:, :, 0] + temperature, 0, 255)
        res[:, :, 2] = np.clip(res[:, :, 2] - temperature, 0, 255)
    # Contrast & Brightness
    if contrast != 1.0 or brightness != 0.0:
        res = np.clip((res - 128.0) * contrast + 128.0 + brightness, 0, 255)
    # Saturation in HSV
    if saturation != 1.0:
        hsv = cv2.cvtColor(res.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
        res = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    return np.clip(res, 0, 255).astype(np.uint8)


def make_side_by_side(orig_rgb: np.ndarray, color_rgb: np.ndarray) -> np.ndarray:
    if orig_rgb is None or color_rgb is None:
        return None
    h, w = orig_rgb.shape[:2]
    if color_rgb.shape[:2] != (h, w):
        color_rgb = cv2.resize(color_rgb, (w, h))

    divider_w = max(4, int(w * 0.006))
    divider = np.full((h, divider_w, 3), 255, dtype=np.uint8)
    combined = np.hstack([orig_rgb, divider, color_rgb])

    scale = max(0.5, min(1.1, w / 700.0))
    thickness = max(1, int(scale * 2))
    margin_x = int(18 * scale)
    margin_y = int(32 * scale)

    # Original label
    cv2.putText(combined, "ORIGINAL B&W", (margin_x, margin_y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(combined, "ORIGINAL B&W", (margin_x, margin_y), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), thickness, cv2.LINE_AA)

    # Colorized label
    offset_color = w + divider_w + margin_x
    cv2.putText(combined, "AI COLORIZED", (offset_color, margin_y), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(combined, "AI COLORIZED", (offset_color, margin_y), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), thickness, cv2.LINE_AA)
    return combined


def colorize_image(
    img,
    model_name=DEFAULT_IMAGE_MODEL,
    input_size=512,
    saturation=1.0,
    contrast=1.0,
    temperature=0,
    ai_enable=False,
    ai_provider="Google Gemini",
    ai_key="",
    ai_model="gemini-2.0-flash",
    ai_context="",
    ai_save_key=False,
    progress=gr.Progress(),
):
    if img is None:
        return None, None, None, "⚠️ Please upload or select a black-and-white image first.", ""

    start_t = time.time()
    bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    ai_card_html = ""

    eff_sat = float(saturation)
    eff_contrast = float(contrast)
    eff_temp = int(temperature)

    if ai_enable and ai_key.strip():
        if ai_save_key:
            ai_assistant.save_api_config(True, ai_provider, ai_key.strip(), ai_model)
        progress(0.1, desc=f"🤖 Calling {ai_provider} for historical vision analysis...")
        ai_res = ai_assistant.analyze_historical_scene(
            bgr,
            provider=ai_provider,
            api_key=ai_key.strip(),
            model=ai_model,
            context_hint=ai_context.strip()
        )
        if "error" not in ai_res:
            eff_sat *= float(ai_res.get("saturation_bias", 1.0))
            eff_contrast *= float(ai_res.get("contrast_bias", 1.0))
            eff_temp += int(ai_res.get("color_temperature", 0))
        ai_card_html = ai_assistant.render_ai_card(ai_res)

    progress(0.4, desc="🎨 Colorizing image with local neural model...")
    pipeline = get_pipeline(model_name, int(input_size), progress=progress)
    result_bgr = pipeline.process(bgr)

    _last_colorized_cache["raw_bgr"] = result_bgr
    _last_colorized_cache["orig_rgb"] = img
    _last_colorized_cache["orig_bgr"] = bgr

    result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
    adjusted_rgb = apply_adjustments(result_rgb, eff_sat, eff_contrast, 0.0, eff_temp)
    sbs_rgb = make_side_by_side(img, adjusted_rgb)

    out_dir = tempfile.mkdtemp(prefix="ai-colorer-img-")
    out_path = os.path.join(out_dir, "colorized_image.png")
    cv2.imwrite(out_path, cv2.cvtColor(adjusted_rgb, cv2.COLOR_RGB2BGR))

    elapsed = time.time() - start_t
    ai_tag = f" • 🤖 {ai_provider} Guided" if (ai_enable and ai_key.strip()) else ""
    status = (
        f"✅ **Colorization Complete** in **{elapsed:.2f}s** • "
        f"Resolution: {img.shape[1]}×{img.shape[0]} px • "
        f"Model: {model_name.split()[0]} • "
        f"Engine: {DEVICE_LABEL}{ai_tag}"
    )
    return adjusted_rgb, sbs_rgb, out_path, status, ai_card_html


def quick_adjust(saturation=1.0, contrast=1.0, temperature=0):
    if _last_colorized_cache["raw_bgr"] is None:
        return None, None, None, "⚠️ No image has been colorized yet. Please colorize an image first.", ""

    raw_bgr = _last_colorized_cache["raw_bgr"]
    orig_rgb = _last_colorized_cache["orig_rgb"]
    raw_rgb = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2RGB)
    adjusted_rgb = apply_adjustments(raw_rgb, float(saturation), float(contrast), 0.0, int(temperature))
    sbs_rgb = make_side_by_side(orig_rgb, adjusted_rgb)

    out_dir = tempfile.mkdtemp(prefix="ai-colorer-adjust-")
    out_path = os.path.join(out_dir, "colorized_adjusted.png")
    cv2.imwrite(out_path, cv2.cvtColor(adjusted_rgb, cv2.COLOR_RGB2BGR))
    status = f"✨ **Adjustments Applied Instantly** (Saturation: {saturation:.2f}×, Contrast: {contrast:.2f}×, Temp: {temperature:+d})"
    return adjusted_rgb, sbs_rgb, out_path, status, ""


def ai_critique_step(ai_provider, ai_key, ai_model, progress=gr.Progress()):
    if _last_colorized_cache["raw_bgr"] is None:
        return None, None, None, "⚠️ Please colorize an image first.", ""
    if not ai_key.strip():
        return None, None, None, "⚠️ Please enter an AI API key first.", ""

    progress(0.2, desc=f"🤖 Sending to {ai_provider} for critique...")
    critique = ai_assistant.critique_and_refine(
        _last_colorized_cache["orig_bgr"],
        _last_colorized_cache["raw_bgr"],
        provider=ai_provider,
        api_key=ai_key.strip(),
        model=ai_model
    )
    if "error" in critique:
        return None, None, None, f"⚠️ AI Critique notice: {critique['error']}", ""

    sat_delta = float(critique.get("saturation_delta", 0.0))
    temp_delta = int(critique.get("temperature_delta", 0))
    contrast_delta = float(critique.get("contrast_delta", 0.0))

    raw_rgb = cv2.cvtColor(_last_colorized_cache["raw_bgr"], cv2.COLOR_BGR2RGB)
    adjusted_rgb = apply_adjustments(raw_rgb, 1.0 + sat_delta, 1.0 + contrast_delta, 0.0, temp_delta)
    sbs_rgb = make_side_by_side(_last_colorized_cache["orig_rgb"], adjusted_rgb)

    out_dir = tempfile.mkdtemp(prefix="ai-colorer-critique-")
    out_path = os.path.join(out_dir, "colorized_critique_refined.png")
    cv2.imwrite(out_path, cv2.cvtColor(adjusted_rgb, cv2.COLOR_RGB2BGR))

    summary = critique.get("critique_summary", "Review complete.")
    card_html = f'''<div style="background:#0f172a;border:1px solid #10b981;border-radius:10px;padding:12px;margin-top:12px;">
      <strong style="color:#34d399;font-size:14px;">🤖 AI Colorist Critique & Refinement:</strong>
      <p style="color:#e2e8f0;margin:6px 0;font-size:13px;"><em>"{summary}"</em></p>
      <div style="color:#94a3b8;font-size:11px;">Applied deltas: Saturation {sat_delta:+0.2f}, Temp {temp_delta:+d}, Contrast {contrast_delta:+0.2f}</div>
    </div>'''
    status = f"✨ **AI Colorist Critique Applied** ({summary[:60]}...)"
    return adjusted_rgb, sbs_rgb, out_path, status, card_html


def ai_analyze_video_keyframe(video_path, provider, key, model, context, progress=gr.Progress()):
    if not video_path:
        return "⚠️ Please upload a video first.", ""
    if not key.strip():
        return "⚠️ Please provide an AI API key first.", ""

    cap = cv2.VideoCapture(video_path)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return "⚠️ Failed to extract keyframe from video.", ""

    progress(0.2, desc=f"🤖 Sending keyframe to {provider} for historical scene analysis...")
    ai_res = ai_assistant.analyze_historical_scene(
        frame,
        provider=provider,
        api_key=key.strip(),
        model=model,
        context_hint=context.strip()
    )
    card_html = ai_assistant.render_ai_card(ai_res)
    sat = ai_res.get("saturation_bias", 1.0)
    temp = ai_res.get("color_temperature", 0)
    msg = f"✅ Keyframe analyzed! Recommended historical bias: Saturation {sat:.2f}×, Warmth {temp:+d}."
    return msg, card_html



def colorize_batch(files, model_name=DEFAULT_IMAGE_MODEL, input_size=512, saturation=1.0, progress=gr.Progress()):
    if not files:
        return [], None, "⚠️ Please select one or more images to colorize."

    start_t = time.time()
    pipeline = get_pipeline(model_name, int(input_size), progress=progress)
    out_dir = tempfile.mkdtemp(prefix="ai-colorer-batch-")
    zip_path = os.path.join(out_dir, "colorized_batch_photos.zip")

    gallery_items = []
    total = len(files)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for idx, f in enumerate(files):
            f_path = f.name if hasattr(f, "name") else str(f)
            progress((idx) / total, desc=f"Colorizing image {idx + 1} of {total}...")
            orig_bgr = cv2.imread(f_path)
            if orig_bgr is None:
                continue
            colored_bgr = pipeline.process(orig_bgr)
            colored_rgb = cv2.cvtColor(colored_bgr, cv2.COLOR_BGR2RGB)
            if saturation != 1.0:
                colored_rgb = apply_adjustments(colored_rgb, float(saturation))
                colored_bgr = cv2.cvtColor(colored_rgb, cv2.COLOR_BGR2RGB)

            base_name = os.path.splitext(os.path.basename(f_path))[0]
            out_img_name = f"colorized_{base_name}.png"
            out_img_path = os.path.join(out_dir, out_img_name)
            cv2.imwrite(out_img_path, cv2.cvtColor(colored_rgb, cv2.COLOR_RGB2BGR))
            zip_f.write(out_img_path, arcname=out_img_name)
            gallery_items.append((colored_rgb, f"Colorized: {base_name}"))

    elapsed = time.time() - start_t
    status = f"✅ **Batch Complete!** Successfully colorized **{len(gallery_items)} photos** in **{elapsed:.1f}s**."
    return gallery_items, zip_path, status


def colorize_video(
    video_path,
    model_name=DEFAULT_VIDEO_MODEL,
    input_size=384,
    mode="Preview: First 5 Seconds",
    preview_duration=5,
    video_scale="Original Resolution",
    output_format="Full Colorized Video",
    progress=gr.Progress(),
):
    if not video_path:
        return None, None, "⚠️ Please upload or select a video to colorize."

    start_time = time.time()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    src_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

    if not total_frames:
        try:
            duration_s = float(subprocess.check_output([
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", video_path,
            ], text=True).strip())
            total_frames = max(1, round(duration_s * fps))
        except Exception:
            total_frames = 0

    max_frames = total_frames if total_frames > 0 else 999999
    if mode == "Preview: First 5 Seconds":
        max_frames = min(max_frames, max(1, int(5 * fps)))
    elif mode == "Preview: First 10 Seconds":
        max_frames = min(max_frames, max(1, int(10 * fps)))
    elif mode == "Custom Duration (Seconds)":
        max_frames = min(max_frames, max(1, int(preview_duration * fps)))

    target_width, target_height = src_width, src_height
    if video_scale == "Downscale to 720p" and src_height > 720:
        ratio = 720.0 / src_height
        target_height = 720
        target_width = int((src_width * ratio) // 2 * 2)
    elif video_scale == "Downscale to 480p" and src_height > 480:
        ratio = 480.0 / src_height
        target_height = 480
        target_width = int((src_width * ratio) // 2 * 2)

    is_sbs = (output_format == "Side-by-Side Video (B&W Left | Color Right)")
    out_width = (target_width * 2) if is_sbs else target_width
    out_height = target_height

    out_dir = tempfile.mkdtemp(prefix="ai-colorer-vid-")
    output_path = os.path.join(out_dir, "colorized_video.mp4")

    pipeline = get_pipeline(model_name, int(input_size), progress=progress)

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{out_width}x{out_height}", "-r", str(fps),
        "-i", "-",
        "-i", video_path,
        "-map", "0:v:0", "-map", "1:a:0?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest",
        output_path,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    frame_idx = 0
    t_start_processing = time.time()
    try:
        while frame_idx < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            if (target_width, target_height) != (src_width, src_height):
                frame = cv2.resize(frame, (target_width, target_height))

            colorized = pipeline.process(frame)

            if is_sbs:
                frame_to_pipe = np.hstack([frame, colorized])
            else:
                frame_to_pipe = colorized

            proc.stdin.write(frame_to_pipe.tobytes())
            frame_idx += 1

            if frame_idx % 3 == 0 or frame_idx == max_frames:
                elapsed = time.time() - t_start_processing
                fps_speed = frame_idx / max(0.001, elapsed)
                rem_frames = max_frames - frame_idx
                eta_s = rem_frames / max(0.001, fps_speed)
                desc = f"Colorizing frame {frame_idx}/{max_frames} ({fps_speed:.1f} fps • ETA: {eta_s:.0f}s)"
                progress(min(frame_idx / max_frames, 1.0), desc=desc)
    finally:
        cap.release()
        proc.stdin.close()
        proc.wait()

    if proc.returncode != 0 or not os.path.exists(output_path):
        raise gr.Error("ffmpeg failed to assemble the colorized video.")

    total_time = time.time() - start_time
    avg_fps = frame_idx / max(0.001, total_time)
    status = (
        f"✅ **Video Colorization Finished!**\n\n"
        f"- **Frames Rendered:** {frame_idx} of {max_frames} frames\n"
        f"- **Render Speed:** {avg_fps:.1f} FPS (Total: {total_time:.1f}s)\n"
        f"- **Output Resolution:** {out_width}×{out_height} @ {fps:.1f} FPS\n"
        f"- **Audio:** Original audio track synchronized and preserved\n"
        f"- **Hardware Engine:** {DEVICE_LABEL}"
    )
    return output_path, output_path, status


# Sample images from assets/test_images
sample_images = []
test_img_dir = os.path.join(_app_dir, "assets", "test_images")
if os.path.exists(test_img_dir):
    candidates = [
        "Audrey Hepburn.jpg",
        "Helen Keller meeting Charlie Chaplin in 1919.jpg",
        "Louis Armstrong practicing in his dressing room, ca 1946.jpg",
        "Acrobats Balance On Top Of The Empire State Building, 1934.jpg",
        "Detroit circa 1915.jpg",
        "New York Riverfront December 15, 1931.jpg",
    ]
    for c in candidates:
        p = os.path.join(test_img_dir, c)
        if os.path.exists(p):
            sample_images.append([p])

custom_css = """
.header-box {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    padding: 24px;
    border-radius: 14px;
    border: 1px solid #334155;
    margin-bottom: 20px;
    color: #f8fafc;
}
.header-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
    margin-top: 6px;
    background: #0284c7;
    color: #ffffff;
}
.hardware-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
    margin-top: 6px;
    background: #059669;
    color: #ffffff;
}
.ai-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
    margin-top: 6px;
    background: #7c3aed;
    color: #ffffff;
}
.action-btn {
    border-radius: 10px !important;
    font-weight: 600 !important;
}
"""

with gr.Blocks(title="AI Colorer - Neural Film & Photo Colorization") as demo:
    with gr.Column(elem_classes=["header-box"]):
        gr.Markdown(
            """# 🎨 AI Colorer
### Photo-Realistic Neural Colorization for Public Domain Movies & Archival Photos""" +
            f"\n<span class='hardware-badge'>⚡ Active Engine: {DEVICE_LABEL}</span> "
            "<span class='ai-badge'>🤖 Optional AI Vision Guidance</span> "
            "<span class='header-badge'>🔒 100% Private & Local</span> "
            "<span class='header-badge'>🧩 Powered by DDColor (ICCV 2023)</span>"
        )

    with gr.Tabs():
        # TAB 1: Single Image
        with gr.Tab("🖼️ Single Image", id="tab_image"):
            with gr.Row():
                with gr.Column(scale=5):
                    image_in = gr.Image(label="Black & White Image (Drop or Upload)", type="numpy")

                    with gr.Accordion("🤖 AI Vision Assistant (Optional API Key)", open=False):
                        gr.Markdown("Provide an optional AI Vision API key (Google Gemini offers free-tier keys) to research authentic historical pigments, uniforms, and period palettes before local colorization.")
                        with gr.Row():
                            ai_enable = gr.Checkbox(label="Enable AI Historical Guidance", value=_saved_ai_config["enabled"], scale=1)
                            ai_save_key = gr.Checkbox(label="Remember API Key locally in .env", value=bool(_saved_ai_config["api_key"]), scale=1)
                        with gr.Row():
                            ai_provider = gr.Dropdown(
                                label="AI Provider",
                                choices=list(ai_assistant.PROVIDER_DEFAULTS.keys()),
                                value=_saved_ai_config["provider"],
                                scale=1
                            )
                            ai_model = gr.Dropdown(
                                label="Vision Model",
                                choices=ai_assistant.PROVIDER_DEFAULTS[_saved_ai_config["provider"]]["models"],
                                value=_saved_ai_config["model"],
                                scale=1
                            )
                        ai_key = gr.Textbox(
                            label="API Key",
                            type="password",
                            placeholder="Enter Google Gemini, OpenAI, Anthropic, or OpenRouter key...",
                            value=_saved_ai_config["api_key"]
                        )
                        ai_context = gr.Textbox(
                            label="Historical Context / Clues (Optional)",
                            placeholder="e.g. 1919 London street, British Army uniforms, or leave blank for auto-detection",
                            value=""
                        )

                        def on_provider_change(prov):
                            info = ai_assistant.PROVIDER_DEFAULTS.get(prov, {})
                            models = info.get("models", [])
                            default_m = info.get("model", models[0] if models else "")
                            return gr.update(choices=models, value=default_m)

                        ai_provider.change(on_provider_change, inputs=ai_provider, outputs=ai_model)

                    with gr.Accordion("⚙️ Model & Neural Settings", open=True):
                        img_model = gr.Dropdown(
                            label="Colorization Model",
                            choices=list(MODEL_MAP.keys()),
                            value=DEFAULT_IMAGE_MODEL,
                            info="ModelScope: balanced photorealism | Artistic: vibrant saturation | Tiny: fastest on CPU/Intel",
                        )
                        img_input_size = gr.Slider(
                            label="Color Inference Resolution (input_size)",
                            minimum=256,
                            maximum=1024,
                            step=128,
                            value=512,
                            info="Higher values produce finer color detail; lower values run faster.",
                        )

                    with gr.Accordion("🎨 Color Tuning & Adjustments", open=True):
                        img_sat = gr.Slider(
                            label="Color Saturation / Vibrancy",
                            minimum=0.5,
                            maximum=2.0,
                            step=0.05,
                            value=1.0,
                            info="1.0 = Natural | > 1.0 = More colorful and vibrant | < 1.0 = Pastel / Muted",
                        )
                        with gr.Row():
                            img_contrast = gr.Slider(
                                label="Contrast",
                                minimum=0.8,
                                maximum=1.3,
                                step=0.02,
                                value=1.0,
                            )
                            img_temp = gr.Slider(
                                label="Temperature Tint",
                                minimum=-30,
                                maximum=30,
                                step=1,
                                value=0,
                                info="Cool (Blue) ← 0 → Warm (Amber)",
                            )

                    with gr.Row():
                        image_btn = gr.Button("🎨 Colorize Image", variant="primary", scale=2, elem_classes=["action-btn"])
                        readjust_btn = gr.Button("✨ Quick Re-adjust", variant="secondary", scale=1, elem_classes=["action-btn"])
                        critique_btn = gr.Button("🤖 AI Critique", variant="secondary", scale=1, elem_classes=["action-btn"])

                with gr.Column(scale=6):
                    with gr.Tabs():
                        with gr.Tab("🎨 Colorized Result"):
                            image_out = gr.Image(label="Colorized Image", type="numpy")
                        with gr.Tab("⚖️ Side-by-Side Comparison"):
                            image_sbs = gr.Image(label="Side-by-Side Comparison", type="numpy")

                    img_download = gr.File(label="📥 Download Colorized Image (PNG)")
                    img_status = gr.Markdown("Ready to colorize.")
                    ai_card = gr.HTML()

            image_btn.click(
                colorize_image,
                inputs=[image_in, img_model, img_input_size, img_sat, img_contrast, img_temp, ai_enable, ai_provider, ai_key, ai_model, ai_context, ai_save_key],
                outputs=[image_out, image_sbs, img_download, img_status, ai_card],
                api_name="colorize_image",
            )

            readjust_btn.click(
                quick_adjust,
                inputs=[img_sat, img_contrast, img_temp],
                outputs=[image_out, image_sbs, img_download, img_status, ai_card],
            )

            critique_btn.click(
                ai_critique_step,
                inputs=[ai_provider, ai_key, ai_model],
                outputs=[image_out, image_sbs, img_download, img_status, ai_card],
            )

            if sample_images:
                gr.Markdown("### 🏛️ Sample Public Domain Historical Photos (Click to Load)")
                gr.Examples(
                    examples=sample_images,
                    inputs=image_in,
                    label="Historical Archive Photos",
                )

        # TAB 2: Batch Images
        with gr.Tab("📁 Batch Photos", id="tab_batch"):
            gr.Markdown(
                """### Batch Colorize Multiple Historical Photos
Upload multiple black-and-white images (family albums, archive collections) to process all of them at once and download a ZIP package."""
            )
            with gr.Row():
                with gr.Column(scale=5):
                    batch_files = gr.File(
                        label="Select or Drop Multiple Images",
                        file_count="multiple",
                        file_types=["image"],
                    )
                    batch_model = gr.Dropdown(
                        label="Model",
                        choices=list(MODEL_MAP.keys()),
                        value=DEFAULT_IMAGE_MODEL,
                    )
                    batch_input_size = gr.Slider(
                        label="Color Inference Resolution",
                        minimum=256,
                        maximum=1024,
                        step=128,
                        value=512,
                    )
                    batch_sat = gr.Slider(
                        label="Saturation Multiplier",
                        minimum=0.5,
                        maximum=2.0,
                        step=0.05,
                        value=1.0,
                    )
                    batch_btn = gr.Button("🚀 Colorize All Photos", variant="primary", elem_classes=["action-btn"])

                with gr.Column(scale=6):
                    batch_gallery = gr.Gallery(label="Colorized Photos Gallery", columns=3, height=450)
                    batch_zip = gr.File(label="📥 Download All Colorized Photos (.zip)")
                    batch_status = gr.Markdown("Ready for batch photos.")

            batch_btn.click(
                colorize_batch,
                inputs=[batch_files, batch_model, batch_input_size, batch_sat],
                outputs=[batch_gallery, batch_zip, batch_status],
            )

        # TAB 3: Video Colorization
        with gr.Tab("🎬 Video & Movies", id="tab_video"):
            gr.Markdown(
                """### Black-and-White Movie & Clip Colorization
Colorizes frames sequentially and synchronizes the original audio track into H.264 MP4.
Use **Preview Snippets** to quickly test settings before processing entire feature-length films!"""
            )
            with gr.Row():
                with gr.Column(scale=5):
                    video_in = gr.Video(label="Input Black & White Video")

                    with gr.Accordion("🤖 AI Keyframe Historical Analysis (Optional)", open=False):
                        gr.Markdown("Analyze the opening keyframe of your movie with an AI Vision model to preview the period palette before running the full film.")
                        with gr.Row():
                            vid_ai_provider = gr.Dropdown(
                                label="AI Provider",
                                choices=list(ai_assistant.PROVIDER_DEFAULTS.keys()),
                                value=_saved_ai_config["provider"],
                                scale=1
                            )
                            vid_ai_model = gr.Dropdown(
                                label="Vision Model",
                                choices=ai_assistant.PROVIDER_DEFAULTS[_saved_ai_config["provider"]]["models"],
                                value=_saved_ai_config["model"],
                                scale=1
                            )
                        vid_ai_key = gr.Textbox(
                            label="API Key",
                            type="password",
                            placeholder="Enter API key...",
                            value=_saved_ai_config["api_key"]
                        )
                        vid_ai_context = gr.Textbox(
                            label="Movie Context (Year, Film Title, Setting)",
                            placeholder="e.g. 1928 Buster Keaton silent comedy",
                            value=""
                        )
                        vid_ai_btn = gr.Button("🔍 Analyze Video Keyframe", variant="secondary")

                        vid_ai_provider.change(on_provider_change, inputs=vid_ai_provider, outputs=vid_ai_model)

                    with gr.Accordion("⚙️ Video & Performance Settings", open=True):
                        vid_model = gr.Dropdown(
                            label="Colorization Model",
                            choices=list(MODEL_MAP.keys()),
                            value=DEFAULT_VIDEO_MODEL,
                            info="DDColor-T Tiny is recommended for videos on CPU/Intel for fastest rendering.",
                        )
                        vid_input_size = gr.Slider(
                            label="Color Resolution (input_size)",
                            minimum=256,
                            maximum=512,
                            step=128,
                            value=384,
                            info="384 or 256 recommended for high video FPS throughput.",
                        )
                        vid_mode = gr.Dropdown(
                            label="Processing Scope",
                            choices=[
                                "Preview: First 5 Seconds",
                                "Preview: First 10 Seconds",
                                "Full Video",
                                "Custom Duration (Seconds)",
                            ],
                            value="Preview: First 5 Seconds",
                            info="Preview modes let you quickly evaluate results in seconds.",
                        )
                        vid_custom_dur = gr.Slider(
                            label="Custom Duration Limit (Seconds)",
                            minimum=1,
                            maximum=600,
                            step=1,
                            value=15,
                            visible=False,
                        )

                        def update_dur_visibility(mode_val):
                            return gr.update(visible=(mode_val == "Custom Duration (Seconds)"))

                        vid_mode.change(update_dur_visibility, inputs=vid_mode, outputs=vid_custom_dur)

                        vid_scale = gr.Dropdown(
                            label="Video Resolution",
                            choices=[
                                "Original Resolution",
                                "Downscale to 720p",
                                "Downscale to 480p",
                            ],
                            value="Original Resolution",
                            info="Downscaling to 720p or 480p provides a dramatic speedup on CPU.",
                        )
                        vid_output_format = gr.Dropdown(
                            label="Output Presentation",
                            choices=[
                                "Full Colorized Video",
                                "Side-by-Side Video (B&W Left | Color Right)",
                            ],
                            value="Full Colorized Video",
                            info="Side-by-Side is great for social media demos and comparisons.",
                        )

                    video_btn = gr.Button("🎬 Colorize Video", variant="primary", elem_classes=["action-btn"])

                with gr.Column(scale=6):
                    video_out = gr.Video(label="Colorized Video Output")
                    vid_download = gr.File(label="📥 Download Colorized Video (.mp4)")
                    video_status = gr.Markdown("Ready to process video.")
                    vid_ai_card = gr.HTML()

            vid_ai_btn.click(
                ai_analyze_video_keyframe,
                inputs=[video_in, vid_ai_provider, vid_ai_key, vid_ai_model, vid_ai_context],
                outputs=[video_status, vid_ai_card],
            )

            video_btn.click(
                colorize_video,
                inputs=[video_in, vid_model, vid_input_size, vid_mode, vid_custom_dur, vid_scale, vid_output_format],
                outputs=[video_out, vid_download, video_status],
                api_name="colorize_video",
            )

        # TAB 4: Guide & Public Domain Archives
        with gr.Tab("📖 Guide & Archives", id="tab_guide"):
            gr.Markdown(
                """
                ### 📚 About AI Colorer & DDColor
                **AI Colorer** is a local, privacy-first colorization suite powered by **DDColor** (ICCV 2023).
                It uses dual decoders and learnable color query tokens to realistically restore monochrome footage without cloud servers or token costs.

                ---

                ### 🤖 Optional AI Vision Guidance (How to Get an API Key)
                You can optionally connect an AI Vision model (such as **Google Gemini**, **OpenAI**, **Anthropic**, or **OpenRouter**) to act as an archival researcher:
                - **Google Gemini**: Get a **free** API key at [aistudio.google.com](https://aistudio.google.com/app/apikey) (generous free tier, no paid billing required!).
                - **OpenAI**: Get an API key at [platform.openai.com](https://platform.openai.com/api-keys).
                - **Anthropic**: Get an API key at [console.anthropic.com](https://console.anthropic.com/settings/keys).
                - **OpenRouter**: Universal multi-provider access at [openrouter.ai](https://openrouter.ai/keys).

                When enabled, the vision model inspects the black-and-white scene, deduces the exact historical era, uniforms, materials, and lighting, and automatically recommends optimal color grading and palette swatches.

                ---

                ### 🏛️ Where to Find Free Public Domain Movies & Photos
                You can freely download thousands of classic historical films, newsreels, and photographs:
                1. **[Internet Archive: Prelinger Archives](https://archive.org/details/prelinger)** — Over 17,000 vintage educational, industrial, and advertising films from 1903–1990s.
                2. **[Library of Congress National Screening Room](https://www.loc.gov/collections/national-screening-room/)** — Historical American movies and documentary shorts.
                3. **[Wikimedia Commons: Public Domain Videos](https://commons.wikimedia.org/wiki/Category:Public_domain_videos)** — Historical speeches, silent film classics, and scientific reels.
                4. **[PublicDomainMovies.net](https://publicdomainmovies.net/)** — Classic silent movies, Charlie Chaplin films, Buster Keaton, and early noir.

                ---

                ### 💡 Pro Tips for Best Results
                - **For Photos**: Use `DDColor-L ModelScope` with `input_size=512` or `768` for maximum sharpness and vivid detail.
                - **For Video on CPU / Intel**: Choose `DDColor-T Tiny` and `input_size=384`. Run a **Preview (First 5s)** first to check the aesthetic before running the full film.
                - **Finetuning Colors**: Use the **Color Tuning** sliders (Saturation, Contrast, Temperature) and click **Quick Re-adjust** to dial in the perfect vintage look without waiting for neural recalculation!

                ---

                ### 🔌 API Reference
                This application exposes standard Gradio API endpoints accessible via Python, JavaScript, and cURL:
                - `colorize_image(img, model_name, input_size, saturation, contrast, temperature, ai_enable, ai_provider, ai_key, ai_model, ai_context, ai_save_key)`
                - `colorize_video(video_path, model_name, input_size, mode, preview_duration, video_scale, output_format)`
                """
            )


if __name__ == "__main__":
    demo.queue().launch(server_name="127.0.0.1", theme=gr.themes.Soft(), css=custom_css)
