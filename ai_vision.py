"""
Dolce Colore - AI Historical Vision Guidance Module
Pure standard-library HTTP calls to Google Gemini, OpenAI, Anthropic, and OpenRouter.
"""

import os
import json
import base64
import urllib.request
import urllib.error
import cv2
import numpy as np

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".dolce_colore")
CONFIG_FILE = os.path.join(CONFIG_DIR, "ai_config.json")

PROVIDER_PRESETS = {
    "Google Gemini": {
        "model": "gemini-2.0-flash",
        "models": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        "docs_url": "https://aistudio.google.com/app/apikey",
        "badge": "Free Tier Available"
    },
    "OpenAI": {
        "model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o"],
        "docs_url": "https://platform.openai.com/api-keys",
        "badge": "Commercial Standard"
    },
    "Anthropic": {
        "model": "claude-3-5-haiku-20241022",
        "models": ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"],
        "docs_url": "https://console.anthropic.com/settings/keys",
        "badge": "High Accuracy"
    },
    "OpenRouter": {
        "model": "google/gemini-2.0-flash-001",
        "models": ["google/gemini-2.0-flash-001", "openai/gpt-4o-mini", "anthropic/claude-3.5-haiku"],
        "docs_url": "https://openrouter.ai/keys",
        "badge": "Multi-Provider"
    }
}


def load_ai_config() -> dict:
    """Load persisted AI settings."""
    default_config = {
        "enabled": False,
        "provider": "Google Gemini",
        "api_key": "",
        "model": "gemini-2.0-flash"
    }
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default_config.update(saved)
        except Exception:
            pass
    return default_config


def save_ai_config(enabled: bool, provider: str, api_key: str, model: str = "") -> dict:
    """Save AI configuration to local disk."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    cfg = {
        "enabled": bool(enabled),
        "provider": provider,
        "api_key": api_key.strip(),
        "model": model or PROVIDER_PRESETS.get(provider, {}).get("model", "")
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return cfg


def encode_image_jpeg_b64(img_bgr: np.ndarray, max_dim: int = 768) -> str:
    """Encode OpenCV BGR image as Base64 JPEG with resolution capping."""
    if img_bgr is None:
        return ""
    h, w = img_bgr.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        img_bgr = cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)

    ok, buf = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    if not ok:
        return ""
    return base64.b64encode(buf).decode("utf-8")


def clean_json_response(text: str) -> str:
    """Strip markdown code fence blocks if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 2:
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
    return text


def analyze_historical_scene(img_bgr: np.ndarray, provider="Google Gemini", api_key="", model="gemini-2.0-flash", context_hint="") -> dict:
    """Query vision AI to identify authentic historical era, period dyes, and grading bias."""
    if not api_key:
        return {"error": "No API key configured."}

    b64_img = encode_image_jpeg_b64(img_bgr, max_dim=768)
    if not b64_img:
        return {"error": "Failed to encode image."}

    hint_str = f"Historical clue/context from user: {context_hint}" if context_hint else "No prior context provided."
    prompt = f"""You are an expert archival photo and movie restoration specialist and historical researcher.
Examine this black-and-white historical image carefully.
{hint_str}

Tasks:
1. Identify the likely time period / era (e.g. '1910s Pre-WWI', '1920s Weimar / Roaring 20s', '1940s WWII', '1950s Mid-Century').
2. Identify the setting, subjects, uniforms/clothing, architectural materials, and lighting mood.
3. Determine the most authentic historical color palette based on genuine period pigments, fabric dyes, and cultural standards.
4. Recommend global post-processing color grading bias:
   - "saturation_bias": float between 0.85 and 1.30 (1.0 = standard)
   - "color_temperature": integer between -15 (cool blue) and +20 (warm amber)
   - "contrast_bias": float between 0.95 and 1.15 (1.0 = standard)
5. Provide a list of key identified elements with their authentic colors, hex codes, and historical reason.

Return ONLY a valid JSON object matching this schema:
{{
  "era": "...",
  "setting": "...",
  "overall_mood": "...",
  "saturation_bias": 1.1,
  "color_temperature": 5,
  "contrast_bias": 1.05,
  "palette": [
    {{"element": "...", "historical_color": "...", "hex": "#RRGGBB", "reason": "..."}}
  ],
  "colorist_notes": "A concise 2-3 sentence explanation of the period-authentic dyes and color balance chosen."
}}"""

    try:
        if provider == "Google Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
                    ]
                }],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.2
                }
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(clean_json_response(raw_text))

        elif provider in ["OpenAI", "OpenRouter"]:
            url = "https://openrouter.ai/api/v1/chat/completions" if provider == "OpenRouter" else "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            if provider == "OpenRouter":
                headers["HTTP-Referer"] = "https://dolcecolore.app"
                headers["X-Title"] = "Dolce Colore Desktop"

            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]
                }],
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["choices"][0]["message"]["content"]
                return json.loads(clean_json_response(raw_text))

        elif provider == "Anthropic":
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "max_tokens": 1024,
                "temperature": 0.2,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64_img}
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["content"][0]["text"]
                return json.loads(clean_json_response(raw_text))

        return {"error": f"Unsupported provider: {provider}"}

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        return {"error": f"Vision API HTTP Error {e.code}: {body[:250]}"}
    except Exception as e:
        return {"error": f"Vision API Request Failed: {str(e)}"}


def critique_and_refine(img_bw_bgr: np.ndarray, img_col_bgr: np.ndarray, provider="Google Gemini", api_key="", model="gemini-2.0-flash") -> dict:
    """Evaluate colorized output against monochrome original to critique skin tones and vibrancy."""
    if not api_key:
        return {"error": "No API key configured."}

    b64_bw = encode_image_jpeg_b64(img_bw_bgr, max_dim=512)
    b64_col = encode_image_jpeg_b64(img_col_bgr, max_dim=512)
    if not b64_bw or not b64_col:
        return {"error": "Failed to encode comparison images."}

    prompt = """You are a senior color grading supervisor inspecting an archival photograph colorization.
Image 1 is the original black-and-white scan. Image 2 is the neural colorized render.

Evaluate:
1. Are skin tones lifelike (not jaundiced, purple, or waxy)?
2. Is color vibrancy balanced or over/undersaturated?
3. Suggest fine deltas:
   - "saturation_delta": float between -0.25 and +0.25 (0.0 = keep current)
   - "temperature_delta": integer between -15 and +15 (negative = cooler, positive = warmer)
   - "contrast_delta": float between -0.10 and +0.10
   - "critique_summary": concise feedback (1-2 sentences)

Return ONLY valid JSON:
{
  "critique_summary": "...",
  "saturation_delta": 0.05,
  "temperature_delta": 4,
  "contrast_delta": 0.0
}"""

    try:
        if provider == "Google Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": b64_bw}},
                        {"inline_data": {"mime_type": "image/jpeg", "data": b64_col}}
                    ]
                }],
                "generationConfig": {"response_mime_type": "application/json"}
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(clean_json_response(raw_text))

        elif provider in ["OpenAI", "OpenRouter"]:
            url = "https://openrouter.ai/api/v1/chat/completions" if provider == "OpenRouter" else "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Image 1 (B&W) and Image 2 (Colorized). " + prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_bw}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_col}"}}
                    ]
                }],
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["choices"][0]["message"]["content"]
                return json.loads(clean_json_response(raw_text))

        return {"error": f"Unsupported provider: {provider}"}
    except Exception as e:
        return {"error": str(e)}
