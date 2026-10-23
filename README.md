# 🎨 Dolce Colore

**1-Click Historical Photo & Video Colorizer — 100% Private, Local AI Neural Restoration.**

A standalone, double-clickable native desktop application for Windows and macOS. Completely eliminates the need for Pinokio, Python virtual environments, or terminal commands.

Powered by **ONNX Runtime** and [DDColor](https://github.com/piddnad/DDColor) (ICCV 2023), Dolce Colore restores authentic, period-accurate color to black-and-white photographs and archival films. Runs 100% offline on standard CPUs, Intel Iris/Arc graphics, Apple Silicon, or NVIDIA GPUs with zero telemetry and zero cloud dependencies.

---

## ✨ Features

- 🖼️ **Photo Studio (Instant Neural Restoration)**:
  - **Interactive Side-by-Side Split Slider**: Drag between the monochrome original and the colorized restoration in real time.
  - **Live 60 FPS Color Grading**: Tune Saturation (vibrancy), Contrast, Color Temperature (cool blue ← → warm amber), and Exposure Bias with instant feedback.
  - **1-Click High-Res PNG Export & Clipboard Copy**: Save uncompressed restorations directly to your disk or clipboard.
  - **Built-in Archival Classics**: Instant 1-click loading for Audrey Hepburn, Charlie Chaplin & Helen Keller (1919), Louis Armstrong (1946), 1930s New York, and London 1945.

- 🤖 **Historical AI Vision Guidance (Optional)**:
  - Connect a free **Google Gemini** API key (or OpenAI / Claude / OpenRouter) to act as a historical researcher.
  - Inspects the monochrome scene to identify the authentic era (*1910s Pre-WWI*, *1920s Roaring 20s*, *1940s WWII*), architectural materials, and period fabric dyes.
  - **Interactive Period Dye Swatches**: Displays authentic pigments (e.g., Prussian Blue, Alizarin Crimson, Chrome Yellow) with hex codes and historical provenance.
  - **AI Colorist Critique**: Evaluates skin tones and color balance, recommending 1-click grading adjustments.
  - 100% optional: Works completely offline when no API key is provided.

- 🎬 **Cinema Video Colorizer**:
  - Colorize classic public domain movies frame-by-frame with H.264 video encoding.
  - **Automatic Audio Preservation**: Synchronizes and muxes the original audio track back into the colorized MP4.
  - **Preview Snippet Modes**: Test the first 5 or 10 seconds or custom durations to verify color grading in seconds before processing a full movie.
  - **Performance Downscaling**: Optional 720p or 480p downscaling for dramatic speedups on standard laptops and Intel graphics.
  - **Side-by-Side Split Video Mode**: Generates split-screen videos (original B&W on left, colorized on right) for demonstration reels.
  - Live throughput telemetry: FPS speed, frame progress bar, elapsed time, and ETA.

- 📁 **Batch Archival Queue**:
  - Drop full archival scans, photo albums, or glass-plate negatives for automated batch colorization.
  - Visual gallery of restored images and 1-click downloads.

- ⚡ **Lightweight ONNX Runtime Engine (Zero PyTorch Bloat)**:
  - Model weights shrunken from 4.5 GB down to ~130 MB.
  - Hardware acceleration via **DirectML** on Windows, **CoreML** on Apple Silicon, and multi-core AVX on CPU.
  - Bundled static FFmpeg binary included out of the box.

---

## 🚀 Running the Desktop App

### Double-Click Native Desktop Mode
Double-click `dist/DolceColore/DolceColore.exe` (or run `python desktop.py` in your development environment).

A native desktop window opens immediately—no command prompt, no terminal window, no browser tab.

```bash
# Development runner:
python desktop.py

# Or run in headless/browser mode:
python desktop.py --web-only
```

---

## 🛠️ Building Standalone Installers

### 1. Build the Complete Executable Bundle
To compile the React frontend and bundle the standalone `DolceColore.exe`:

```bash
python build_desktop.py
```

The output will be placed in `dist/DolceColore/DolceColore.exe`.

### 2. Windows Installer (Inno Setup)
An Inno Setup script is provided in `installer/dolce_colore.iss`. To compile the single-file setup installer:

```bash
iscc installer/dolce_colore.iss
```
This generates `dist-installer/DolceColore_Setup_v<version>.exe` with desktop icon, start menu shortcut, and clean uninstaller.

---

## 🏛️ Public Domain Archives for Vintage Media

- **[Internet Archive: Prelinger Archives](https://archive.org/details/prelinger)**: Over 17,000 vintage educational, industrial, and advertising films.
- **[Library of Congress National Screening Room](https://www.loc.gov/collections/national-screening-room/)**: Historic American short films and newsreels.
- **[Wikimedia Commons Public Domain Media](https://commons.wikimedia.org/wiki/Category:Public_domain_videos)**: Silent classics, speeches, and scientific footage.
- **[PublicDomainMovies.net](https://publicdomainmovies.net/)**: Classic silent comedies, westerns, and early noir.

---

## 📄 License

Dolce Colore is proprietary software of Revisited Labs. Personal and archival use is free; Pro features are unlocked with a license key. See [LICENSE](LICENSE) for the terms.

It builds on open-source components, including the DDColor model (Apache 2.0) and FFmpeg. Their licenses and credits are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
