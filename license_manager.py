"""
Dolce Colore - Offline Algorithmic License Manager
Enables standalone, offline license key verification for Dolce Colore Pro.
Crafted for Revisited Labs (https://revisitedlabs.com).
"""

import os
import re
import json
import hashlib
import secrets
from typing import Dict, Any, Tuple

SALT = "REVISITED_LABS_2026_DOLCE_SECRET_SALT_V1"

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


def get_license_status() -> Dict[str, Any]:
    """Read saved license from ~/.dolce_colore/license.json."""
    if not os.path.isfile(LICENSE_FILE):
        return {
            "is_pro": False,
            "tier": "Community Edition",
            "key": None,
            "revisited_url": "https://revisitedlabs.com"
        }

    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        key = data.get("key", "")
        valid, tier = verify_key(key)
        if valid:
            return {
                "is_pro": True,
                "tier": tier,
                "key": key,
                "activated_at": data.get("activated_at"),
                "revisited_url": "https://revisitedlabs.com"
            }
    except Exception:
        pass

    return {
        "is_pro": False,
        "tier": "Community Edition",
        "key": None,
        "revisited_url": "https://revisitedlabs.com"
    }


def activate_key(key: str) -> Dict[str, Any]:
    """Activate and persist a license key."""
    valid, tier_or_reason = verify_key(key)
    if not valid:
        return {"success": False, "error": tier_or_reason}

    os.makedirs(LICENSE_DIR, exist_ok=True)
    import datetime
    license_data = {
        "key": key.strip().upper(),
        "tier": tier_or_reason,
        "activated_at": datetime.datetime.now().isoformat()
    }
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(license_data, f, indent=2)

    return {
        "success": True,
        "tier": tier_or_reason,
        "message": f"Successfully activated {tier_or_reason}! All Pro features unlocked."
    }


def deactivate_key() -> Dict[str, Any]:
    """Deactivate license and revert to Community Edition."""
    if os.path.isfile(LICENSE_FILE):
        try:
            os.remove(LICENSE_FILE)
        except OSError:
            pass
    return {"success": True, "message": "License deactivated. Reverted to Community Edition."}


if __name__ == "__main__":
    print("Generating 3 sample valid keys for Revisited Labs:")
    for _ in range(3):
        k = generate_key("PRO1")
        v, t = verify_key(k)
        print(f"Key: {k} -> Valid: {v} ({t})")
