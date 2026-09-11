import os
import json
import base64
import urllib.request
import urllib.error
import cv2
import numpy as np

_root = os.path.dirname(os.path.abspath(__file__))

PROVIDER_DEFAULTS = {
    "Google Gemini": {
        "model": "gemini-2.0-flash",
        "models": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        "docs_url": "https://aistudio.google.com/app/apikey",
    },
    "OpenAI": {
        "model": "gpt-4o-mini",
        "models": ["gpt-4o-mini", "gpt-4o"],
        "docs_url": "https://platform.openai.com/api-keys",
    },
    "Anthropic": {
        "model": "claude-3-5-haiku-20241022",
        "models": ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"],
        "docs_url": "https://console.anthropic.com/settings/keys",
    },
    "OpenRouter": {
        "model": "google/gemini-2.0-flash-001",
        "models": ["google/gemini-2.0-flash-001", "openai/gpt-4o-mini", "anthropic/claude-3.5-haiku"],
        "docs_url": "https://openrouter.ai/keys",
    },
}


def load_saved_config():
    env_path = os.path.join(_root, ".env")
    config = {
        "enabled": False,
        "provider": "Google Gemini",
        "api_key": "",
        "model": "gemini-2.0-flash",
    }
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k in ["AI_ENABLED"]:
                            config["enabled"] = (v.lower() in ["1", "true", "yes"])
                        elif k in ["AI_PROVIDER", "PROVIDER"]:
                            config["provider"] = v
                        elif k in ["AI_API_KEY", "API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"]:
                            config["api_key"] = v
                        elif k in ["AI_MODEL", "MODEL"]:
                            config["model"] = v
        except Exception:
            pass
    return config


def save_api_config(enabled: bool, provider: str, api_key: str, model: str = "") -> str:
    env_path = os.path.join(_root, ".env")
    try:
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(f"AI_ENABLED={'true' if enabled else 'false'}\n")
            f.write(f"AI_PROVIDER={provider}\n")
            f.write(f"AI_API_KEY={api_key}\n")
            if model:
                f.write(f"AI_MODEL={model}\n")
        return "✅ AI settings saved locally to .env"
    except Exception as e:
        return f"⚠️ Error saving settings: {e}"


def _encode_image_jpeg_b64(img_bgr, max_dim=768):
    if img_bgr is None:
        return None
    h, w = img_bgr.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / float(max(h, w))
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        img_bgr = cv2.resize(img_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    success, buffer = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
    if not success:
        return None
    return base64.b64encode(buffer).decode("utf-8")


def _clean_json_str(text: str) -> str:
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


def analyze_historical_scene(img_bgr, provider="Google Gemini", api_key="", model="gemini-2.0-flash", context_hint=""):
    if not api_key:
        return {"error": "No API key provided."}
    b64_img = _encode_image_jpeg_b64(img_bgr, max_dim=768)
    if not b64_img:
        return {"error": "Failed to encode image."}

    context_str = f"User historical context / clue: {context_hint}" if context_hint else "No prior context provided."
    prompt = f"""You are a master archival film and photography colorist and historical researcher.
Examine this black-and-white historical image carefully.
{context_str}

Tasks:
1. Identify the likely time period / era (e.g. "1910s Pre-WWI", "1940s WWII era", "1930s Great Depression", "1950s Post-war").
2. Identify the setting, subjects, architecture, clothing/uniforms, materials, and lighting.
3. Determine the most historically accurate color palette based on genuine period dyes, pigments, uniforms, and cultural styles.
4. Recommend global post-processing color grading adjustments:
   - "saturation_bias": float between 0.85 and 1.35 (1.0 = standard, >1.0 = more vibrant)
   - "color_temperature": integer between -15 (cool blue morning/fog) and +20 (warm golden afternoon/amber)
   - "contrast_bias": float between 0.95 and 1.15 (1.0 = standard)
5. Provide a list of key identified elements with their authentic colors, hex codes, and historical reason.

You MUST reply ONLY with a valid JSON object matching this schema:
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
  "colorist_notes": "A concise 2-3 sentence explanation of the historical colors chosen and period authentic pigments."
}}
"""

    try:
        if provider == "Google Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": b64_img
                            }
                        }
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
                return json.loads(_clean_json_str(raw_text))

        elif provider in ["OpenAI", "OpenRouter"]:
            url = "https://openrouter.ai/api/v1/chat/completions" if provider == "OpenRouter" else "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            if provider == "OpenRouter":
                headers["HTTP-Referer"] = "https://pinokio.computer"
                headers["X-Title"] = "Dolce Colore"

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
                return json.loads(_clean_json_str(raw_text))

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
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64_img
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["content"][0]["text"]
                return json.loads(_clean_json_str(raw_text))

        else:
            return {"error": f"Unsupported provider: {provider}"}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="ignore")
        return {"error": f"API HTTP Error {e.code}: {error_body[:200]}"}
    except Exception as e:
        return {"error": f"API Request Failed: {str(e)}"}


def critique_and_refine(img_bw_bgr, img_col_bgr, provider="Google Gemini", api_key="", model="gemini-2.0-flash"):
    if not api_key:
        return {"error": "No API key provided."}
    b64_bw = _encode_image_jpeg_b64(img_bw_bgr, max_dim=512)
    b64_col = _encode_image_jpeg_b64(img_col_bgr, max_dim=512)
    if not b64_bw or not b64_col:
        return {"error": "Failed to encode images."}

    prompt = """You are an expert color grading supervisor examining a colorized archival photograph.
Compare Image 1 (original black-and-white) and Image 2 (neural colorized output).

Evaluate:
1. Are skin tones realistic (not overly yellow, purple, or gray)?
2. Is the overall color vibrancy balanced or over/undersaturated?
3. Suggest fine adjustments:
   - "saturation_delta": float between -0.3 and +0.3 (0.0 = keep current)
   - "temperature_delta": integer between -15 and +15 (negative = cooler, positive = warmer)
   - "contrast_delta": float between -0.1 and +0.1
   - "critique_summary": concise feedback (1-2 sentences)

Return JSON only:
{{
  "critique_summary": "...",
  "saturation_delta": 0.05,
  "temperature_delta": 4,
  "contrast_delta": 0.0
}}
"""

    try:
        if provider == "Google Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Image 1 is the original B&W, Image 2 is the colorized version. " + prompt},
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
                return json.loads(_clean_json_str(raw_text))

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
                return json.loads(_clean_json_str(raw_text))

        elif provider == "Anthropic":
            url = "https://api.anthropic.com/v1/messages"
            headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            payload = {
                "model": model,
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Original B&W:"},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64_bw}},
                        {"type": "text", "text": "Colorized:"},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64_col}},
                        {"type": "text", "text": prompt}
                    ]
                }]
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["content"][0]["text"]
                return json.loads(_clean_json_str(raw_text))

        return {"error": f"Unsupported provider: {provider}"}
    except Exception as e:
        return {"error": str(e)}


def render_ai_card(info: dict) -> str:
    if not info:
        return ""
    if "error" in info:
        return f'<div style="background:#450a0a;border:1px solid #ef4444;border-radius:10px;padding:12px;margin-top:12px;color:#fca5a5;font-size:13px;"><strong>⚠️ AI Vision Notice:</strong> {info["error"]} (Falling back to local colorization)</div>'

    era = info.get("era", "Historical Era")
    setting = info.get("setting", "Historical Scene")
    mood = info.get("overall_mood", "Standard Lighting")
    notes = info.get("colorist_notes", "")
    palette = info.get("palette", [])

    swatches = ""
    for p in palette:
        hex_c = p.get("hex", "#888888")
        elem = p.get("element", "Item")
        col_name = p.get("historical_color", "")
        reason = p.get("reason", "")
        title_tip = f"{col_name} - {reason}" if reason else col_name
        swatches += f'<div title="{title_tip}" style="display:inline-flex;align-items:center;margin:4px 6px 4px 0;background:#1e293b;padding:4px 10px;border-radius:8px;border:1px solid #334155;"><span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:{hex_c};margin-right:8px;border:1px solid #fff;"></span><span style="font-size:12px;color:#f8fafc;"><strong>{elem}</strong>: {col_name} <code style="color:#94a3b8;font-size:11px;">{hex_c}</code></span></div>'

    html = f'''<div style="background:#0f172a;border:1px solid #3b82f6;border-radius:12px;padding:16px;margin-top:14px;box-shadow:0 4px 12px rgba(0,0,0,0.3);">
  <div style="display:flex;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:6px;">
    <span style="font-size:18px;">🏛️</span>
    <strong style="color:#60a5fa;font-size:15px;">AI Historical Colorist Analysis</strong>
    <span style="margin-left:auto;background:#1e3a8a;color:#93c5fd;font-size:11px;font-weight:600;padding:3px 10px;border-radius:9999px;">{era}</span>
  </div>
  <p style="color:#94a3b8;font-size:13px;margin:4px 0;"><strong>Setting:</strong> {setting} &bull; <strong>Lighting:</strong> {mood}</p>
  <p style="color:#e2e8f0;font-size:13px;margin:8px 0;background:#1e293b;padding:10px 12px;border-radius:8px;border-left:3px solid #3b82f6;line-height:1.4;"><em>"{notes}"</em></p>
  <div style="margin-top:10px;">
    <div style="color:#94a3b8;font-size:11px;font-weight:700;letter-spacing:0.05em;margin-bottom:6px;text-transform:uppercase;">AUTHENTIC PERIOD PALETTE & DYES:</div>
    <div style="display:flex;flex-wrap:wrap;">{swatches}</div>
  </div>
</div>'''
    return html
