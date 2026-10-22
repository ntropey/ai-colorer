import React, { useState } from 'react';
import { Sparkles, Cpu, Film, Image as ImageIcon, FolderArchive, Layers, HelpCircle, X } from 'lucide-react';

export default function Header({
  activeTab,
  setActiveTab,
  hardwareLabel = "DirectML GPU",
  hasVisionKey = false,
  onSelectSample
}) {
  const [showHelp, setShowHelp] = useState(false);

  const SAMPLES = [
    { label: "Audrey Hepburn", file: "/samples/Audrey Hepburn.jpg" },
    { label: "Charlie Chaplin & Helen Keller 1919", file: "/samples/Helen Keller meeting Charlie Chaplin in 1919.jpg" },
    { label: "Louis Armstrong 1946", file: "/samples/Louis Armstrong practicing in his dressing room, ca 1946.jpg" },
    { label: "New York Riverfront 1931", file: "/samples/New York Riverfront December 15, 1931.jpg" },
    { label: "London 1945", file: "/samples/Abandoned Boy Holding a Stuffed Toy Animal. London 1945.jpg" }
  ];

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-xl sticky top-0 z-40 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Logo and Tagline */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl overflow-hidden bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 p-[1.5px] shadow-lg shadow-amber-500/10 shrink-0">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <img src="/icon.png" alt="Dolce Colore Logo" className="w-8 h-8 rounded-lg object-contain" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight bg-gradient-to-r from-amber-400 via-rose-400 to-purple-400 bg-clip-text text-transparent">
                Dolce Colore
              </h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/25">
                v2.0 Native
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              1-Click Historical Photo & Video Colorizer • 100% Private, Local AI Neural Restoration
            </p>
          </div>
        </div>

        {/* Tab Navigation with ARIA roles */}
        <nav role="tablist" aria-label="Workspaces" className="flex items-center bg-slate-900/90 border border-slate-800 p-1 rounded-xl shadow-inner">
          <button
            role="tab"
            aria-selected={activeTab === 'photo'}
            onClick={() => setActiveTab('photo')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'photo'
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ImageIcon className="w-3.5 h-3.5" />
            Photo Studio
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'video'}
            onClick={() => setActiveTab('video')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'video'
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Film className="w-3.5 h-3.5" />
            Cinema Colorizer
          </button>
          <button
            role="tab"
            aria-selected={activeTab === 'batch'}
            onClick={() => setActiveTab('batch')}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'batch'
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FolderArchive className="w-3.5 h-3.5" />
            Batch Archive
          </button>
        </nav>

        {/* Right Section: Sample Picker, Hardware & Help */}
        <div className="flex items-center gap-2.5">
          {/* Historical Sample Selector */}
          {activeTab === 'photo' && (
            <select
              aria-label="Load Historical Archival Sample"
              onChange={(e) => {
                if (e.target.value) onSelectSample(e.target.value);
              }}
              defaultValue=""
              className="bg-slate-900 border border-slate-800 text-slate-300 rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-amber-500 cursor-pointer"
            >
              <option value="" disabled>Load Historical Sample...</option>
              {SAMPLES.map((s, idx) => (
                <option key={idx} value={s.file}>{s.label}</option>
              ))}
            </select>
          )}

          {/* Engine acceleration badge */}
          <div
            title={`Active Neural Engine: ${hardwareLabel}`}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 font-mono shadow-sm"
          >
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span className="truncate max-w-[140px]">{hardwareLabel}</span>
          </div>

          {/* Quick Help Modal Trigger */}
          <button
            onClick={() => setShowHelp(true)}
            className="p-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
            title="Keyboard shortcuts & Quick Guide"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Quick Help Dialog */}
      {showHelp && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-150"
          onClick={() => setShowHelp(false)}
        >
          <div
            className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="font-bold text-slate-100 text-sm flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-amber-400" />
                Dolce Colore Keyboard Shortcuts
              </h3>
              <button
                onClick={() => setShowHelp(false)}
                className="text-slate-400 hover:text-slate-200 text-sm cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-300">
              <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Slide Split Divider</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">← / →</kbd>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Peek Original B&W</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">Spacebar</kbd>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Full 100% B&W / Color</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">Home / End</kbd>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Copy Colorized to Clipboard</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">Click Copy</kbd>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400">Close Dialogs</span>
                <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">Escape</kbd>
              </div>
            </div>

            <div className="pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowHelp(false)}
                className="w-full py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg transition-colors cursor-pointer text-xs"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
