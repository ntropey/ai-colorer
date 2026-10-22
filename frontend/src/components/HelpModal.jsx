import React from 'react';
import { HelpCircle, X } from 'lucide-react';

export default function HelpModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 my-auto max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="font-bold text-slate-100 text-sm flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-amber-400" />
            Dolce Colore Keyboard Shortcuts
          </h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 text-sm cursor-pointer p-1 rounded-lg hover:bg-slate-800 transition-colors"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3 text-xs text-slate-300">
          <div className="flex justify-between items-center py-1.5 border-b border-slate-800/60">
            <span className="text-slate-400">Slide Split Divider</span>
            <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">
              ← / →
            </kbd>
          </div>
          <div className="flex justify-between items-center py-1.5 border-b border-slate-800/60">
            <span className="text-slate-400">Peek Original B&W</span>
            <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">
              Spacebar
            </kbd>
          </div>
          <div className="flex justify-between items-center py-1.5 border-b border-slate-800/60">
            <span className="text-slate-400">Full 100% B&W / Color</span>
            <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">
              Home / End
            </kbd>
          </div>
          <div className="flex justify-between items-center py-1.5 border-b border-slate-800/60">
            <span className="text-slate-400">Copy Colorized to Clipboard</span>
            <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">
              Click Copy
            </kbd>
          </div>
          <div className="flex justify-between items-center py-1.5">
            <span className="text-slate-400">Close Dialogs</span>
            <kbd className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-amber-400">
              Escape
            </kbd>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-800">
          <button
            onClick={onClose}
            className="w-full py-2.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl transition-colors cursor-pointer text-xs shadow-md shadow-amber-500/15"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
