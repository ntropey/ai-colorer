import React, { useState } from 'react';
import { X, Key, CheckCircle2, AlertCircle, ExternalLink, Sparkles, RefreshCw } from 'lucide-react';

export default function LicenseModal({
  isOpen,
  onClose,
  license,
  onLicenseUpdated
}) {
  const [serialInput, setSerialInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState(null); // { type: 'success' | 'error', text: '' }

  if (!isOpen) return null;

  // Format serial as user types: DOLCE-XXXX-XXXX-XXXX-XXXX
  const handleInputChange = (e) => {
    let raw = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (!raw.startsWith('DOLCE')) {
      // Auto-prefix if user just started typing code
      if (raw.length > 0 && !'DOLCE'.startsWith(raw)) {
        raw = 'DOLCE' + raw;
      }
    }
    // Chunk into 5-4-4-4-4
    let formatted = '';
    if (raw.length > 0) formatted += raw.substring(0, 5);
    if (raw.length > 5) formatted += '-' + raw.substring(5, 9);
    if (raw.length > 9) formatted += '-' + raw.substring(9, 13);
    if (raw.length > 13) formatted += '-' + raw.substring(13, 17);
    if (raw.length > 17) formatted += '-' + raw.substring(17, 21);

    setSerialInput(formatted.substring(0, 29));
    setFeedback(null);
  };

  const handleActivate = async (e) => {
    e.preventDefault();
    if (!serialInput.trim()) return;

    setIsLoading(true);
    setFeedback(null);

    try {
      const formData = new FormData();
      formData.append('key', serialInput.trim());

      const res = await fetch('/api/license/activate', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Activation failed');
      }

      setFeedback({ type: 'success', text: data.message });
      if (onLicenseUpdated) onLicenseUpdated();
    } catch (err) {
      setFeedback({ type: 'error', text: err.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeactivate = async () => {
    if (!window.confirm('Are you sure you want to deactivate your license on this machine?')) return;
    setIsLoading(true);
    try {
      await fetch('/api/license/deactivate', { method: 'POST' });
      setFeedback({ type: 'success', text: 'License deactivated.' });
      setSerialInput('');
      if (onLicenseUpdated) onLicenseUpdated();
    } catch (err) {
      setFeedback({ type: 'error', text: 'Failed to deactivate license.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenStore = async () => {
    try {
      const formData = new FormData();
      formData.append('url', 'https://revisitedlabs.com');
      await fetch('/api/system/open-url', { method: 'POST', body: formData });
    } catch (e) {
      window.open('https://revisitedlabs.com', '_blank');
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-150"
      onClick={onClose}
    >
      <div
        className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full overflow-hidden shadow-2xl space-y-0"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 bg-gradient-to-r from-amber-500/10 via-rose-500/5 to-purple-500/10 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <Key className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-slate-100 text-sm">
                License & Registration
              </h3>
              <p className="text-[11px] text-slate-400">
                Dolce Colore Desktop Suite
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-full bg-slate-950/60 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-5 text-xs">
          {/* Current Status Card */}
          <div className="bg-slate-950 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-500 font-medium uppercase tracking-wider block">
                Current Status
              </span>
              <span className="font-bold text-slate-200 text-sm">
                {license?.tier || 'Community Edition'}
              </span>
              {license?.key && (
                <span className="block text-[10px] text-slate-400 font-mono mt-0.5">
                  {license.key}
                </span>
              )}
            </div>
            <span
              className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-1 rounded-full ${
                license?.is_pro
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
              }`}
            >
              {license?.is_pro ? 'Active Pro' : 'Free Tier'}
            </span>
          </div>

          {/* Activation Form */}
          {!license?.is_pro ? (
            <form onSubmit={handleActivate} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-slate-300 block">
                  Enter Serial Number
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={serialInput}
                    onChange={handleInputChange}
                    placeholder="DOLCE-PRO1-XXXX-XXXX-XXXX"
                    className="w-full bg-slate-950 border border-slate-800 focus:border-amber-500 rounded-xl px-3.5 py-2.5 text-xs font-mono tracking-wider text-amber-300 placeholder:text-slate-600 focus:outline-none transition-colors"
                    maxLength={29}
                    required
                  />
                </div>
                <p className="text-[10px] text-slate-500">
                  Offline algorithmic verification. 100% private, no internet phone-home required.
                </p>
              </div>

              {feedback && (
                <div
                  className={`p-3 rounded-xl border text-[11px] flex items-start gap-2 ${
                    feedback.type === 'success'
                      ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                      : 'bg-rose-500/10 border-rose-500/30 text-rose-300'
                  }`}
                >
                  {feedback.type === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  )}
                  <span>{feedback.text}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading || serialInput.length < 24}
                className="w-full py-2.5 px-4 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 font-bold transition-all shadow-md shadow-amber-500/15 cursor-pointer flex items-center justify-center gap-2 text-xs"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Verifying Serial...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Activate Dolce Colore Pro</span>
                  </>
                )}
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-[11px] flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold">License Fully Active</p>
                  <p className="text-[10px] text-emerald-400/80 mt-0.5">
                    Thank you for supporting Revisited Labs! All Pro features are unlocked.
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={handleDeactivate}
                disabled={isLoading}
                className="w-full py-2 px-3 rounded-xl bg-slate-950 hover:bg-rose-950/30 border border-slate-800 hover:border-rose-800/40 text-slate-400 hover:text-rose-300 text-xs font-semibold transition-colors cursor-pointer"
              >
                Deactivate License on This Device
              </button>
            </div>
          )}

          {/* Need a key link */}
          <div className="pt-2 border-t border-slate-800 text-center">
            <button
              onClick={handleOpenStore}
              className="inline-flex items-center gap-1.5 text-[11px] text-amber-400 hover:text-amber-300 font-semibold transition-colors cursor-pointer"
            >
              <span>Need a license key? Visit Revisited Labs</span>
              <ExternalLink className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
