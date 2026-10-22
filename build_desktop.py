"""
Dolce Colore - Desktop Packaging Script
Builds the React frontend and compiles a standalone, terminal-free Windows .exe and macOS app bundle.
"""

import os
import sys
import shutil
import subprocess

_ROOT = os.path.dirname(os.path.abspath(__file__))


def run(cmd, cwd=_ROOT):
    print(f"\n[EXEC] {cmd} (cwd={cwd})")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if res.returncode != 0:
        print(f"Command failed with code {res.returncode}")
        sys.exit(res.returncode)


def main():
    print("==================================================")
    print("   [Dolce Colore] Standalone Desktop Builder      ")
    print("==================================================")

    # 1. Build React/Vite Frontend
    frontend_dir = os.path.join(_ROOT, "frontend")
    print("\n[1/3] Building React/Vite frontend distribution...")
    run("npm run build", cwd=frontend_dir)

    dist_html = os.path.join(frontend_dir, "dist", "index.html")
    if not os.path.isfile(dist_html):
        print("Error: frontend/dist/index.html was not generated.")
        sys.exit(1)
    print("SUCCESS: Frontend successfully compiled to frontend/dist!")

    # 2. Package with PyInstaller
    print("\n[2/3] Compiling standalone executable with PyInstaller...")

    # Find pywebview lib directory
    import webview
    webview_lib_dir = os.path.join(os.path.dirname(webview.__file__), "lib")

    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "DolceColore",
        "--noconsole",
        "--icon", os.path.join(_ROOT, "icon.ico"),
        "--add-data", f"{os.path.join(_ROOT, 'frontend', 'dist')}{os.pathsep}frontend/dist",
        "--add-data", f"{os.path.join(_ROOT, 'models')}{os.pathsep}models",
        "--add-data", f"{os.path.join(_ROOT, 'tools')}{os.pathsep}tools",
        "--add-data", f"{os.path.join(_ROOT, 'icon.png')}{os.pathsep}.",
        "--add-data", f"{os.path.join(_ROOT, 'icon.ico')}{os.pathsep}.",
        "--add-data", f"{webview_lib_dir}{os.pathsep}webview/lib",
        "--hidden-import", "server",
        "--hidden-import", "dolce_engine",
        "--hidden-import", "ai_vision",
        "--hidden-import", "cv2",
        "--hidden-import", "numpy",
        "--hidden-import", "PIL",
        "--hidden-import", "fastapi",
        "--hidden-import", "starlette",
        "--hidden-import", "uvicorn",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "clr",
        "--hidden-import", "pythonnet",
        "--hidden-import", "clr_loader",
        "--hidden-import", "webview.platforms.winforms",
        "--hidden-import", "webview.platforms.edgechromium",
        "--collect-all", "onnxruntime",
        "--collect-all", "pywebview",
        "--collect-all", "pythonnet",
        "--collect-all", "clr_loader",
        "--collect-all", "fastapi",
        "--collect-all", "starlette",
        "--noconfirm",
        os.path.join(_ROOT, "desktop.py")
    ]

    run(" ".join(f'"{arg}"' if " " in arg else arg for arg in pyinstaller_cmd))

    dist_dir = os.path.join(_ROOT, "dist", "DolceColore")
    internal_dir = os.path.join(dist_dir, "_internal")

    # Post-process: ensure interop DLLs are copied directly to dist_dir and _internal
    if os.path.isdir(webview_lib_dir):
        print("\nDeploying webview interop DLLs...")
        for item in os.listdir(webview_lib_dir):
            src_item = os.path.join(webview_lib_dir, item)
            dst_root = os.path.join(dist_dir, item)
            dst_internal = os.path.join(internal_dir, item)
            if os.path.isfile(src_item):
                shutil.copy2(src_item, dst_root)
                shutil.copy2(src_item, dst_internal)
            elif os.path.isdir(src_item):
                if not os.path.exists(dst_root):
                    shutil.copytree(src_item, dst_root)
                if not os.path.exists(dst_internal):
                    shutil.copytree(src_item, dst_internal)

    # Also copy icon.png and icon.ico directly to dist/DolceColore
    shutil.copy2(os.path.join(_ROOT, "icon.png"), os.path.join(dist_dir, "icon.png"))
    shutil.copy2(os.path.join(_ROOT, "icon.ico"), os.path.join(dist_dir, "icon.ico"))

    out_exe = os.path.join(dist_dir, "DolceColore.exe")
    if os.path.isfile(out_exe):
        print(f"\nSUCCESS: Standalone build complete: {out_exe}")
    else:
        print("\nBuild completed in dist/DolceColore.")

    # 3. Compile Inno Setup installer if available
    iscc = shutil.which("iscc") or r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if os.path.isfile(iscc):
        print("\n[3/3] Compiling Windows Setup Installer with Inno Setup...")
        iss_path = os.path.join(_ROOT, "installer", "dolce_colore.iss")
        run(f'"{iscc}" "{iss_path}"')
        print("SUCCESS: Windows Setup Installer generated in dist-installer/!")
    else:
        print("\n[Note] Inno Setup compiler (ISCC.exe) not found on PATH. dist/DolceColore is ready for portable distribution or zip packaging.")


if __name__ == "__main__":
    main()
