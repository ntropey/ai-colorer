import React, { useState } from 'react';
import { APP_VERSION } from '../version';
import { X, ExternalLink, ShieldCheck, Cpu, Key, Sparkles, Heart, RefreshCw, CheckCircle2 } from 'lucide-react';

export default function AboutModal({
  isOpen,
  onClose,
  license,
  onOpenLicense,
  hardwareLabel = "DirectML GPU"
}) {
  // idle | checking | done | error
  const [updateState, setUpdateState] = useState('idle');
  const [updateInfo, setUpdateInfo] = useState(null);

  if (!isOpen) return null;

  const openUrl = async (url) => {
    try {
      const formData = new FormData();
      formData.append('url', url);
      await fetch('/api/system/open-url', {
        method: 'POST',
        body: formData,
      });
    } catch (e) {
      window.open(url, '_blank');
    }
  };

  const handleOpenRevisitedLabs = () => openUrl('https://revisitedlabs.com');

  const handleCheckUpdates = async () => {
    setUpdateState('checking');
    try {
      const res = await fetch('/api/update/check');
      const data = await res.json();
      setUpdateInfo(data);
      setUpdateState(data.error ? 'error' : 'done');
    } catch (e) {
      setUpdateInfo(null);
      setUpdateState('error');
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-800 rounded-3xl max-w-lg w-full overflow-hidden shadow-2xl space-y-0"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header with Banner */}
        <div className="relative p-6 bg-gradient-to-br from-amber-500/10 via-rose-500/5 to-purple-500/10 border-b border-slate-800/80">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1.5 rounded-full bg-slate-950/60 hover:bg-slate-800 text-slate-400 hover:text-slate-100 transition-colors cursor-pointer"
            aria-label="Close"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-slate-950 p-2 border border-slate-800/80 shadow-xl flex items-center justify-center shrink-0">
              <img src="/icon.png" alt="Dolce Colore" className="w-11 h-11 rounded-xl object-contain" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-black tracking-tight bg-gradient-to-r from-amber-300 via-rose-300 to-purple-300 bg-clip-text text-transparent">
                  Dolce Colore
                </h2>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  v{APP_VERSION}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                1-Click Historical Photo & Video Colorizer
              </p>
            </div>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 text-xs text-slate-300 max-h-[75vh] overflow-y-auto">
          {/* Revisited Labs Card */}
          <div className="bg-gradient-to-r from-slate-950 to-slate-900/90 border border-amber-500/25 rounded-2xl p-4 shadow-lg space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span className="font-bold text-slate-100 tracking-wide text-sm">
                  Revisited Labs
                </span>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
                Studio Edition
              </span>
            </div>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              Dolce Colore is designed and maintained by <strong>Revisited Labs</strong>.
              We build modern, private, high-craft desktop & web tools that revive vintage classics,
              archival photography, and historical software.
            </p>
            <button
              onClick={handleOpenRevisitedLabs}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold transition-all shadow-md shadow-amber-500/15 cursor-pointer text-xs"
            >
              <span>Visit revisitedlabs.com</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* License & Registration Status */}
          <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 font-semibold flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-amber-400" />
                License Registration
              </span>
              <span
                className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                  license?.is_pro
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-slate-800 text-slate-400 border border-slate-700'
                }`}
              >
                {license?.tier || 'Community Edition'}
              </span>
            </div>
            {license?.is_pro ? (
              <div className="text-[11px] text-slate-400 space-y-1 font-mono">
                <p>Serial Key: <span className="text-slate-200">{license?.key}</span></p>
                <p className="text-emerald-400 text-[10px]">✓ Unlimited batch processing and 4K cinema exports enabled.</p>
              </div>
            ) : (
              <p className="text-[11px] text-slate-400">
                You are currently running the free Community Edition. Unlimited photo colorization is free.
                Unlock batch video exports & 4K upscaling with a Pro serial key.
              </p>
            )}
            <button
              onClick={() => {
                onClose();
                if (onOpenLicense) onOpenLicense();
              }}
              className="w-full py-2 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-slate-100 font-semibold text-xs transition-colors cursor-pointer"
            >
              {license?.is_pro ? 'Manage License Key' : 'Enter Serial Number / Activate Pro'}
            </button>
          </div>

          {/* Check for updates (manual only) */}
          <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between gap-3">
              <span className="text-slate-400 font-semibold flex items-center gap-1.5">
                <RefreshCw className="w-3.5 h-3.5 text-amber-400" />
                Updates
              </span>
              <button
                type="button"
                onClick={handleCheckUpdates}
                disabled={updateState === 'checking'}
                className="py-1.5 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 disabled:opacity-60 border border-slate-800 text-slate-200 font-semibold text-xs transition-colors cursor-pointer disabled:cursor-wait"
              >
                {updateState === 'checking' ? 'Checking…' : 'Check for updates'}
              </button>
            </div>
            <div aria-live="polite" className="text-[11px] text-slate-400 space-y-2">
              {updateState === 'done' && updateInfo && !updateInfo.update_available && (
                <p className="flex items-center gap-1.5 text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  You're up to date (v{updateInfo.current}).
                </p>
              )}
              {updateState === 'done' && updateInfo?.update_available && (
                <>
                  <p className="text-amber-300 font-semibold">
                    Version {updateInfo.latest} is available. You have v{updateInfo.current}.
                  </p>
                  {updateInfo.notes && (
                    <p className="whitespace-pre-line text-slate-500 max-h-24 overflow-y-auto">{updateInfo.notes}</p>
                  )}
                  <button
                    type="button"
                    onClick={() => openUrl(updateInfo.download_url)}
                    className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-colors cursor-pointer"
                  >
                    <span>Download version {updateInfo.latest}</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                </>
              )}
              {updateState === 'error' && (
                <p className="text-rose-300">
                  Couldn't check right now. Make sure you're online and try again.
                </p>
              )}
              <p className="text-[10px] text-slate-500">
                Only checks when you press the button. It contacts revisitedlabs.com and sends nothing about you or your photos.
              </p>
            </div>
          </div>

          {/* Technical Architecture Specs */}
          <div className="space-y-2">
            <h4 className="text-[11px] uppercase tracking-wider text-slate-400 font-bold">
              Technical Architecture
            </h4>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 space-y-0.5">
                <span className="text-slate-500">Neural Engine</span>
                <p className="text-slate-200 font-medium">ONNX Runtime DirectML</p>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 space-y-0.5">
                <span className="text-slate-500">Acceleration</span>
                <p className="text-emerald-400 font-medium">{hardwareLabel}</p>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 space-y-0.5">
                <span className="text-slate-500">Colorization Architecture</span>
                <p className="text-slate-200 font-medium">DDColor Double-Decoder</p>
              </div>
              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 space-y-0.5">
                <span className="text-slate-500">Color Space</span>
                <p className="text-slate-200 font-medium">CIE L*a*b* (100% Sharpness)</p>
              </div>
            </div>
          </div>

          {/* Privacy & Legal */}
          <div className="pt-2 border-t border-slate-800/80 flex flex-col gap-1 text-[10px] text-slate-500 text-center">
            <p className="flex items-center justify-center gap-1">
              <ShieldCheck className="w-3 h-3 text-emerald-400" />
              100% Private, Local Execution — Zero Cloud Telemetry
            </p>
            <p>© 2026 Revisited Labs. All rights reserved. (LLC pending registration).</p>
          </div>
        </div>
      </div>
    </div>
  );
}
