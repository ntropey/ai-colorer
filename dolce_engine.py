"""
Dolce Colore - Neural Colorization Engine (ONNX Runtime)
High-performance, lightweight, PyTorch-free colorization.
"""

import os
import sys
import time
import zipfile
import tempfile
import subprocess
import shutil
import numpy as np
import cv2
import logging
logger = logging.getLogger("DolceColore")
logger.info("dolce_engine.py: importing onnxruntime...")
import onnxruntime as ort
logger.info("dolce_engine.py: onnxruntime imported")

if getattr(sys, "frozen", False):
    _ROOT = sys._MEIPASS
else:
    _ROOT = os.path.dirname(os.path.abspath(__file__))

MODELS_DIR = os.path.join(_ROOT, "models")
TOOLS_DIR = os.path.join(_ROOT, "tools")

# Supported models configuration
AVAILABLE_MODELS = {
    "ddcolor-tiny": {
        "name": "DDColor-T Tiny (Fast & Lightweight)",
        "file": "ddcolor-tiny-fp16.onnx",
        "url": "https://huggingface.co/edgetools/ddcolor/resolve/main/ddcolor-tiny-fp16.onnx",
        "input_size": 512,
        "default": True,
    },
    "ddcolor-large": {
        "name": "DDColor-L 512 (Photorealistic Detail)",
        "file": "ddcolor-512-fp16.onnx",
        "url": "https://huggingface.co/Diogo122333/ddcolor-512-fp16/resolve/main/ddcolor-512-fp16.onnx",
        "input_size": 512,
        "default": False,
    }
}


def get_ffmpeg_path():
    """Locate bundled or system ffmpeg executable."""
    bundled_win = os.path.join(TOOLS_DIR, "ffmpeg.exe")
    bundled_unix = os.path.join(TOOLS_DIR, "ffmpeg")
    if os.path.isfile(bundled_win) and os.access(bundled_win, os.X_OK):
        return bundled_win
    if os.path.isfile(bundled_unix) and os.access(bundled_unix, os.X_OK):
        return bundled_unix
    # Check PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    return "ffmpeg"


def detect_acceleration():
    """Detect available ONNX Runtime acceleration providers."""
    logger.info("dolce_engine.py: detect_acceleration()...")
    available = ort.get_available_providers()
    logger.info(f"dolce_engine.py: available providers = {available}")
    if "DmlExecutionProvider" in available:
        return ["DmlExecutionProvider", "CPUExecutionProvider"], "DirectML (GPU Acceleration)"
    if "CoreMLExecutionProvider" in available:
        return ["CoreMLExecutionProvider", "CPUExecutionProvider"], "CoreML (Apple Neural Engine)"
    if "CUDAExecutionProvider" in available:
        return ["CUDAExecutionProvider", "CPUExecutionProvider"], "NVIDIA CUDA"
    return ["CPUExecutionProvider"], "CPU (Multi-Core AVX Optimized)"


logger.info("dolce_engine.py: calling detect_acceleration()...")
PROVIDERS, PROVIDER_LABEL = detect_acceleration()
logger.info(f"dolce_engine.py: acceleration configured: {PROVIDER_LABEL}")


class DolceEngine:
    def __init__(self, models_dir=MODELS_DIR):
        self.models_dir = models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        self.sessions = {}
        self.ffmpeg_path = get_ffmpeg_path()
        self.last_cache = {
            "orig_bgr": None,
            "orig_rgb": None,
            "raw_color_bgr": None,
            "adjusted_bgr": None
        }

    def ensure_model(self, model_key="ddcolor-tiny", progress_callback=None):
        """Ensure model weights exist, downloading if necessary."""
        if model_key not in AVAILABLE_MODELS:
            model_key = "ddcolor-tiny"

        model_info = AVAILABLE_MODELS[model_key]
        dest_path = os.path.join(self.models_dir, model_info["file"])

        if not os.path.isfile(dest_path) or os.path.getsize(dest_path) < 1000:
            import urllib.request
            if progress_callback:
                progress_callback(0.05, f"Downloading {model_info['name']} weights...")
            
            def reporthook(block_num, block_size, total_size):
                if total_size > 0 and progress_callback and block_num % 50 == 0:
                    pct = min(1.0, (block_num * block_size) / total_size)
                    progress_callback(0.05 + 0.85 * pct, f"Downloading {model_info['name']} ({int(pct*100)}%)...")

            urllib.request.urlretrieve(model_info["url"], dest_path, reporthook=reporthook)

        return dest_path, model_info["input_size"]

    def get_session(self, model_key="ddcolor-tiny", progress_callback=None):
        """Get or initialize an ONNX Runtime inference session."""
        if model_key in self.sessions:
            return self.sessions[model_key]

        model_path, input_size = self.ensure_model(model_key, progress_callback)
        
        opts = ort.SessionOptions()
        opts.log_severity_level = 3
        opts.enable_mem_pattern = True
        opts.intra_op_num_threads = max(1, os.cpu_count() or 4)

        # Attempt with hardware accelerator first, fallback cleanly to CPU
        session = None
        for prov in [PROVIDERS, ["CPUExecutionProvider"]]:
            try:
                session = ort.InferenceSession(model_path, opts, providers=prov)
                break
            except Exception as e:
                print(f"[DolceEngine] Warning: Provider {prov} init failed: {e}")
                continue

        if session is None:
            raise RuntimeError(f"Failed to load ONNX model with any provider.")

        active_provider = session.get_providers()[0]
        if active_provider == "DmlExecutionProvider":
            active_label = "DirectML (GPU Acceleration)"
        elif active_provider == "CoreMLExecutionProvider":
            active_label = "CoreML (Apple Neural Engine)"
        elif active_provider == "CUDAExecutionProvider":
            active_label = "NVIDIA CUDA"
        else:
            active_label = "CPU (Multi-Core AVX Optimized)"

        self.sessions[model_key] = (session, input_size, active_label)
        return self.sessions[model_key]

    @staticmethod
    def apply_adjustments(img_rgb: np.ndarray, saturation: float = 1.0, contrast: float = 1.0, brightness: float = 0.0, temperature: int = 0) -> np.ndarray:
        """
        Ultra-fast real-time color grading (Saturation, Contrast, Brightness, Color Temperature).
        Executed in < 5ms on a 4K frame.
        """
        if img_rgb is None:
            return None
        res = img_rgb.astype(np.float32)

        # Color Temperature: shift Red warmer and Blue cooler
        if temperature != 0:
            res[:, :, 0] = np.clip(res[:, :, 0] + temperature, 0, 255)
            res[:, :, 2] = np.clip(res[:, :, 2] - temperature, 0, 255)

        # Contrast & Brightness
        if contrast != 1.0 or brightness != 0.0:
            res = np.clip((res - 128.0) * contrast + 128.0 + brightness, 0, 255)

        # Saturation in HSV space
        if saturation != 1.0:
            hsv = cv2.cvtColor(res.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation, 0, 255)
            res = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)

        return np.clip(res, 0, 255).astype(np.uint8)

    @staticmethod
    def make_split_comparison(orig_rgb: np.ndarray, color_rgb: np.ndarray, divider_pct: float = 0.5) -> np.ndarray:
        """Create a side-by-side or split comparison image with crisp labeling."""
        if orig_rgb is None or color_rgb is None:
            return None
        h, w = orig_rgb.shape[:2]
        if color_rgb.shape[:2] != (h, w):
            color_rgb = cv2.resize(color_rgb, (w, h))

        divider_x = int(w * divider_pct)
        split = np.empty_like(orig_rgb)
        split[:, :divider_x] = orig_rgb[:, :divider_x]
        split[:, divider_x:] = color_rgb[:, divider_x:]

        # Divider bar
        div_w = max(2, int(w * 0.003))
        x1 = max(0, divider_x - div_w // 2)
        x2 = min(w, divider_x + div_w // 2)
        split[:, x1:x2] = [255, 255, 255]

        # Subtle labels
        scale = max(0.4, min(1.0, w / 800.0))
        thickness = max(1, int(scale * 2))
        cv2.putText(split, "B&W ORIGINAL", (16, int(30 * scale) + 10), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(split, "B&W ORIGINAL", (16, int(30 * scale) + 10), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), thickness, cv2.LINE_AA)

        color_x = min(w - 180, divider_x + 16)
        cv2.putText(split, "DOLCE COLORE", (color_x, int(30 * scale) + 10), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
        cv2.putText(split, "DOLCE COLORE", (color_x, int(30 * scale) + 10), cv2.FONT_HERSHEY_SIMPLEX, scale, (255, 255, 255), thickness, cv2.LINE_AA)
        return split

    def colorize_frame_raw(self, img_bgr: np.ndarray, model_key="ddcolor-tiny", session_tuple=None) -> np.ndarray:
        """
        Colorize a single BGR frame using ONNX Runtime.
        Returns the raw colorized BGR frame without user tuning adjustments.
        """
        if session_tuple is None:
            session_tuple = self.get_session(model_key)
        session = session_tuple[0]
        input_size = session_tuple[1]

        h, w = img_bgr.shape[:2]

        # 1. Convert to float Lab space and extract original full-resolution L channel
        img_norm = (img_bgr / 255.0).astype(np.float32)
        orig_l = cv2.cvtColor(img_norm, cv2.COLOR_BGR2Lab)[:, :, :1]

        # 2. Prepare resized input tensor in gray-RGB space
        img_resized = cv2.resize(img_norm, (input_size, input_size))
        img_l_resized = cv2.cvtColor(img_resized, cv2.COLOR_BGR2Lab)[:, :, :1]
        img_gray_lab = np.concatenate((img_l_resized, np.zeros_like(img_l_resized), np.zeros_like(img_l_resized)), axis=-1)
        img_gray_rgb = cv2.cvtColor(img_gray_lab, cv2.COLOR_LAB2RGB)

        tensor_in = img_gray_rgb.transpose((2, 0, 1))[np.newaxis, ...].astype(np.float32)

        # 3. ONNX inference -> outputs predicted ab chrominance (1, 2, input_size, input_size)
        input_name = session.get_inputs()[0].name
        outputs = session.run(None, {input_name: tensor_in})
        output_ab = outputs[0][0]  # shape: (2, H_in, W_in)

        # 4. Upsample ab chrominance back to full original resolution
        ab_resized = cv2.resize(output_ab.transpose((1, 2, 0)), (w, h), interpolation=cv2.INTER_LINEAR)

        # 5. Concatenate original L with predicted ab and convert back to BGR
        output_lab = np.concatenate((orig_l, ab_resized), axis=-1)
        output_bgr = cv2.cvtColor(output_lab, cv2.COLOR_LAB2BGR)
        output_img = np.clip(output_bgr * 255.0, 0, 255).astype(np.uint8)
        return output_img

    def colorize_image(
        self,
        img_bgr: np.ndarray,
        model_key: str = "ddcolor-tiny",
        saturation: float = 1.0,
        contrast: float = 1.0,
        brightness: float = 0.0,
        temperature: int = 0,
        progress_callback=None
    ):
        """Full image colorization workflow with cache and tuning."""
        if img_bgr is None:
            raise ValueError("Invalid image input")

        t0 = time.time()
        if progress_callback:
            progress_callback(0.2, "Neural chrominance prediction...")

        raw_bgr = self.colorize_frame_raw(img_bgr, model_key=model_key)
        raw_rgb = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2RGB)
        orig_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # Cache for real-time instantaneous tuning
        self.last_cache["orig_bgr"] = img_bgr
        self.last_cache["orig_rgb"] = orig_rgb
        self.last_cache["raw_color_bgr"] = raw_bgr

        if progress_callback:
            progress_callback(0.8, "Applying historical color grading...")

        adjusted_rgb = self.apply_adjustments(
            raw_rgb,
            saturation=saturation,
            contrast=contrast,
            brightness=brightness,
            temperature=temperature
        )
        self.last_cache["adjusted_bgr"] = cv2.cvtColor(adjusted_rgb, cv2.COLOR_RGB2BGR)

        split_rgb = self.make_split_comparison(orig_rgb, adjusted_rgb)
        elapsed_ms = (time.time() - t0) * 1000

        return {
            "colorized_rgb": adjusted_rgb,
            "split_rgb": split_rgb,
            "elapsed_ms": round(elapsed_ms, 1),
            "width": img_bgr.shape[1],
            "height": img_bgr.shape[0],
            "hardware": self.sessions.get(model_key, (None, None, PROVIDER_LABEL))[2],
        }

    def quick_tune_cache(self, saturation=1.0, contrast=1.0, brightness=0.0, temperature=0):
        """Instant (< 5ms) re-grading of cached raw colorized image."""
        if self.last_cache["raw_color_bgr"] is None:
            return None
        raw_rgb = cv2.cvtColor(self.last_cache["raw_color_bgr"], cv2.COLOR_BGR2RGB)
        adjusted_rgb = self.apply_adjustments(
            raw_rgb,
            saturation=float(saturation),
            contrast=float(contrast),
            brightness=float(brightness),
            temperature=int(temperature)
        )
        split_rgb = self.make_split_comparison(self.last_cache["orig_rgb"], adjusted_rgb)
        return {
            "colorized_rgb": adjusted_rgb,
            "split_rgb": split_rgb
        }

    def colorize_video(
        self,
        video_path: str,
        output_path: str,
        model_key: str = "ddcolor-tiny",
        mode: str = "preview-5s",
        custom_duration: float = 5.0,
        resolution_mode: str = "original",
        side_by_side: bool = False,
        saturation: float = 1.0,
        contrast: float = 1.0,
        brightness: float = 0.0,
        temperature: int = 0,
        progress_callback=None
    ):
        """
        High-throughput video colorizer using FFmpeg piping and audio remuxing.
        """
        if not os.path.isfile(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        session_tuple = self.get_session(model_key)
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

        # Calculate max frames based on mode
        if mode == "preview-5s":
            max_frames = min(total_frames or 120, max(1, int(5 * fps)))
        elif mode == "preview-10s":
            max_frames = min(total_frames or 240, max(1, int(10 * fps)))
        elif mode == "custom":
            max_frames = min(total_frames or 99999, max(1, int(custom_duration * fps)))
        else:  # "full"
            max_frames = total_frames if total_frames > 0 else 999999

        target_w, target_h = src_w, src_h
        if resolution_mode == "720p" and src_h > 720:
            target_h = 720
            target_w = int((src_w * (720.0 / src_h)) // 2 * 2)
        elif resolution_mode == "480p" and src_h > 480:
            target_h = 480
            target_w = int((src_w * (480.0 / src_h)) // 2 * 2)

        out_w = (target_w * 2) if side_by_side else target_w
        out_h = target_h

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        cmd = [
            self.ffmpeg_path, "-y",
            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{out_w}x{out_h}", "-r", str(fps),
            "-i", "-",
            "-i", video_path,
            "-map", "0:v:0", "-map", "1:a:0?",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest",
            output_path
        ]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        frame_idx = 0
        t_start = time.time()

        try:
            while frame_idx < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                if (target_w, target_h) != (src_w, src_h):
                    frame = cv2.resize(frame, (target_w, target_h))

                colored = self.colorize_frame_raw(frame, session_tuple=session_tuple)

                if saturation != 1.0 or contrast != 1.0 or brightness != 0.0 or temperature != 0:
                    colored_rgb = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
                    colored_rgb = self.apply_adjustments(colored_rgb, saturation, contrast, brightness, temperature)
                    colored = cv2.cvtColor(colored_rgb, cv2.COLOR_BGR2RGB)

                frame_pipe = np.hstack([frame, colored]) if side_by_side else colored
                proc.stdin.write(frame_pipe.tobytes())
                frame_idx += 1

                if progress_callback and (frame_idx % 2 == 0 or frame_idx == max_frames):
                    elapsed = max(0.001, time.time() - t_start)
                    fps_rate = frame_idx / elapsed
                    remaining = max_frames - frame_idx
                    eta_s = remaining / max(0.001, fps_rate)
                    pct = frame_idx / max_frames
                    progress_callback(pct, {
                        "frame": frame_idx,
                        "total": max_frames,
                        "fps": round(fps_rate, 1),
                        "eta_s": round(eta_s, 1),
                        "elapsed_s": round(elapsed, 1)
                    })
        finally:
            cap.release()
            proc.stdin.close()
            proc.wait()

        if proc.returncode != 0 or not os.path.exists(output_path):
            raise RuntimeError("FFmpeg video encoding failed.")

        return {
            "frames_processed": frame_idx,
            "total_time_s": round(time.time() - t_start, 2),
            "avg_fps": round(frame_idx / max(0.001, time.time() - t_start), 1),
            "output_path": output_path
        }
