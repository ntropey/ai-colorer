module.exports = {
  requires: {
    bundle: "ai"
  },
  run: [
    // Vendor the DDColor model/inference code as the app logic.
    {
      method: "shell.run",
      params: {
        message: [
          "git clone https://github.com/piddnad/DDColor app"
        ]
      }
    },
    // ffmpeg is used to mux audio + re-encode colorized frames into a playable video.
    {
      method: "shell.run",
      params: {
        message: "conda install -y -c conda-forge ffmpeg"
      }
    },
    // Inference-only deps (skip the training-only extras in DDColor's own requirements.txt)
    {
      method: "shell.run",
      params: {
        venv: "env",
        path: "app",
        message: [
          "uv pip install gradio opencv-python==4.7.0.72 numpy==1.24.3 pillow tqdm huggingface-hub sympy networkx"
        ]
      }
    },
    // torch.js auto-detects gpu/platform and falls back to CPU (no Nvidia required)
    {
      method: "script.start",
      params: {
        uri: "torch.js",
        params: {
          venv: "env",
          path: "app"
        }
      }
    }
  ]
}
