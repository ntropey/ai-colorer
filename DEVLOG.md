# 🗒️ Dev Journal — Dolce Colore

Running log of notable changes to the launcher and app, newest entry on top.
This is a working journal (not user-facing docs) — see `README.md` for that.

---

## 2026-09-11

**AI-guided video color grading (wired in, previously display-only)**
- `colorize_video()` in `video_app.py` gained `ai_apply_grading`, `ai_provider`, `ai_key`, `ai_model`, `ai_context` params.
- When enabled, it grabs the first frame, runs the existing `ai_assistant.analyze_historical_scene()` vision call on it (same one the "Analyze Video Keyframe" button already used), then applies the returned saturation/contrast/temperature bias to *every* rendered frame via `apply_adjustments()` before piping to ffmpeg.
- Added a "🎨 Apply this AI historical color grading to the full render" checkbox to the Video tab's AI accordion, wired into `video_btn.click`'s inputs/outputs (now also emits the analysis card).
- Updated in-app API reference text and root `README.md` Python/JS examples to match the new signature.
- Verified: syntax-compiled, and launched the real Gradio server via the Pinokio-managed venv — UI built with no wiring errors, checkbox confirmed present in rendered page, then shut down.
- **Why this mattered:** the AI vision assistant (era/palette/grading analysis, era-authentic pigments) was already fully built in `ai_assistant.py` and applied correctly for single images, but for video it was cosmetic — the keyframe analysis card displayed a recommendation that was never actually applied to the rendered output.
- **Not done yet, on purpose:** Batch Photos tab still has zero AI wiring (no vision call, no per-photo grading) — deferred until this video wiring is tested and confirmed good.

**Rebranding: "AI Colorer" → "Dolce Colore" (display name only)**
- Updated `pinokio.json` (`title`), `README.md` (H1), and `video_app.py` (Gradio window title + banner heading) to "Dolce Colore".
- Repo/folder slug intentionally left as `ai-colorer` — no requirement that the Pinokio install folder name match the display title.
- Note: this rename briefly landed via a stray background agent whose task got disconnected from this conversation, was reverted as a precaution, then re-applied once confirmed it was in fact wanted.

**Banner styling pass**
- Split the header markdown into separate title/subtitle blocks (`video_app.py`) so each could get its own CSS treatment.
- Heading is now larger (44px), bold, gradient text (blue→purple→pink); subtitle restyled for cleaner spacing/color. Badges (engine/AI/privacy/model) unchanged.

---

## Next up
- Wire `ai_assistant` vision guidance into the Batch Photos tab (currently just a flat saturation multiplier, no per-photo analysis).
