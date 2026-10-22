# Dolce Colore — Distribution, Monetization & Landing Page Blueprint
**Studio:** Revisited Labs ([https://revisitedlabs.com](https://revisitedlabs.com))  
**Product:** Dolce Colore (v2.0 Native Desktop Suite)  
**Positioning:** 1-Click Historical Photo & Video Colorizer — 100% Private, Local AI Neural Restoration

---

## 1. Domain & URL Architecture

### The Umbrella Studio Strategy
- **Official Hub:** `https://revisitedlabs.com/dolce-colore` (or `https://dolce.revisitedlabs.com`)
- **Vanity Domain Forwarding:** Register `dolcecolore.app` or `dolcecolore.com` ($10–$12/yr via Cloudflare Registrar or Namecheap) and configure a **301 Permanent Redirect** to `https://revisitedlabs.com/dolce-colore`.
- **Benefit:** All press links, backlink SEO authority, and customer traffic directly builds the brand equity of **Revisited Labs** while making vanity URLs clean for social media, YouTube, and ads.

---

## 2. High-Converting Landing Page Blueprint

### Section 1: Hero
- **Headline:** *1-Click Historical Photo & Video Colorizer — 100% Private, Local AI*
- **Subheadline:** *Revive black-and-white family heirlooms and archival 35mm cinema in seconds. DirectML GPU accelerated on your PC. No subscriptions, zero cloud uploads.*
- **Primary CTA:** `[Download Free Trial (Windows / macOS)]` *(Direct installer download)*
- **Secondary CTA:** `[Get Lifetime Pro — $39]` *(Triggers Gumroad/LemonSqueezy checkout overlay)*
- **Trust Badges:** `100% Private & Offline` • `No Cloud Telemetry` • `DirectML & Apple Silicon Accelerated` • `Commercial Rights Included`

### Section 2: Interactive Before/After Split Slider
- Embed an interactive comparison slider (just like the in-app React slider):
  - Left: Authentic 1920s/1940s monochrome archival photo (e.g., Audrey Hepburn, London 1945, or Louis Armstrong).
  - Right: Vibrant, photorealistic colorization using DDColor in CIE $L*a*b*$ space preserving 100% original sharpness.

### Section 3: The Privacy & Offline Advantage (Comparison Matrix)

| Feature | Dolce Colore (Revisited Labs) | Cloud Colorizers (MyHeritage, Palette) | Old Pinokio / Python Scripts |
| :--- | :---: | :---: | :---: |
| **Privacy Guarantee** | **100% Offline (Local DirectML)** | Uploaded to third-party cloud | Local but complex |
| **Pricing Model** | **One-time Lifetime License ($39)** | $120–$240 / year subscription | Free open-source |
| **Ease of Use** | **Double-click Native App (.exe / .dmg)** | Web browser upload | Terminal, Python venv, Git |
| **Full Video Restoration** | **Unlimited Full-Length Cinema** | 15–30 second strict caps | Complex FFmpeg commands |
| **Hardware Acceleration** | **DirectML (AMD/Intel/NVIDIA) + CoreML** | Server-side queue wait times | Requires 6GB+ NVIDIA CUDA |
| **Image Resolution** | **Full Native Camera Resolution** | Downscaled unless extra credit paid | Raw resolution |

### Section 4: Pricing & Tiers
- **Community Edition ($0 — Free Forever)**:
  - Single-photo colorization at standard resolution.
  - Interactive split comparison slider.
  - 15-second video preview clip generator.
  - Great for personal family photos and testing.
- **Dolce Colore Pro ($39 — One-Time Lifetime License)**:
  - Batch photo archive queue (drag & drop hundreds of photos).
  - Cinema Colorizer (unlimited full-length MP4/MOV restoration).
  - 4K photorealistic neural detail weights (`DDColor-L 512`).
  - Historical AI Vision Assistant integration (Gemini / Claude / OpenAI).
  - Commercial usage license for client work & YouTube.

### Section 5: Frequently Asked Questions (FAQ)
- **Q: Does Dolce Colore upload my photos to the internet?**  
  *A: Absolutely not. All neural inferencing and video processing runs 100% locally on your machine's GPU or CPU. You can disconnect your internet cable and the app functions identically.*
- **Q: What are the system requirements?**  
  *A: Windows 10 or 11 with any modern GPU (DirectX 12 / DirectML compatible) or CPU. macOS with Apple Silicon (M1/M2/M3/M4) or Intel.*
- **Q: How do I receive my Pro license key?**  
  *A: Immediately upon checkout on Gumroad / LemonSqueezy, your serial number (`DOLCE-PRO1-XXXX-XXXX-XXXX`) is displayed on-screen and emailed to you. Enter it once into the app to unlock all Pro features permanently.*

---

## 3. Gumroad & LemonSqueezy Serial Number Setup

### Step-by-Step Key Generation & Upload:
1. Open your terminal in `c:\dev\ai-colorer`.
2. Generate 500 or 1,000 valid algorithmic keys using the built-in generator:
   ```bash
   python keygen.py --count 500 --tier PRO1 > keys.txt
   ```
3. Extract just the key codes (strip labels) or use the clean list.
4. **On Gumroad**:
   - Go to **Products** -> **New Product** -> Type: **Digital Product** -> Title: `Dolce Colore Pro`.
   - Under **Product Details**, scroll to **License Keys**.
   - Toggle **"Generate a unique license key per sale"** -> Choose **"Upload your own list of keys"**.
   - Upload `keys.txt`.
   - Gumroad will dispense one key per sale and email it to the buyer with the download link for `DolceColore_Setup_v2.0.exe`.
5. **On LemonSqueezy**:
   - Go to **Products** -> Add Product -> Title: `Dolce Colore Pro`.
   - Under **Files & Fulfillment**, enable **License Keys**.
   - Choose **"Import custom keys"** and upload `keys.txt`.

---

## 4. Launch & Promotional Channels

1. **Reddit**:
   - Post before/after restorations to `r/ColorizedHistory`, `r/OldSchoolCool`, `r/Genealogy`, and `r/photography`.
   - Offer a 20% launch discount code: `REVISITED20`.
2. **Product Hunt**:
   - Launch tagline: *"Dolce Colore — 1-Click Historical Photo & Video Colorizer (100% Private, Local AI)"*.
3. **YouTube Creators**:
   - Reach out to historical documentary creators, genealogy channels, and restoration YouTubers with free review Pro keys.
