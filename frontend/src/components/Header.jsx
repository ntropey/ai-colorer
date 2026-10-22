import React, { useState } from 'react';
import { Sparkles, Cpu, Film, Image as ImageIcon, FolderArchive, Layers, HelpCircle, X, Info, Key, Award } from 'lucide-react';

export default function Header({
  activeTab,
  setActiveTab,
  hardwareLabel = "DirectML GPU",
  hasVisionKey = false,
  onSelectSample,
  license,
  onOpenAbout,
  onOpenLicense,
  onOpenHelp
}) {
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
        {/* Logo and Tagline (Clickable to open About Modal) */}
        <div
          onClick={onOpenAbout}
          className="flex items-center gap-3 cursor-pointer group select-none transition-transform active:scale-[0.99]"
          title="About Dolce Colore & Revisited Labs"
        >
          <div className="w-10 h-10 rounded-xl overflow-hidden bg-gradient-to-tr from-amber-500 via-rose-500 to-purple-600 p-[1.5px] shadow-lg shadow-amber-500/10 shrink-0 group-hover:shadow-amber-500/25 transition-shadow">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <img src="/icon.png" alt="Dolce Colore Logo" className="w-8 h-8 rounded-lg object-contain group-hover:scale-105 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight bg-gradient-to-r from-amber-400 via-rose-400 to-purple-400 bg-clip-text text-transparent group-hover:brightness-110 transition-all">
                Dolce Colore
              </h1>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/25">
                v2.0 Native
              </span>
            </div>
            <p className="text-[11px] text-slate-400 group-hover:text-slate-300 transition-colors">
              1-Click Historical Photo & Video Colorizer • <span className="text-amber-400/90 font-medium">Revisited Labs</span>
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

        {/* Right Section: Sample Picker, License, Hardware & Help */}
        <div className="flex items-center gap-2">
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
              <option value="" disabled>Historical Sample...</option>
              {SAMPLES.map((s, idx) => (
                <option key={idx} value={s.file}>{s.label}</option>
              ))}
            </select>
          )}

          {/* License Badge Button */}
          <button
            onClick={onOpenLicense}
            title={license?.is_pro ? "Dolce Colore Pro Active" : "Click to enter Serial Key or Activate Pro"}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer border ${
              license?.is_pro
                ? 'bg-gradient-to-r from-amber-500/15 to-yellow-500/15 border-amber-500/40 text-amber-300 hover:border-amber-400'
                : 'bg-slate-900 hover:bg-slate-800 border-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {license?.is_pro ? (
              <>
                <Award className="w-3.5 h-3.5 text-amber-400" />
                <span>PRO</span>
              </>
            ) : (
              <>
                <Key className="w-3.5 h-3.5 text-slate-400" />
                <span>Free Tier</span>
              </>
            )}
          </button>

          {/* Engine acceleration badge */}
          <div
            title={`Active Neural Engine: ${hardwareLabel}`}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-[11px] text-slate-300 font-mono shadow-sm"
          >
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span className="truncate max-w-[120px]">{hardwareLabel}</span>
          </div>

          {/* About Modal Trigger */}
          <button
            onClick={onOpenAbout}
            className="p-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
            title="About Dolce Colore & Revisited Labs"
          >
            <Info className="w-4 h-4" />
          </button>

          {/* Quick Help Modal Trigger */}
          <button
            onClick={onOpenHelp}
            className="p-1 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
            title="Keyboard shortcuts & Quick Guide"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
