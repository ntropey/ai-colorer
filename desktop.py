"""
Dolce Colore - Standalone Native Desktop Application
Double-clickable, terminal-free desktop runner with PyWebView, FastAPI, and DirectML acceleration.
"""

import os
import sys
import multiprocessing

# Critical for PyInstaller frozen executables on Windows
if __name__ == "__main__":
    multiprocessing.freeze_support()

import time
import socket
import threading
import logging
import traceback
import ctypes
import subprocess
import shutil

# 1. Setup persistent auto-flushing file logging (append mode so subprocesses don't wipe it)
LOG_DIR = os.path.join(os.path.expanduser("~"), ".dolce_colore")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "desktop.log")


class AutoFlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()


logger = logging.getLogger("DolceColore")
logger.setLevel(logging.DEBUG)
handler = AutoFlushFileHandler(LOG_FILE, mode="a", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] [PID:%(process)d] %(message)s"))
logger.addHandler(handler)
logger.propagate = False  # Isolate from uvicorn's root logging config

logger.info(f"=== Starting Dolce Colore (sys.frozen={getattr(sys, 'frozen', False)}, PID={os.getpid()}) ===")

# Handle PyInstaller bundle root
if getattr(sys, "frozen", False):
    _ROOT = sys._MEIPASS
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
else:
    _ROOT = os.path.dirname(os.path.abspath(__file__))

logger.info(f"Root path: {_ROOT}")
logger.info(f"Executable path: {sys.executable}")


# 2. Critical PyInstaller Fix: Monkey-patch webview.util.interop_dll_path
# PyInstaller onedir mode stores pure python modules in base_library.zip,
# which causes pywebview's default DLL finder to fail and crash WebView2 silently.
try:
    import webview.util
    _orig_interop_dll_path = webview.util.interop_dll_path

    def _patched_interop_dll_path(dll_name: str) -> str:
        try:
            return _orig_interop_dll_path(dll_name)
        except Exception:
            pass

        search_roots = [_ROOT, os.path.dirname(sys.executable)]
        for base in search_roots:
            if not os.path.exists(base):
                continue
            direct = os.path.join(base, dll_name)
            if os.path.exists(direct):
                return direct
            for root, dirs, files in os.walk(base):
                if dll_name in files:
                    return os.path.join(root, dll_name)
                if dll_name in dirs:
                    return os.path.join(root, dll_name)

        raise FileNotFoundError(f"Cannot find interop DLL or folder: {dll_name}")

    webview.util.interop_dll_path = _patched_interop_dll_path
    logger.info("Successfully patched webview.util.interop_dll_path for PyInstaller bundle")
except Exception as e:
    logger.warning(f"Could not patch webview.util: {e}")


# 3. Import Application Modules step-by-step with explicit logging
try:
    logger.info("Importing server module...")
    import server
    logger.info("Importing uvicorn module...")
    import uvicorn
    logger.info("Importing webview module...")
    import webview
    logger.info("All primary modules imported successfully!")
except BaseException as e:
    err_msg = f"Fatal error during imports:\n{traceback.format_exc()}"
    logger.error(err_msg)
    if sys.platform == "win32":
        ctypes.windll.user32.MessageBoxW(0, err_msg, "Dolce Colore Startup Error", 0x10)
    sys.exit(1)


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
    """Run FastAPI uvicorn server with isolated logging config."""
    try:
        config = uvicorn.Config(
            server.app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
            log_config=None
        )
        server_instance = uvicorn.Server(config)
        server_instance.run()
    except Exception as e:
        logger.error(f"Uvicorn server crashed: {traceback.format_exc()}")


def wait_for_server(port, timeout=12.0):
    """Poll localhost until API responds."""
    start_t = time.time()
    while time.time() - start_t < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def launch_edge_app_mode(url):
    """Fallback: Launch chromeless Edge App window if WebView2 fails."""
    logger.info(f"Attempting fallback chromeless Edge App launch for {url}")
    edge_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        shutil.which("msedge"),
    ]
    msedge = None
    for p in edge_paths:
        if p and os.path.isfile(p):
            msedge = p
            break

    if not msedge:
        logger.error("Microsoft Edge not found for app-mode fallback.")
        return False

    cmd = [
        msedge,
        f"--app={url}",
        "--window-size=1280,840",
        "--hide-scrollbars",
        f"--user-data-dir={os.path.join(LOG_DIR, 'edge_profile')}"
    ]
    logger.info(f"Launching Edge app mode: {' '.join(cmd)}")
    proc = subprocess.Popen(cmd)
    proc.wait()
    return True


def main():
    try:
        port = find_free_port()
        logger.info(f"Binding API server to port {port}")

        server_thread = threading.Thread(target=start_api_server, args=(port,), daemon=True)
        server_thread.start()

        logger.info("Waiting for API server to become ready...")
        if not wait_for_server(port):
            msg = f"API server failed to respond on port {port} within timeout."
            logger.error(msg)
            if sys.platform == "win32":
                ctypes.windll.user32.MessageBoxW(0, msg, "Dolce Colore Error", 0x10)
            sys.exit(1)

        url = f"http://127.0.0.1:{port}"
        logger.info(f"Server is ready and verified responsive at {url}")

        if "--web-only" in sys.argv:
            logger.info("Running in web-only mode")
            print(f"Dolce Colore running at {url}")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                sys.exit(0)

        # Native Desktop Window via PyWebView
        icon_path = os.path.join(_ROOT, "icon.png")
        if not os.path.isfile(icon_path):
            icon_path = os.path.join(os.path.dirname(sys.executable), "icon.png")
            if not os.path.isfile(icon_path):
                icon_path = None

        storage_path = os.path.join(LOG_DIR, "webview_profile")
        os.makedirs(storage_path, exist_ok=True)

        logger.info(f"Creating native PyWebView window (icon={icon_path}, storage={storage_path})")
        wv_logger = logging.getLogger("pywebview")
        wv_logger.setLevel(logging.INFO)
        wv_logger.addHandler(handler)

        window = webview.create_window(
            title="Dolce Colore — 1-Click Historical Photo & Video Colorizer",
            url=url,
            width=1280,
            height=840,
            min_size=(1024, 680),
            background_color="#0b0f19",
            text_select=False
        )
        window.events.shown += lambda: logger.info(">>> PyWebView Window is SHOWN on screen! <<<")
        window.events.loaded += lambda: logger.info(">>> PyWebView DOM loaded successfully! <<<")

        logger.info("Starting webview event loop...")
        try:
            webview.start(
                debug="--debug" in sys.argv,
                private_mode=False,
                storage_path=storage_path
            )
            logger.info("PyWebView event loop terminated normally. Exiting.")
        except Exception as wv_err:
            logger.error(f"PyWebView failed to open window: {traceback.format_exc()}")
            logger.info("Engaging chromeless Edge App mode fallback...")
            if not launch_edge_app_mode(url):
                raise wv_err

    except BaseException as e:
        err_msg = f"Unhandled exception in main:\n{traceback.format_exc()}"
        logger.error(err_msg)
        if sys.platform == "win32":
            ctypes.windll.user32.MessageBoxW(0, err_msg, "Dolce Colore Error", 0x10)
        sys.exit(1)


if __name__ == "__main__":
    main()
