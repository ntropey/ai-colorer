import React, { useState, useRef } from 'react';
import { FolderArchive, Upload, Download, CheckCircle2, RefreshCw, Image as ImageIcon } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function BatchStudio() {
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentIdx, setCurrentIdx] = useState(0);
  const fileInputRef = useRef(null);

  const handleFiles = (newFiles) => {
    if (!newFiles || !newFiles.length) return;
    setFiles(Array.from(newFiles));
    setResults([]);
  };

  const processBatch = async () => {
    if (!files.length || isProcessing) return;
    setIsProcessing(true);
    setProgress(0);
    const completed = [];

    for (let i = 0; i < files.length; i++) {
      setCurrentIdx(i + 1);
      const file = files[i];
      const formData = new FormData();
      formData.append('file', file);
      formData.append('model_key', 'ddcolor-tiny');
      formData.append('saturation', 1.05);

      try {
        const res = await fetch('/api/colorize/photo', {
          method: 'POST',
          body: formData
        });
        if (res.ok) {
          const data = await res.json();
          completed.push({
            name: file.name,
            original: data.original_url,
            colorized: data.colorized_url
          });
          setResults([...completed]);
        }
      } catch (err) {
        console.error('Batch error on', file.name, err);
      }
      setProgress(Math.round(((i + 1) / files.length) * 100));
    }

    setIsProcessing(false);
    confetti({ particleCount: 60, spread: 60, origin: { y: 0.7 } });
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900/60 rounded-2xl border border-slate-800/80 p-5 shadow-xl backdrop-blur-md flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
            <FolderArchive className="w-4 h-4 text-amber-400" />
            Batch Archival Photo Restoration
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Colorize entire albums, boxes of historical scans, or negative archives in a single batch pass.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition-colors"
          >
            <Upload className="w-3.5 h-3.5" />
            {files.length > 0 ? `Change Photos (${files.length})` : 'Select Photos'}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*"
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />

          <button
            onClick={processBatch}
            disabled={!files.length || isProcessing}
            className="flex items-center gap-1.5 px-5 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-xl transition-all shadow-md shadow-amber-500/20 disabled:opacity-40"
          >
            {isProcessing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Colorizing {currentIdx}/{files.length}...
              </>
            ) : (
              'Start Batch Colorization'
            )}
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      {isProcessing && (
        <div className="bg-slate-900/60 rounded-xl border border-amber-500/30 p-4 space-y-2">
          <div className="flex justify-between text-xs text-amber-300 font-semibold">
            <span>Processing photo {currentIdx} of {files.length} ({progress}%)</span>
            <span>Batch Neural Inference</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className="bg-gradient-to-r from-amber-500 to-rose-500 h-full rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Results Gallery */}
      {results.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Colorized Archive Gallery ({results.length} restored)
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {results.map((item, idx) => (
              <div key={idx} className="group relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 shadow-md">
                <img
                  src={item.colorized}
                  alt={item.name}
                  className="w-full aspect-square object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent opacity-0 group-hover:opacity-100 transition-opacity p-3 flex flex-col justify-end">
                  <span className="text-[11px] font-semibold text-white truncate">{item.name}</span>
                  <a
                    href={item.colorized}
                    download={`colorized_${item.name}`}
                    className="mt-1 flex items-center justify-center gap-1 py-1 px-2 rounded bg-amber-500 text-slate-950 font-bold text-[10px]"
                  >
                    <Download className="w-3 h-3" />
                    Download PNG
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
