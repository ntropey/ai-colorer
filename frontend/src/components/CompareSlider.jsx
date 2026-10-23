import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Columns, Download, Copy, Check, Eye, EyeOff, ZoomIn, ZoomOut, ImagePlus, X } from 'lucide-react';

export default function CompareSlider({
  originalUrl,
  colorizedUrl,
  saturation = 1.0,
  contrast = 1.0,
  temperature = 0,
  brightness = 0,
  onDownload,
  onNewPhoto,
  onClear,
  title = "Dolce Colore Restoration"
}) {
  const [sliderPos, setSliderPos] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isPeekingOriginal, setIsPeekingOriginal] = useState(false);
  const [zoomMode, setZoomMode] = useState('contain'); // 'contain' or 'cover'
  const containerRef = useRef(null);

  const handleMove = useCallback((clientX) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
    const percent = Math.round((x / rect.width) * 100);
    setSliderPos(percent);
  }, []);

  const handleTouchMove = useCallback((e) => {
    if (!isDragging) return;
    handleMove(e.touches[0].clientX);
  }, [isDragging, handleMove]);

  const handleMouseMove = useCallback((e) => {
    if (!isDragging) return;
    handleMove(e.clientX);
  }, [isDragging, handleMove]);

  useEffect(() => {
    const handleMouseUp = () => setIsDragging(false);
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      window.addEventListener('touchmove', handleTouchMove);
      window.addEventListener('touchend', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleTouchMove]);

  // Keyboard navigation for WCAG 2.2 AA accessibility
  const handleKeyDown = (e) => {
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      setSliderPos((prev) => Math.max(0, prev - 5));
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      setSliderPos((prev) => Math.min(100, prev + 5));
    } else if (e.key === 'Home') {
      e.preventDefault();
      setSliderPos(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      setSliderPos(100);
    } else if (e.key === ' ') {
      // Spacebar toggle peek
      e.preventDefault();
      setIsPeekingOriginal((prev) => !prev);
    }
  };

  const copyToClipboard = async () => {
    if (!colorizedUrl) return;
    try {
      const response = await fetch(colorizedUrl);
      const blob = await response.blob();
      await navigator.clipboard.write([
        new ClipboardItem({ [blob.type]: blob })
      ]);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy image:', err);
    }
  };

  // Real-time CSS filter preview for zero-latency slider interaction
  const colorFilter = `
    saturate(${saturation})
    contrast(${contrast})
    brightness(${1 + brightness / 100})
    ${temperature > 0 ? `sepia(${Math.min(temperature * 1.5, 40)}%)` : ''}
    ${temperature < 0 ? `hue-rotate(${temperature * 0.8}deg)` : ''}
  `.trim();

  const effectivePos = isPeekingOriginal ? 100 : sliderPos;

  return (
    <div className="flex flex-col h-full bg-slate-900/70 rounded-2xl border border-slate-800/80 p-4 shadow-2xl backdrop-blur-md">
      {/* Top Controls Toolbar */}
      <div className="flex flex-wrap items-center justify-between pb-3 mb-2 border-b border-slate-800/60 gap-3">
        {/* Left: Quick View Presets (WCAG 2.2 AA Single-Pointer Alternative) */}
        <div className="flex items-center gap-1.5 bg-slate-950/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setSliderPos(100)}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition-colors cursor-pointer ${
              sliderPos === 100 && !isPeekingOriginal ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
            title="View 100% Original B&W"
          >
            B&W (100%)
          </button>
          <button
            onClick={() => setSliderPos(50)}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition-colors cursor-pointer ${
              sliderPos === 50 && !isPeekingOriginal ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30 shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Split 50/50 Comparison"
          >
            Split 50/50
          </button>
          <button
            onClick={() => setSliderPos(0)}
            className={`px-2.5 py-1 text-[11px] font-semibold rounded-lg transition-colors cursor-pointer ${
              sliderPos === 0 && !isPeekingOriginal ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
            }`}
            title="View 100% Colorized"
          >
            Color (100%)
          </button>
          <div className="h-3 w-px bg-slate-800 mx-0.5" />
          <button
            onMouseDown={() => setIsPeekingOriginal(true)}
            onMouseUp={() => setIsPeekingOriginal(false)}
            onMouseLeave={() => setIsPeekingOriginal(false)}
            onTouchStart={() => setIsPeekingOriginal(true)}
            onTouchEnd={() => setIsPeekingOriginal(false)}
            className={`flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold rounded-lg transition-colors cursor-pointer select-none ${
              isPeekingOriginal ? 'bg-amber-500 text-slate-950' : 'bg-slate-900 text-slate-300 hover:bg-slate-800'
            }`}
            title="Hold to quickly view original monochrome scan"
          >
            {isPeekingOriginal ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
            Hold to Peek B&W
          </button>
        </div>

        {/* Right Actions: New photo, Clear, Zoom, Copy & Download */}
        <div className="flex items-center gap-2 flex-wrap">
          {onNewPhoto && (
            <button
              onClick={onNewPhoto}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-700 cursor-pointer"
              title="Colorize a different photo"
            >
              <ImagePlus className="w-3.5 h-3.5 text-amber-400" />
              New photo
            </button>
          )}
          {onClear && (
            <button
              onClick={onClear}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-700 cursor-pointer"
              title="Clear this photo and start over"
            >
              <X className="w-3.5 h-3.5 text-slate-400" />
              Clear
            </button>
          )}
          <button
            onClick={() => setZoomMode(zoomMode === 'contain' ? 'cover' : 'contain')}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors cursor-pointer"
            title={zoomMode === 'contain' ? 'Fill frame (Zoom)' : 'Fit image in window'}
          >
            {zoomMode === 'contain' ? <ZoomIn className="w-3.5 h-3.5" /> : <ZoomOut className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={copyToClipboard}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg transition-colors border border-slate-700 cursor-pointer"
            title="Copy colorized image to clipboard"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-slate-400" />}
            {copied ? 'Copied!' : 'Copy'}
          </button>
          <button
            onClick={onDownload}
            className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-lg transition-all shadow-md shadow-amber-500/15 cursor-pointer"
          >
            <Download className="w-3.5 h-3.5" />
            Download HD PNG
          </button>
        </div>
      </div>

      {/* Main Interactive Canvas */}
      <div
        ref={containerRef}
        tabIndex={0}
        role="slider"
        aria-valuenow={sliderPos}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Before/After Split Comparison Slider"
        onKeyDown={handleKeyDown}
        onMouseDown={(e) => {
          setIsDragging(true);
          handleMove(e.clientX);
        }}
        onTouchStart={(e) => {
          setIsDragging(true);
          handleMove(e.touches[0].clientX);
        }}
        className="relative flex-1 min-h-[420px] w-full rounded-xl overflow-hidden cursor-ew-resize select-none bg-slate-950 border border-slate-800 flex items-center justify-center focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:outline-none"
      >
        {/* Colorized Image (Background) */}
        <img
          src={colorizedUrl}
          alt="Colorized Output"
          style={{ filter: colorFilter }}
          className={`absolute inset-0 w-full h-full pointer-events-none transition-filter duration-75 ${
            zoomMode === 'contain' ? 'object-contain' : 'object-cover'
          }`}
        />

        {/* Original B&W Image (Clipped Left Layer) */}
        <div
          className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none"
          style={{
            clipPath: `polygon(0 0, ${effectivePos}% 0, ${effectivePos}% 100%, 0 100%)`
          }}
        >
          <img
            src={originalUrl}
            alt="Original B&W"
            className={`absolute inset-0 w-full h-full pointer-events-none ${
              zoomMode === 'contain' ? 'object-contain' : 'object-cover'
            }`}
          />
        </div>

        {/* Divider Bar & Handle */}
        {!isPeekingOriginal && (
          <div
            className="absolute top-0 bottom-0 w-1 bg-white/90 shadow-[0_0_16px_rgba(0,0,0,0.9)] pointer-events-none transition-transform"
            style={{ left: `${sliderPos}%` }}
          >
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-slate-900 border-2 border-white shadow-2xl flex items-center justify-center text-white text-[10px] font-bold">
              <svg viewBox="0 0 24 24" className="w-4 h-4 fill-none stroke-current stroke-2">
                <path d="M8 7l-5 5 5 5M16 7l5 5-5 5" />
              </svg>
            </div>
          </div>
        )}

        {/* Floating Badges */}
        <div className="absolute top-3 left-3 px-2.5 py-1 rounded-md bg-black/75 backdrop-blur-md border border-white/10 text-[11px] font-bold tracking-wider text-slate-200 shadow-md">
          ORIGINAL B&W
        </div>
        <div className="absolute top-3 right-3 px-2.5 py-1 rounded-md bg-amber-500/25 backdrop-blur-md border border-amber-500/40 text-[11px] font-bold tracking-wider text-amber-300 shadow-md">
          DOLCE COLORE
        </div>

        {/* Keyboard hint helper (discreet) */}
        <div className="absolute bottom-2.5 right-3 px-2 py-0.5 rounded bg-black/60 backdrop-blur-sm border border-white/5 text-[9px] text-slate-400 font-mono pointer-events-none">
          Use ← → arrows to slide • Spacebar to peek
        </div>
      </div>
    </div>
  );
}
