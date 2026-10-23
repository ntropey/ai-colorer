# Third-Party Notices

Dolce Colore is proprietary software of Revisited Labs, released under the terms in
[LICENSE](LICENSE). It includes and builds on the open-source components listed below, each of
which remains under its own license. Nothing here changes those licenses.

## Colorization model

| Component | License | Source |
|---|---|---|
| **DDColor** (model architecture and "tiny" weights, exported to ONNX) | Apache License 2.0 | https://github.com/piddnad/DDColor |
| ONNX export used by this app (`ddcolor-tiny-fp16.onnx`) | Apache License 2.0, inherited from DDColor | https://huggingface.co/edgetools/ddcolor |

DDColor: *Towards Photo-Realistic Image Colorization via Dual Decoders*, Kang et al., ICCV 2023.
Licensed under the Apache License, Version 2.0 (https://www.apache.org/licenses/LICENSE-2.0).
The model files are redistributed unmodified apart from the ONNX conversion and precision
reduction described above.

## Video encoding: FFmpeg

Video colorization uses **FFmpeg** (https://ffmpeg.org), run as a separate program, to read and
write video and to keep the original audio. FFmpeg is licensed under the **LGPL v2.1 or later**,
or the **GPL v2 or later** depending on how a given build was configured. Builds that include
encoders such as x264 are GPL.

- The FFmpeg source code is available at https://ffmpeg.org/download.html.
- The macOS app bundles the FFmpeg build installed by Homebrew on the release machine. On
  request, Revisited Labs will provide the corresponding source for the exact build included
  in a release: support@revisitedlabs.com.
- The Windows app does not include FFmpeg. Setup checks for an FFmpeg already installed on the
  computer and links to the download page if there isn't one; the app then uses that copy.
- FFmpeg runs as its own executable, separate from the Dolce Colore application code.

## Python components (bundled into the desktop app)

| Component | License |
|---|---|
| FastAPI | MIT |
| Uvicorn | BSD 3-Clause |
| python-multipart | Apache 2.0 |
| pywebview | BSD 3-Clause |
| Pillow | HPND (MIT-CMU style) |
| NumPy | BSD 3-Clause |
| OpenCV (`opencv-python-headless`) | Apache 2.0 (OpenCV); the wheel also ships FFmpeg libraries under the LGPL 2.1 |
| ONNX Runtime | MIT |
| PyInstaller (used to package the app) | GPL 2.0 with a bootloader exception that allows distributing the resulting app under any license |

## Interface components (bundled into the app's window)

| Component | License |
|---|---|
| React, React DOM | MIT |
| Tailwind CSS | MIT |
| Lucide icons (`lucide-react`) | ISC |
| canvas-confetti | ISC |

## Updating this file

Run through this list when dependencies change (`requirements.txt`, `frontend/package.json`,
or the FFmpeg source used by the release workflow), and confirm each license against the
package's own metadata before a release.
