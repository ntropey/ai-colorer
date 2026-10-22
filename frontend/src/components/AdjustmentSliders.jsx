import React from 'react';
import { Sliders, Sun, Palette, Thermometer, RotateCcw, Undo2 } from 'lucide-react';

export default function AdjustmentSliders({
  saturation,
  setSaturation,
  contrast,
  setContrast,
  temperature,
  setTemperature,
  brightness,
  setBrightness,
  onApplyInstant,
  disabled = false
}) {
  const resetAll = () => {
    setSaturation(1.0);
    setContrast(1.0);
    setTemperature(0);
    setBrightness(0);
    if (onApplyInstant) onApplyInstant({ sat: 1.0, con: 1.0, temp: 0, bri: 0 });
  };

  const isDefault = saturation === 1.0 && contrast === 1.0 && temperature === 0 && brightness === 0;

  return (
    <div className="bg-slate-900/70 rounded-2xl border border-slate-800/80 p-4 shadow-xl backdrop-blur-md flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-amber-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Real-Time Color Grading
          </h3>
        </div>
        <button
          onClick={resetAll}
          disabled={disabled || isDefault}
          className={`flex items-center gap-1 text-[11px] font-medium transition-colors cursor-pointer rounded px-1.5 py-0.5 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:outline-none ${
            isDefault ? 'text-slate-600 cursor-not-allowed opacity-50' : 'text-slate-400 hover:text-amber-400'
          }`}
          title="Reset all adjustments to neutral defaults"
        >
          <RotateCcw className="w-3 h-3" />
          Reset All
        </button>
      </div>

      <div className="space-y-4">
        {/* Saturation */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="flex items-center gap-1.5 text-slate-200 font-medium">
              <Palette className="w-3.5 h-3.5 text-rose-400" />
              Saturation (Vibrancy)
            </span>
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-[11px] text-amber-400 font-semibold min-w-[36px] text-right">
                {saturation.toFixed(2)}×
              </span>
              {saturation !== 1.0 && (
                <button
                  onClick={() => {
                    setSaturation(1.0);
                    if (onApplyInstant) onApplyInstant({ sat: 1.0 });
                  }}
                  className="text-slate-500 hover:text-slate-300 cursor-pointer p-0.5"
                  title="Reset Saturation"
                >
                  <Undo2 className="w-2.5 h-2.5" />
                </button>
              )}
            </div>
          </div>
          <input
            type="range"
            min="0.0"
            max="2.0"
            step="0.05"
            value={saturation}
            disabled={disabled}
            aria-label="Saturation Vibrancy"
            onChange={(e) => {
              const val = parseFloat(e.target.value);
              setSaturation(val);
              if (onApplyInstant) onApplyInstant({ sat: val });
            }}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500 disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:outline-none"
          />
        </div>

        {/* Contrast */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="flex items-center gap-1.5 text-slate-200 font-medium">
              <Sun className="w-3.5 h-3.5 text-sky-400" />
              Contrast
            </span>
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-[11px] text-amber-400 font-semibold min-w-[36px] text-right">
                {contrast.toFixed(2)}×
              </span>
              {contrast !== 1.0 && (
                <button
                  onClick={() => {
                    setContrast(1.0);
                    if (onApplyInstant) onApplyInstant({ con: 1.0 });
                  }}
                  className="text-slate-500 hover:text-slate-300 cursor-pointer p-0.5"
                  title="Reset Contrast"
                >
                  <Undo2 className="w-2.5 h-2.5" />
                </button>
              )}
            </div>
          </div>
          <input
            type="range"
            min="0.6"
            max="1.4"
            step="0.02"
            value={contrast}
            disabled={disabled}
            aria-label="Contrast"
            onChange={(e) => {
              const val = parseFloat(e.target.value);
              setContrast(val);
              if (onApplyInstant) onApplyInstant({ con: val });
            }}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500 disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:outline-none"
          />
        </div>

        {/* Color Temperature */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="flex items-center gap-1.5 text-slate-200 font-medium">
              <Thermometer className="w-3.5 h-3.5 text-amber-400" />
              Color Temperature
            </span>
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-[11px] text-amber-400 font-semibold min-w-[50px] text-right">
                {temperature > 0 ? `+${temperature} (Warm)` : temperature < 0 ? `${temperature} (Cool)` : '0 (Neutral)'}
              </span>
              {temperature !== 0 && (
                <button
                  onClick={() => {
                    setTemperature(0);
                    if (onApplyInstant) onApplyInstant({ temp: 0 });
                  }}
                  className="text-slate-500 hover:text-slate-300 cursor-pointer p-0.5"
                  title="Reset Temperature"
                >
                  <Undo2 className="w-2.5 h-2.5" />
                </button>
              )}
            </div>
          </div>
          <input
            type="range"
            min="-25"
            max="25"
            step="1"
            value={temperature}
            disabled={disabled}
            aria-label="Color Temperature"
            onChange={(e) => {
              const val = parseInt(e.target.value, 10);
              setTemperature(val);
              if (onApplyInstant) onApplyInstant({ temp: val });
            }}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500 disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:outline-none"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-medium">
            <span>Cool Cyan</span>
            <span>Warm Amber</span>
          </div>
        </div>

        {/* Brightness / Exposure */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <span className="flex items-center gap-1.5 text-slate-200 font-medium">
              <Sun className="w-3.5 h-3.5 text-yellow-300" />
              Exposure Bias
            </span>
            <div className="flex items-center gap-1.5">
              <span className="font-mono text-[11px] text-amber-400 font-semibold min-w-[36px] text-right">
                {brightness > 0 ? `+${brightness}` : brightness}
              </span>
              {brightness !== 0 && (
                <button
                  onClick={() => {
                    setBrightness(0);
                    if (onApplyInstant) onApplyInstant({ bri: 0 });
                  }}
                  className="text-slate-500 hover:text-slate-300 cursor-pointer p-0.5"
                  title="Reset Exposure"
                >
                  <Undo2 className="w-2.5 h-2.5" />
                </button>
              )}
            </div>
          </div>
          <input
            type="range"
            min="-30"
            max="30"
            step="1"
            value={brightness}
            disabled={disabled}
            aria-label="Exposure Bias"
            onChange={(e) => {
              const val = parseInt(e.target.value, 10);
              setBrightness(val);
              if (onApplyInstant) onApplyInstant({ bri: val });
            }}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500 disabled:opacity-40 focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:outline-none"
          />
        </div>
      </div>
    </div>
  );
}
