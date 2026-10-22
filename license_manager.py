"""
Dolce Colore - Unified License Manager
Supports both LemonSqueezy Cloud License API and Offline Algorithmic Verification.
Crafted for Revisited Labs (https://revisitedlabs.com).
"""

import os
import re
import json
import hashlib
import secrets
import platform
import urllib.request
import urllib.parse
import urllib.error
import datetime
from typing import Dict, Any, Tuple

SALT = "REVISITED_LABS_2026_DOLCE_SECRET_SALT_V1"
LEMONSQUEEZY_API_BASE = "https://api.lemonsqueezy.com/v1/licenses"

LICENSE_DIR = os.path.join(os.path.expanduser("~"), ".dolce_colore")
LICENSE_FILE = os.path.join(LICENSE_DIR, "license.json")


def compute_checksums(part1: str, part2: str) -> Tuple[str, str]:
    """Compute 2x 4-character checksums from parts + salt."""
    seed = f"{SALT}:{part1.upper()}:{part2.upper()}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest().upper()
    return digest[0:4], digest[4:8]


def generate_key(tier: str = "PRO1") -> str:
    """Generate a valid algorithmic license key for Revisited Labs customers."""
    tier = tier[:4].upper().ljust(4, "X")
    charset = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # visually unambiguous charset
    part2 = "".join(secrets.choice(charset) for _ in range(4))
    chk1, chk2 = compute_checksums(tier, part2)
    return f"DOLCE-{tier}-{part2}-{chk1}-{chk2}"


def verify_key(key: str) -> Tuple[bool, str]:
    """
    Verify if a license key is valid according to the algorithmic salt.
    Returns (is_valid, tier_or_reason).
    """
    if not key or not isinstance(key, str):
        return False, "Empty or invalid key"

    clean_key = key.strip().upper().replace(" ", "")
    parts = clean_key.split("-")
    if len(parts) != 5:
        return False, "License key format must be DOLCE-XXXX-XXXX-XXXX-XXXX"

    prefix, part1, part2, chk1, chk2 = parts
    if prefix != "DOLCE":
        return False, "Invalid product prefix (expected DOLCE)"

    expected_chk1, expected_chk2 = compute_checksums(part1, part2)
    if chk1 == expected_chk1 and chk2 == expected_chk2:
        tier_name = "Dolce Colore Pro"
        if "PRO" in part1:
            tier_name = "Dolce Colore Pro (Lifetime)"
        elif "STUD" in part1:
            tier_name = "Dolce Colore Studio Edition"
        elif "LABS" in part1:
            tier_name = "Revisited Labs Founder Edition"
        return True, tier_name

    return False, "Invalid license key checksum"


def get_instance_name() -> str:
    """Generate a friendly device label for LemonSqueezy activation tracking."""
    host = platform.node() or os.environ.get("COMPUTERNAME", "Desktop")
    system = platform.system() or "PC"
    return f"{host} ({system})"


def activate_lemonsqueezy(license_key: str, instance_name: str = None) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Activate a license key using LemonSqueezy License API.
    POST https://api.lemonsqueezy.com/v1/licenses/activate
    """
    if not instance_name:
        instance_name = get_instance_name()

    url = f"{LEMONSQUEEZY_API_BASE}/activate"
    data = urllib.parse.urlencode({
        "license_key": license_key.strip(),
        "instance_name": instance_name
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "User-Agent": "DolceColore/2.0 (Revisited Labs)"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if body.get("activated"):
                return True, "Successfully activated via LemonSqueezy", body
            err = body.get("error") or "Activation failed"
            return False, err, body
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
            err = err_body.get("error") or f"HTTP error {e.code}"
            return False, err, err_body
        except Exception:
            return False, f"LemonSqueezy server returned HTTP {e.code}", {}
    except urllib.error.URLError as e:
        return False, f"Network error connecting to LemonSqueezy: {e.reason}", {}
    except Exception as e:
        return False, str(e), {}


def deactivate_lemonsqueezy(license_key: str, instance_id: str) -> Tuple[bool, str]:
    """
    Deactivate a license instance via LemonSqueezy License API.
    POST https://api.lemonsqueezy.com/v1/licenses/deactivate
    """
    url = f"{LEMONSQUEEZY_API_BASE}/deactivate"
    data = urllib.parse.urlencode({
        "license_key": license_key.strip(),
        "instance_id": instance_id
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "User-Agent": "DolceColore/2.0 (Revisited Labs)"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            if body.get("deactivated"):
                return True, "Instance successfully deactivated on LemonSqueezy"
            return False, body.get("error") or "Deactivation failed on LemonSqueezy"
    except Exception as e:
        return False, str(e)


def get_license_status() -> Dict[str, Any]:
    """Read saved license from ~/.dolce_colore/license.json."""
    if not os.path.isfile(LICENSE_FILE):
        return {
            "is_pro": False,
            "tier": "Community Edition",
            "key": None,
            "provider": None,
            "revisited_url": "https://revisitedlabs.com"
        }

    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        provider = data.get("provider", "algorithmic")
        key = data.get("key", "")

        if provider == "algorithmic":
            valid, tier = verify_key(key)
            if valid:
                return {
                    "is_pro": True,
                    "tier": tier,
                    "key": key,
                    "provider": "algorithmic",
                    "activated_at": data.get("activated_at"),
                    "revisited_url": "https://revisitedlabs.com"
                }
        elif provider == "lemonsqueezy":
            # LemonSqueezy activated license
            return {
                "is_pro": True,
                "tier": data.get("tier", "Dolce Colore Pro (Lifetime)"),
                "key": key,
                "provider": "lemonsqueezy",
                "instance_id": data.get("instance_id"),
                "customer_email": data.get("customer_email"),
                "customer_name": data.get("customer_name"),
                "activated_at": data.get("activated_at"),
                "revisited_url": "https://revisitedlabs.com"
            }
    except Exception:
        pass

    return {
        "is_pro": False,
        "tier": "Community Edition",
        "key": None,
        "provider": None,
        "revisited_url": "https://revisitedlabs.com"
    }


def activate_key(raw_key: str) -> Dict[str, Any]:
    """
    Activate a license key.
    Checks algorithmic offline format first; if not, attempts LemonSqueezy API.
    """
    if not raw_key or not isinstance(raw_key, str):
        return {"success": False, "error": "Please enter a valid license key."}

    clean_key = raw_key.strip()
    os.makedirs(LICENSE_DIR, exist_ok=True)
    now = datetime.datetime.now().isoformat()

    # 1. Check if it's an offline algorithmic key (format: DOLCE-XXXX-XXXX-XXXX-XXXX)
    if clean_key.upper().startswith("DOLCE-"):
        valid, tier_or_reason = verify_key(clean_key)
        if valid:
            license_data = {
                "provider": "algorithmic",
                "key": clean_key.upper(),
                "tier": tier_or_reason,
                "activated_at": now
            }
            with open(LICENSE_FILE, "w", encoding="utf-8") as f:
                json.dump(license_data, f, indent=2)

            return {
                "success": True,
                "tier": tier_or_reason,
                "provider": "algorithmic",
                "message": f"Successfully activated {tier_or_reason}! All Pro features unlocked offline."
            }
        else:
            return {"success": False, "error": f"Invalid offline key: {tier_or_reason}"}

    # 2. Try LemonSqueezy License API
    ok, msg, payload = activate_lemonsqueezy(clean_key)
    if ok:
        instance_id = payload.get("instance", {}).get("id")
        meta = payload.get("meta", {})
        customer_email = meta.get("customer_email")
        customer_name = meta.get("customer_name")
        product_name = meta.get("product_name") or "Dolce Colore Pro (Lifetime)"

        license_data = {
            "provider": "lemonsqueezy",
            "key": clean_key,
            "instance_id": instance_id,
            "customer_email": customer_email,
            "customer_name": customer_name,
            "tier": product_name,
            "activated_at": now
        }
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(license_data, f, indent=2)

        return {
            "success": True,
            "tier": product_name,
            "provider": "lemonsqueezy",
            "message": f"Successfully activated via LemonSqueezy! Registered to {customer_email or 'customer'}."
        }
    else:
        # LemonSqueezy returned an error or key wasn't found
        return {
            "success": False,
            "error": f"Activation failed: {msg}. Please check your key or visit revisitedlabs.com/dolce-colore."
        }


def deactivate_key() -> Dict[str, Any]:
    """Deactivate license and revert to Community Edition."""
    if os.path.isfile(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            # If it was LemonSqueezy, notify their server to free the activation instance
            if data.get("provider") == "lemonsqueezy" and data.get("instance_id") and data.get("key"):
                deactivate_lemonsqueezy(data["key"], data["instance_id"])

            os.remove(LICENSE_FILE)
        except Exception:
            pass

    return {"success": True, "message": "License deactivated. Reverted to Community Edition."}


if __name__ == "__main__":
    print("Unified License Manager ready.")
    k = generate_key("PRO1")
    v, t = verify_key(k)
    print(f"Sample offline key: {k} -> Valid: {v} ({t})")
