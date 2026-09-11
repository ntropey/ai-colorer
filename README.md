# 🎨 Dolce Colore

Locally colorize black-and-white public domain movies and historical photos using
[DDColor](https://github.com/piddnad/DDColor) (ICCV 2023), a state-of-the-art neural
colorization architecture. Runs 100% locally on your computer — no Nvidia GPU, no
high-powered graphics card, and no paid cloud API required. Optimized to run on standard
CPUs and Intel integrated graphics out of the box, with automatic GPU acceleration (NVIDIA CUDA,
Apple Silicon MPS, or Intel XPU) when detected.

---

## ✨ Features

- 🖼️ **Single Photo Restoration**:
  - Neural colorization with real-time **Side-by-Side Comparison** tab.
  - **Instant Color Tuning**: Fine-tune Saturation (vibrancy), Contrast, and Color Temperature (cool blue ← → warm amber) and apply changes instantly without waiting for neural re-calculation.
  - One-click full-resolution PNG download.
  - Built-in historical archive samples (Audrey Hepburn, Charlie Chaplin & Helen Keller 1919, Louis Armstrong 1946, 1930s New York, etc.).

- 🤖 **Optional AI Vision Historical Guidance**:
  - Connect an optional Vision API key (**Google Gemini** free tier, **OpenAI**, **Anthropic**, or **OpenRouter**) to act as a historical researcher.
  - The AI inspects the monochrome scene, identifies authentic period dyes, military uniforms, and architectural materials, and generates a visual palette with historical notes.
  - **AI Colorist Critique**: One-click review that evaluates skin tones and fine-tunes color warmth and saturation automatically.
  - 100% optional: Works completely offline and local when no key is provided.

- 📁 **Batch Photo Processing**:
  - Drop multiple archival scans or photo albums to colorize them in a single batch.
  - Interactive result gallery and one-click `.zip` bundle download.

- 🎬 **Movie & Video Colorization**:
  - Colorize classic public domain movies frame-by-frame with H.264 video encoding.
  - **AI Keyframe Historical Grading (Optional)**: Analyze the opening frame with a Vision API and, if enabled, automatically apply its recommended saturation/contrast/temperature bias to every rendered frame.
  - **Automatic Audio Preservation**: Synchronizes and muxes the original audio track back in.
  - **Preview Snippet Modes**: Test the first 5 or 10 seconds or custom durations to verify color grading in seconds before processing a feature-length film!
  - **Performance Downscaling**: Optional 720p or 480p downscaling for dramatic speedups on standard laptops and Intel graphics.
  - **Side-by-Side Video Mode**: Generates split-screen videos (original B&W on left, colorized on right) for social media and demonstration reels.
  - Live progress display with FPS throughput and ETA estimates.

- 🧩 **DDColor Model Zoo**:
  - **DDColor-L ModelScope (Default)**: Best overall photorealism for general photos and movies.
  - **DDColor-L Artistic**: Saturated, rich colors with minimal color-bleeding artifacts.
  - **DDColor-T Tiny**: Ultra-lightweight model running ~3× faster, ideal for video and CPU/Intel hardware.
  - **DDColor-Paper**: Original ICCV 2023 research benchmark weights.

---

## 🚀 How to Run with Pinokio

1. Click **Install** from the Pinokio sidebar.
2. Click **Start** to launch the local web server.
3. Click **Open Web UI** to start colorizing movies and photos!

---

## 🏛️ Public Domain Movie & Photo Archives

Looking for vintage movies and photographs to colorize? These public domain archives offer free downloads:
- **[Internet Archive: Prelinger Archives](https://archive.org/details/prelinger)**: Over 17,000 vintage educational, industrial, and advertising films.
- **[Library of Congress National Screening Room](https://www.loc.gov/collections/national-screening-room/)**: Historic American short films and newsreels.
- **[Wikimedia Commons Public Domain Media](https://commons.wikimedia.org/wiki/Category:Public_domain_videos)**: Silent classics, speeches, and scientific footage.
- **[PublicDomainMovies.net](https://publicdomainmovies.net/)**: Classic silent comedies, westerns, and early noir.

---

## 🔌 API Documentation

The web UI is powered by Gradio and exposes `colorize_image` and `colorize_video` as standard API endpoints. Replace `<url>` below with the address shown on the "Open Web UI" tab (e.g. `http://127.0.0.1:7860`).

### Python (`gradio_client`)

```python
from gradio_client import Client, handle_file

client = Client("<url>")

# 1. Colorize Image
result = client.predict(
    img=handle_file("input.jpg"),
    model_name="DDColor-L ModelScope (Best for General Photos & Movies)",
    input_size=512,
    saturation=1.0,
    contrast=1.0,
    temperature=0,
    api_name="/colorize_image"
)
# Returns: [colorized_image_path, side_by_side_path, download_file_path, status_text]
print("Colorized Image:", result[0])

# 2. Colorize Video
video_result = client.predict(
    video_path=handle_file("vintage_clip.mp4"),
    model_name="DDColor-T Tiny (Fast & Lightweight - Recommended for CPU/Intel)",
    input_size=384,
    mode="Preview: First 5 Seconds",
    preview_duration=5,
    video_scale="Original Resolution",
    output_format="Full Colorized Video",
    ai_apply_grading=False,          # set True to auto-analyze the first frame and grade every frame to match
    ai_provider="Google Gemini",
    ai_key="",
    ai_model="gemini-2.0-flash",
    ai_context="",
    api_name="/colorize_video"
)
print("Colorized Video:", video_result[0])
```

### JavaScript (`@gradio/client`)

```javascript
import { Client } from "@gradio/client";

const client = await Client.connect("<url>");

// Image Colorization
const imageResult = await client.predict("/colorize_image", {
  img: await client.uploadFile(imageFile),
  model_name: "DDColor-L ModelScope (Best for General Photos & Movies)",
  input_size: 512,
  saturation: 1.0,
  contrast: 1.0,
  temperature: 0
});
console.log("Colorized image:", imageResult.data[0]);

// Video Colorization
const videoResult = await client.predict("/colorize_video", {
  video_path: await client.uploadFile(videoFile),
  model_name: "DDColor-T Tiny (Fast & Lightweight - Recommended for CPU/Intel)",
  input_size: 384,
  mode: "Preview: First 5 Seconds",
  preview_duration: 5,
  video_scale: "Original Resolution",
  output_format: "Full Colorized Video",
  ai_apply_grading: false, // set true to auto-analyze the first frame and grade every frame to match
  ai_provider: "Google Gemini",
  ai_key: "",
  ai_model: "gemini-2.0-flash",
  ai_context: ""
});
console.log("Colorized video:", videoResult.data[0]);
```

### cURL

Gradio's queued HTTP API uses POST to initiate a job followed by GET to stream the result events:

```sh
# 1. Submit colorization job
curl -X POST "<url>/call/colorize_image" \
  -H "Content-Type: application/json" \
  -d '{"data": [{"path": "/absolute/path/to/input.jpg"}, "DDColor-L ModelScope (Best for General Photos & Movies)", 512, 1.0, 1.0, 0]}'

# 2. Receive the Server-Sent Event stream result
curl -N "<url>/call/colorize_image/<event_id>"
```
