"""Dolce Colore - manual "Check for updates".

Runs only when the user presses the button. It makes one HTTPS request to the
public GitHub Releases API and sends nothing about the user or their files.
"""

import json
import re
import urllib.error
import urllib.request

from app_version import __version__

RELEASES_URL = "https://api.github.com/repos/ntropey/ai-colorer/releases/latest"
RELEASE_PAGE_PREFIX = "https://github.com/ntropey/ai-colorer/"
TIMEOUT_SECONDS = 6


def parse_version(text: str):
    """'v2.0.10' -> (2, 0, 10). Returns None when there is no x.y.z in the text."""
    match = re.match(r"^\s*v?(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(part) for part in match.groups()) if match else None


def is_newer(latest: str, current: str) -> bool:
    a, b = parse_version(latest), parse_version(current)
    return a is not None and b is not None and a > b


def check_for_update(current: str = __version__, opener=urllib.request.urlopen) -> dict:
    """Return {current, latest, update_available, release_url, notes} or {current, error}."""
    result = {"current": current}
    request = urllib.request.Request(
        RELEASES_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"DolceColore/{current} (update check)",
        },
    )
    try:
        with opener(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        result["error"] = "unreachable"
        return result

    tag = str(data.get("tag_name", ""))
    if parse_version(tag) is None:
        result["error"] = "unreadable"
        return result

    url = str(data.get("html_url", ""))
    if not url.startswith(RELEASE_PAGE_PREFIX):
        url = RELEASE_PAGE_PREFIX + "releases"

    result.update(
        latest=tag.lstrip("v"),
        update_available=is_newer(tag, current),
        release_url=url,
        notes=str(data.get("body") or "")[:600],
    )
    return result
