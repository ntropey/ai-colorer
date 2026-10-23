"""Dolce Colore - manual "Check for updates".

Runs only when the user presses the button. It makes one HTTPS request for a
small JSON file on revisitedlabs.com and sends nothing about the user or their
files. Where the installers are hosted (GitHub, Lemon Squeezy, ...) is decided
by that file, not by this code:

    {"version": "2.0.2", "download_url": "https://revisitedlabs.com/dolce-colore", "notes": "..."}
"""

import json
import re
import urllib.error
import urllib.parse
import urllib.request

from app_version import __version__

MANIFEST_URL = "https://revisitedlabs.com/dolce-colore-latest.json"
FALLBACK_DOWNLOAD_URL = "https://revisitedlabs.com/dolce-colore"
ALLOWED_DOWNLOAD_HOSTS = ("revisitedlabs.com", "lemonsqueezy.com")
TIMEOUT_SECONDS = 6


def parse_version(text: str):
    """'v2.0.10' -> (2, 0, 10). Returns None when there is no x.y.z in the text."""
    match = re.match(r"^\s*v?(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(part) for part in match.groups()) if match else None


def is_newer(latest: str, current: str) -> bool:
    a, b = parse_version(latest), parse_version(current)
    return a is not None and b is not None and a > b


def safe_download_url(url: str) -> str:
    """Only https links on our own sites or Lemon Squeezy are ever opened."""
    parts = urllib.parse.urlparse(str(url or ""))
    host = (parts.hostname or "").lower()
    trusted = any(host == h or host.endswith("." + h) for h in ALLOWED_DOWNLOAD_HOSTS)
    return url if parts.scheme == "https" and trusted else FALLBACK_DOWNLOAD_URL


def check_for_update(current: str = __version__, opener=urllib.request.urlopen) -> dict:
    """Return {current, latest, update_available, download_url, notes} or {current, error}."""
    result = {"current": current}
    request = urllib.request.Request(
        MANIFEST_URL,
        headers={"Accept": "application/json", "User-Agent": f"DolceColore/{current} (update check)"},
    )
    try:
        with opener(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        result["error"] = "unreachable"
        return result

    version = str(data.get("version", "")) if isinstance(data, dict) else ""
    if parse_version(version) is None:
        result["error"] = "unreadable"
        return result

    result.update(
        latest=version.lstrip("v"),
        update_available=is_newer(version, current),
        download_url=safe_download_url(data.get("download_url")),
        notes=str(data.get("notes") or "")[:600],
    )
    return result
