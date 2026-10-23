"""
Dolce Colore - macOS App Bundle and DMG Builder
Builds the React frontend and compiles a standalone, native macOS .app bundle and .dmg.
Supports Apple Silicon (CoreML / Neural Engine) and Intel Macs.
"""

import os
import sys
import shutil
import subprocess

_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
from app_version import __version__


def run(cmd, cwd=_ROOT):
    print(f"\n[EXEC] {cmd} (cwd={cwd})")
    res = subprocess.run(cmd, shell=True, cwd=cwd)
    if res.returncode != 0:
        print(f"Command failed with code {res.returncode}")
        sys.exit(res.returncode)


def main():
    print("==================================================")
    print("   [Dolce Colore] macOS Bundle & DMG Builder      ")
    print("==================================================")

    # 1. Build React/Vite Frontend
    frontend_dir = os.path.join(_ROOT, "frontend")
    print("\n[1/4] Building React/Vite frontend distribution...")
    run("npm run build", cwd=frontend_dir)

    dist_html = os.path.join(frontend_dir, "dist", "index.html")
    if not os.path.isfile(dist_html):
        print("Error: frontend/dist/index.html was not generated.")
        sys.exit(1)
    print("SUCCESS: Frontend successfully compiled to frontend/dist!")

    # 2. Icon setup (icon.icns if present, otherwise icon.png)
    icon_path = os.path.join(_ROOT, "icon.icns")
    if not os.path.isfile(icon_path):
        icon_path = os.path.join(_ROOT, "icon.png")

    # 3. Compile with PyInstaller
    print("\n[2/4] Compiling native macOS App Bundle with PyInstaller...")
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "Dolce Colore",
        "--windowed",
        "--icon", icon_path,
        "--add-data", f"{os.path.join(_ROOT, 'frontend', 'dist')}:frontend/dist",
        "--add-data", f"{os.path.join(_ROOT, 'models')}:models",
        "--add-data", f"{os.path.join(_ROOT, 'tools')}:tools",
        "--add-data", f"{os.path.join(_ROOT, 'THIRD_PARTY_NOTICES.md')}:.",
        "--add-data", f"{os.path.join(_ROOT, 'icon.png')}:.",
        "--hidden-import", "server",
        "--hidden-import", "dolce_engine",
        "--hidden-import", "ai_vision",
        "--hidden-import", "license_manager",
        "--hidden-import", "app_version",
        "--hidden-import", "update_checker",
        "--hidden-import", "cv2",
        "--hidden-import", "numpy",
        "--hidden-import", "PIL",
        "--hidden-import", "fastapi",
        "--hidden-import", "starlette",
        "--hidden-import", "uvicorn",
        "--hidden-import", "multipart",
        "--hidden-import", "webview.platforms.cocoa",
        "--collect-all", "onnxruntime",
        "--collect-all", "pywebview",
        "--collect-all", "fastapi",
        "--collect-all", "starlette",
        "--collect-all", "multipart",
        "--noconfirm",
        "--osx-bundle-identifier", "com.revisitedlabs.dolcecolore",
        os.path.join(_ROOT, "desktop.py")
    ]

    run(" ".join(f'"{arg}"' if " " in arg else arg for arg in pyinstaller_cmd))

    app_path = os.path.join(_ROOT, "dist", "Dolce Colore.app")
    if not os.path.exists(app_path):
        print(f"Error: {app_path} was not created.")
        sys.exit(1)
    print(f"SUCCESS: App bundle compiled at {app_path}")

    # 4. Generate DMG Disk Image
    print("\n[3/4] Creating macOS .dmg disk image...")
    dmg_out_dir = os.path.join(_ROOT, "dist-installer")
    os.makedirs(dmg_out_dir, exist_ok=True)
    dmg_path = os.path.join(dmg_out_dir, f"DolceColore_v{__version__}_macOS.dmg")

    if shutil.which("create-dmg"):
        create_dmg_cmd = (
            f'create-dmg --volname "Dolce Colore" '
            f'--window-pos 200 120 --window-size 800 450 '
            f'--icon-size 100 --icon "Dolce Colore.app" 200 190 '
            f'--hide-extension "Dolce Colore.app" '
            f'--app-drop-link 600 185 '
            f'"{dmg_path}" "{app_path}"'
        )
        run(create_dmg_cmd)
    elif shutil.which("hdiutil"):
        hdiutil_cmd = f'hdiutil create -volname "Dolce Colore" -srcfolder "{app_path}" -ov -format UDZO "{dmg_path}"'
        run(hdiutil_cmd)
    else:
        print("[Note] hdiutil/create-dmg not found (running on non-macOS). App bundle is ready.")

    if os.path.isfile(dmg_path):
        print(f"\nSUCCESS: macOS DMG generated at: {dmg_path}")
    else:
        print(f"\nBuild complete. Ready for distribution at: {app_path}")


if __name__ == "__main__":
    main()
