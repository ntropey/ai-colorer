"""
Generate professional LemonSqueezy product image assets for Dolce Colore Pro.
Outputs:
1. 01_cover_hero.png (1280x720) - Primary storefront cover
2. 02_split_comparison.png (1280x720) - Before / After restoration
3. 03_studio_ui.png (1280x720) - Native desktop studio interface
4. 04_cinema_colorizer.png (1280x720) - Cinema video engine & filmstrip
5. 05_pro_features_guarantee.png (1280x720) - 4-pillar grid & 30-day guarantee
6. 06_product_icon_512.png (512x512) - High-res square avatar/thumbnail
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT_DIR = r"c:\dev\ai-colorer\lemonsqueezy_assets"
os.makedirs(OUT_DIR, exist_ok=True)

# Color Palette
BG_COLOR = (11, 15, 25)         # #0B0F19
CARD_BG = (17, 24, 39)          # #111827
CARD_BORDER = (30, 41, 59)      # #1E293B
ACCENT_BLUE = (56, 189, 248)    # #38BDF8
ACCENT_INDIGO = (129, 140, 248) # #818CF8
ACCENT_AMBER = (245, 158, 11)   # #F59E0B
ACCENT_GREEN = (16, 185, 129)   # #10B981
TEXT_WHITE = (241, 245, 249)    # #F1F5F9
TEXT_MUTED = (148, 163, 184)    # #94A3B8
TEXT_DARK = (15, 23, 42)

def get_font(size, bold=False):
    font_name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", font_name), size)
    except Exception:
        try:
            return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

def draw_pill(draw, xy, text, font, bg, fg, border=None):
    x0, y0 = xy
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 14, 6
    w, h = tw + pad_x * 2, th + pad_y * 2
    r = h // 2
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=r, fill=bg, outline=border, width=1)
    draw.text((x0 + pad_x, y0 + pad_y - 2), text, font=font, fill=fg)
    return w, h

def load_sample_images():
    sample_path = r"c:\dev\ai-colorer\models\test_out.png"
    if os.path.exists(sample_path):
        color_img = Image.open(sample_path).convert("RGB")
    else:
        color_img = Image.new("RGB", (512, 512), (100, 150, 200))
    bw_img = color_img.convert("L").convert("RGB")
    return color_img, bw_img

def draw_window_header(draw, x0, y0, x1, title="Dolce Colore Studio"):
    h = 36
    draw.rounded_rectangle([x0, y0, x1, y0 + h + 20], radius=12, fill=(15, 23, 42))
    draw.rectangle([x0, y0 + 16, x1, y0 + h], fill=(15, 23, 42))
    # dots
    draw.ellipse([x0 + 14, y0 + 12, x0 + 24, y0 + 22], fill=(239, 68, 68))
    draw.ellipse([x0 + 30, y0 + 12, x0 + 40, y0 + 22], fill=(245, 158, 11))
    draw.ellipse([x0 + 46, y0 + 12, x0 + 56, y0 + 22], fill=(16, 185, 129))
    # title
    f_title = get_font(12, bold=True)
    draw.text((x0 + 70, y0 + 10), title, font=f_title, fill=TEXT_MUTED)
    draw.line([x0, y0 + h, x1, y0 + h], fill=CARD_BORDER, width=1)
    return y0 + h

# ==============================================================================
# SLIDE 1: Cover Hero (1280 x 720)
# ==============================================================================
def make_slide_1():
    img = Image.new("RGB", (1280, 720), BG_COLOR)
    draw = ImageDraw.Draw(img)
    color_img, bw_img = load_sample_images()
    icon_path = r"c:\dev\ai-colorer\icon.png"
    icon = Image.open(icon_path).convert("RGBA").resize((64, 64)) if os.path.exists(icon_path) else None

    # Ambient Glow
    glow = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([700, 100, 1300, 700], fill=(56, 189, 248, 25))
    gdraw.ellipse([100, 400, 600, 900], fill=(129, 140, 248, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    img.paste(glow, (0, 0), glow)

    # Left Column
    x = 75
    y = 65

    # App Icon + Studio Name
    if icon:
        img.paste(icon, (x, y), icon)
    draw.text((x + 76, y + 8), "REVISITED LABS", font=get_font(12, bold=True), fill=ACCENT_BLUE)
    draw.text((x + 76, y + 26), "Dolce Colore Pro v2.0", font=get_font(18, bold=True), fill=TEXT_WHITE)

    y += 95
    # Pro Badge
    draw_pill(draw, (x, y), "⭐  NATIVE DESKTOP AI SUITE", get_font(11, bold=True), (40, 30, 15), ACCENT_AMBER, ACCENT_AMBER)

    y += 45
    # Headline
    draw.text((x, y), "1-Click AI Historical", font=get_font(40, bold=True), fill=TEXT_WHITE)
    y += 50
    draw.text((x, y), "Photo & Video Colorizer", font=get_font(40, bold=True), fill=ACCENT_BLUE)

    y += 65
    # Subtitle
    lead = ("Breathe vibrant, historically faithful color into black-and-white\n"
            "family archives and vintage cinema. 100% private neural\n"
            "inference running entirely on your local machine.")
    draw.text((x, y), lead, font=get_font(15), fill=TEXT_MUTED, spacing=6)

    y += 100
    # 3 Badges
    b1_w, _ = draw_pill(draw, (x, y), "⚡ DirectML GPU Accelerated", get_font(12, bold=True), CARD_BG, ACCENT_BLUE, CARD_BORDER)
    b2_w, _ = draw_pill(draw, (x + b1_w + 10, y), "🔒 100% Offline Privacy", get_font(12, bold=True), CARD_BG, ACCENT_GREEN, CARD_BORDER)
    y += 40
    draw_pill(draw, (x, y), "🪟 Windows 10/11  &  🍎 macOS", get_font(12, bold=True), CARD_BG, TEXT_WHITE, CARD_BORDER)

    y += 65
    # Pricing Box
    draw.rounded_rectangle([x, y, x + 530, y + 70], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=1)
    draw.text((x + 18, y + 14), "$39 USD", font=get_font(26, bold=True), fill=TEXT_WHITE)
    draw.text((x + 130, y + 20), "Lifetime License · No Subscriptions · 30-Day Guarantee", font=get_font(12), fill=ACCENT_AMBER)

    # Right Column: Showcase Window
    wx0, wy0, wx1, wy1 = 660, 85, 1205, 635
    draw.rounded_rectangle([wx0 - 4, wy0 - 4, wx1 + 4, wy1 + 4], radius=16, outline=ACCENT_BLUE, width=1)
    draw.rounded_rectangle([wx0, wy0, wx1, wy1], radius=14, fill=CARD_BG, outline=CARD_BORDER, width=2)
    top_y = draw_window_header(draw, wx0, wy0, wx1, "Dolce Colore Pro — DirectML [Hardware GPU Active]")

    # Inner image frame
    img_w, img_h = 515, 485
    # Composite Split Image
    split_comp = Image.new("RGB", (img_w, img_h))
    bw_res = bw_img.resize((img_w, img_h))
    col_res = color_img.resize((img_w, img_h))
    split_x = img_w // 2

    split_comp.paste(bw_res.crop((0, 0, split_x, img_h)), (0, 0))
    split_comp.paste(col_res.crop((split_x, 0, img_w, img_h)), (split_x, 0))

    sdraw = ImageDraw.Draw(split_comp)
    # Split line
    sdraw.line([(split_x, 0), (split_x, img_h)], fill=(255, 255, 255), width=2)
    # Handle circle
    cy = img_h // 2
    sdraw.ellipse([split_x - 18, cy - 18, split_x + 18, cy + 18], fill=TEXT_WHITE, outline=CARD_BORDER, width=2)
    sdraw.text((split_x - 8, cy - 9), "◀▶", font=get_font(10, bold=True), fill=TEXT_DARK)

    # Badges on image
    draw_pill(sdraw, (15, 15), "ORIGINAL B&W", get_font(10, bold=True), (0, 0, 0), TEXT_WHITE)
    draw_pill(sdraw, (split_x + 15, 15), "AI RESTORED", get_font(10, bold=True), ACCENT_BLUE, TEXT_DARK)

    img.paste(split_comp, (wx0 + 15, top_y + 15))

    img.save(os.path.join(OUT_DIR, "01_cover_hero.png"), quality=95)
    print("[OK] Created 01_cover_hero.png")

# ==============================================================================
# SLIDE 2: Split Comparison (1280 x 720)
# ==============================================================================
def make_slide_2():
    img = Image.new("RGB", (1280, 720), BG_COLOR)
    draw = ImageDraw.Draw(img)
    color_img, bw_img = load_sample_images()

    # Header
    draw_pill(draw, (75, 45), "NEURAL RESTORATION QUALITY", get_font(11, bold=True), (20, 30, 45), ACCENT_BLUE, ACCENT_BLUE)
    draw.text((75, 80), "CIE L*a*b* Chromatic Isolation", font=get_font(34, bold=True), fill=TEXT_WHITE)
    draw.text((75, 126), "Synthesizes color channels only. Original grain, focus, and micro-contrast remain 100% untouched.",
              font=get_font(15), fill=TEXT_MUTED)

    # Wide Comparison Box
    bx0, by0, bx1, by1 = 75, 175, 1205, 545
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)

    comp_w, comp_h = 1100, 340
    bw_cropped = bw_img.resize((comp_w // 2, comp_h))
    col_cropped = color_img.resize((comp_w // 2, comp_h))

    img.paste(bw_cropped, (bx0 + 15, by0 + 15))
    img.paste(col_cropped, (bx0 + 15 + comp_w // 2, by0 + 15))

    # Divider line
    mid_x = bx0 + 15 + comp_w // 2
    draw.line([(mid_x, by0 + 15), (mid_x, by0 + 15 + comp_h)], fill=ACCENT_BLUE, width=3)

    # Labels
    draw_pill(draw, (bx0 + 30, by0 + 30), "BEFORE: Archival Grayscale", get_font(11, bold=True), (15, 23, 42), TEXT_WHITE)
    draw_pill(draw, (mid_x + 20, by0 + 30), "AFTER: Deep Neural Colorization", get_font(11, bold=True), (16, 185, 129), TEXT_DARK)

    # 3 Pillar feature cards at bottom
    cy = 570
    card_w = 360
    cards = [
        ("🔍 Zero Lost Sharpness", "Luminance L* channel is mathematically preserved; never introduces blur."),
        ("🎨 Historical Color Space", "Trained on millions of archival photos for natural skin tones and fabrics."),
        ("⚡ 1-Click Processing", "Drag and drop any photograph or scan and get immediate neural results.")
    ]
    for i, (ctitle, cdesc) in enumerate(cards):
        cx0 = 75 + i * (card_w + 12)
        cx1 = cx0 + card_w
        draw.rounded_rectangle([cx0, cy, cx1, cy + 105], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=1)
        draw.text((cx0 + 16, cy + 14), ctitle, font=get_font(14, bold=True), fill=TEXT_WHITE)
        draw.text((cx0 + 16, cy + 42), cdesc, font=get_font(12), fill=TEXT_MUTED, spacing=4)

    img.save(os.path.join(OUT_DIR, "02_split_comparison.png"), quality=95)
    print("[OK] Created 02_split_comparison.png")

# ==============================================================================
# SLIDE 3: Studio UI (1280 x 720)
# ==============================================================================
def make_slide_3():
    img = Image.new("RGB", (1280, 720), BG_COLOR)
    draw = ImageDraw.Draw(img)
    color_img, _ = load_sample_images()

    # Header
    draw_pill(draw, (75, 45), "NATIVE DESKTOP INTERFACE", get_font(11, bold=True), (40, 30, 15), ACCENT_AMBER, ACCENT_AMBER)
    draw.text((75, 80), "Professional Local AI Studio", font=get_font(34, bold=True), fill=TEXT_WHITE)
    draw.text((75, 126), "Fluid desktop controls for fine-tuning render factors, color saturation, and GPU hardware engines.",
              font=get_font(15), fill=TEXT_MUTED)

    # Studio Mockup Window
    wx0, wy0, wx1, wy1 = 75, 175, 1205, 665
    draw.rounded_rectangle([wx0, wy0, wx1, wy1], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=2)
    top_y = draw_window_header(draw, wx0, wy0, wx1, "Dolce Colore Studio v2.0 — GPU: Microsoft DirectML [DirectX 12]")

    # Left Sidebar in Window
    sb_w = 230
    draw.rectangle([wx0, top_y, wx0 + sb_w, wy1 - 1], fill=(13, 19, 33))
    draw.line([wx0 + sb_w, top_y, wx0 + sb_w, wy1 - 1], fill=CARD_BORDER, width=1)

    sy = top_y + 20
    draw.text((wx0 + 20, sy), "MODE SELECTION", font=get_font(10, bold=True), fill=TEXT_MUTED)
    sy += 25
    draw_pill(draw, (wx0 + 15, sy), "📷 Single Photo Studio", get_font(11, bold=True), ACCENT_BLUE, TEXT_DARK)
    sy += 38
    draw.text((wx0 + 20, sy), "🎬 Cinema Video Colorizer", font=get_font(11), fill=TEXT_MUTED)
    sy += 30
    draw.text((wx0 + 20, sy), "📁 Batch Folder Queue", font=get_font(11), fill=TEXT_MUTED)

    sy += 45
    draw.text((wx0 + 20, sy), "ENGINE CONTROLS", font=get_font(10, bold=True), fill=TEXT_MUTED)
    sy += 25
    draw.text((wx0 + 20, sy), "Model: DeOldify Artistic v2", font=get_font(11), fill=TEXT_WHITE)
    sy += 25
    draw.text((wx0 + 20, sy), "Render Factor: 35 [Ultra]", font=get_font(11), fill=ACCENT_AMBER)
    sy += 25
    draw.text((wx0 + 20, sy), "Resolution: 4K UHD (Pro)", font=get_font(11), fill=ACCENT_GREEN)
    sy += 25
    draw.text((wx0 + 20, sy), "Acceleration: DirectML ON", font=get_font(11), fill=ACCENT_BLUE)

    # Center Canvas Area
    cx0 = wx0 + sb_w + 20
    cy0 = top_y + 20
    canvas_w = 580
    canvas_h = 400
    draw.rounded_rectangle([cx0, cy0, cx0 + canvas_w, cy0 + canvas_h], radius=10, fill=(10, 14, 22), outline=CARD_BORDER, width=1)

    # Center image preview
    preview = color_img.resize((360, 360))
    img.paste(preview, (cx0 + (canvas_w - 360) // 2, cy0 + 20))

    # Right Tool Inspector
    rx0 = cx0 + canvas_w + 20
    draw.text((rx0, cy0 + 10), "HISTOGRAM & SPECS", font=get_font(11, bold=True), fill=TEXT_WHITE)
    draw.text((rx0, cy0 + 40), "Input: 3840 x 2160 (4K)", font=get_font(11), fill=TEXT_MUTED)
    draw.text((rx0, cy0 + 65), "Color Space: CIE L*a*b*", font=get_font(11), fill=TEXT_MUTED)
    draw.text((rx0, cy0 + 90), "Inference Time: 1.42s", font=get_font(11), fill=ACCENT_GREEN)
    draw.text((rx0, cy0 + 115), "VRAM Usage: 1.8 GB", font=get_font(11), fill=ACCENT_BLUE)

    # Save button mockup
    draw_pill(draw, (rx0, cy0 + 160), "💾 Export 4K Image", get_font(12, bold=True), ACCENT_BLUE, TEXT_DARK)
    draw_pill(draw, (rx0, cy0 + 210), "⚡ Compare Split View", get_font(12, bold=True), CARD_BG, TEXT_WHITE, CARD_BORDER)

    img.save(os.path.join(OUT_DIR, "03_studio_ui.png"), quality=95)
    print("[OK] Created 03_studio_ui.png")

# ==============================================================================
# SLIDE 4: Cinema Video Colorizer (1280 x 720)
# ==============================================================================
def make_slide_4():
    img = Image.new("RGB", (1280, 720), BG_COLOR)
    draw = ImageDraw.Draw(img)
    color_img, bw_img = load_sample_images()

    # Header
    draw_pill(draw, (75, 45), "DOLCE COLORE PRO FEATURE", get_font(11, bold=True), (40, 20, 30), (236, 72, 153), (236, 72, 153))
    draw.text((75, 80), "Cinema Video Colorizer Engine", font=get_font(34, bold=True), fill=TEXT_WHITE)
    draw.text((75, 126), "Colorize historical film reels, archival newsreels, and vintage 8mm clips with 60 FPS temporal smoothing.",
              font=get_font(15), fill=TEXT_MUTED)

    # Filmstrip Container
    fx0, fy0, fx1, fy1 = 75, 180, 1205, 520
    draw.rounded_rectangle([fx0, fy0, fx1, fy1], radius=16, fill=(15, 15, 20), outline=(50, 50, 60), width=2)

    # Sprocket holes on top and bottom
    for sx in range(fx0 + 20, fx1 - 20, 35):
        draw.rounded_rectangle([sx, fy0 + 8, sx + 18, fy0 + 26], radius=4, fill=(40, 40, 50))
        draw.rounded_rectangle([sx, fy1 - 26, sx + 18, fy1 - 8], radius=4, fill=(40, 40, 50))

    # 4 Frames across the strip
    frame_w, frame_h = 245, 240
    frame_y = fy0 + 45
    labels = ["Frame 001 (B&W)", "Frame 015 (Init)", "Frame 030 (Smoothed)", "Frame 060 (Restored)"]

    for i in range(4):
        cx0 = fx0 + 40 + i * (frame_w + 35)
        # Interpolate between B&W and color
        alpha = i / 3.0
        frame_img = Image.blend(bw_img, color_img, alpha).resize((frame_w, frame_h))
        img.paste(frame_img, (cx0, frame_y))
        draw.rectangle([cx0, frame_y, cx0 + frame_w, frame_y + frame_h], outline=CARD_BORDER, width=2)
        draw_pill(draw, (cx0 + 10, frame_y + 10), labels[i], get_font(10, bold=True), (10, 10, 10),
                  TEXT_WHITE if i < 2 else ACCENT_GREEN)

    # Bottom Spec Bar
    sy = 550
    specs = [
        ("🎞️ Temporal Consistency", "Filters inter-frame flicker for smooth motion."),
        ("🚀 GPU Video Pipeline", "Multi-frame batching for fast rendering."),
        ("🔊 Audio Track Preservation", "Original sound track synced and exported automatically.")
    ]
    sw = 360
    for i, (stitle, sdesc) in enumerate(specs):
        sx0 = 75 + i * (sw + 12)
        draw.rounded_rectangle([sx0, sy, sx0 + sw, sy + 115], radius=12, fill=CARD_BG, outline=CARD_BORDER, width=1)
        draw.text((sx0 + 16, sy + 16), stitle, font=get_font(14, bold=True), fill=TEXT_WHITE)
        draw.text((sx0 + 16, sy + 46), sdesc, font=get_font(12), fill=TEXT_MUTED, spacing=4)

    img.save(os.path.join(OUT_DIR, "04_cinema_colorizer.png"), quality=95)
    print("[OK] Created 04_cinema_colorizer.png")

# ==============================================================================
# SLIDE 5: Pro Features & Guarantee (1280 x 720)
# ==============================================================================
def make_slide_5():
    img = Image.new("RGB", (1280, 720), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Header
    draw_pill(draw, (75, 45), "LIFETIME VALUE & PROTECTION", get_font(11, bold=True), (20, 40, 30), ACCENT_GREEN, ACCENT_GREEN)
    draw.text((75, 80), "Why Creators Choose Dolce Colore Pro", font=get_font(34, bold=True), fill=TEXT_WHITE)
    draw.text((75, 126), "Software you own forever. No monthly subscriptions, no token meters, no cloud queues.",
              font=get_font(15), fill=TEXT_MUTED)

    # 4 Feature Grid Cards
    gw, gh = 540, 185
    grid_coords = [
        (75, 180, "🔒 100% Offline & Private",
         "Your sensitive family portraits and commercial archives never leave your PC. All neural inference runs locally. Zero servers, zero telemetric tracking."),
        (650, 180, "⚡ DirectML GPU Acceleration",
         "Hardware accelerated on Windows (DirectX 12 DirectML) and macOS (Apple Silicon MPS). Experience lightning-fast rendering without queue wait times."),
        (75, 390, "🔑 Algorithmic Offline License",
         "Activates mathematically without calling home. Valid for offline, air-gapped workstations and multiple personal devices for life."),
        (650, 390, "🛡️ 30-Day Money-Back Guarantee",
         "Try Dolce Colore Pro 100% risk-free. If it does not perform to your expectations, email support@revisitedlabs.com for an immediate, full refund.")
    ]

    for x0, y0, title, desc in grid_coords:
        draw.rounded_rectangle([x0, y0, x0 + gw, y0 + gh], radius=16, fill=CARD_BG, outline=CARD_BORDER, width=1)
        draw.text((x0 + 24, y0 + 24), title, font=get_font(18, bold=True), fill=TEXT_WHITE)
        draw.text((x0 + 24, y0 + 64), desc, font=get_font(13), fill=TEXT_MUTED, spacing=6)

    # Bottom Callout Strip
    by = 600
    draw.rounded_rectangle([75, by, 1205, by + 75], radius=14, fill=(18, 30, 49), outline=ACCENT_BLUE, width=1)
    draw.text((105, by + 18), "Dolce Colore Pro · $39 USD Lifetime", font=get_font(16, bold=True), fill=TEXT_WHITE)
    draw.text((105, by + 42), "Includes Windows single-file installer, macOS .dmg, all v2.x updates & priority support",
              font=get_font(12), fill=ACCENT_BLUE)
    draw_pill(draw, (980, by + 18), "Instant Key Delivery ->", get_font(12, bold=True), ACCENT_BLUE, TEXT_DARK)

    img.save(os.path.join(OUT_DIR, "05_pro_features_guarantee.png"), quality=95)
    print("[OK] Created 05_pro_features_guarantee.png")

# ==============================================================================
# SLIDE 6: Product Icon (512 x 512)
# ==============================================================================
def make_slide_6():
    img = Image.new("RGB", (512, 512), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Radial subtle glow
    glow = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([80, 80, 432, 432], fill=(56, 189, 248, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img.paste(glow, (0, 0), glow)

    # Card border
    draw.rounded_rectangle([16, 16, 496, 496], radius=48, outline=CARD_BORDER, width=2)

    # Center Icon
    icon_path = r"c:\dev\ai-colorer\icon.png"
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).convert("RGBA").resize((320, 320))
        img.paste(icon, (96, 75), icon)

    # Typography
    draw.text((256, 405), "DOLCE COLORE", font=get_font(20, bold=True), fill=TEXT_WHITE, anchor="mm")
    draw_pill(draw, (206, 435), "PRO EDITION", get_font(11, bold=True), (40, 30, 15), ACCENT_AMBER, ACCENT_AMBER)

    img.save(os.path.join(OUT_DIR, "06_product_icon_512.png"), quality=95)
    print("[OK] Created 06_product_icon_512.png")

if __name__ == "__main__":
    print("Generating LemonSqueezy product image assets...")
    make_slide_1()
    make_slide_2()
    make_slide_3()
    make_slide_4()
    make_slide_5()
    make_slide_6()
    print("All LemonSqueezy assets generated successfully!")
