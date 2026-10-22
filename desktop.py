"""
Dolce Colore - Standalone Native Desktop Application
Double-clickable, terminal-free desktop runner with PyWebView and FastAPI.
"""

import os
import sys
import time
import socket
import threading
import uvicorn
import webview

_ROOT = os.path.dirname(os.path.abspath(__file__))


def find_free_port(default_port=49221):
    """Find an available localhost port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", default_port))
            return default_port
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


def start_api_server(port):
    """Run FastAPI uvicorn server in a background daemon thread."""
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
        access_log=False
    )


def wait_for_server(port, timeout=10.0):
    """Poll localhost until API responds."""
    start_t = time.time()
    while time.time() - start_t < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def main():
    port = find_free_port()
    server_thread = threading.Thread(target=start_api_server, args=(port,), daemon=True)
    server_thread.start()

    if not wait_for_server(port):
        print(f"Failed to start local server on port {port}")
        sys.exit(1)

    url = f"http://127.0.0.1:{port}"

    # Check for --web-only or --headless flag
    if "--web-only" in sys.argv:
        print(f"Dolce Colore running in web-only mode at {url}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)

    # Launch Native PyWebView Desktop Window
    icon_path = os.path.join(_ROOT, "icon.png")
    window = webview.create_window(
        title="Dolce Colore — 1-Click Historical Photo & Video Colorizer",
        url=url,
        width=1280,
        height=840,
        min_size=(1024, 680),
        background_color="#0b0f19",
        text_select=False
    )

    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
