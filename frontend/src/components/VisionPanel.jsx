import React, { useState, useEffect } from 'react';
import { Sparkles, Key, CheckCircle2, AlertCircle, RefreshCw, Layers, ShieldCheck, Copy, Check } from 'lucide-react';

export default function VisionPanel({
  aiAnalysis,
  aiCritique,
  onRunAnalysis,
  onRunCritique,
  onApplyBiases,
  onSaveConfig,
  currentConfig,
  isAnalyzing,
  isCritiquing,
  hasImage
}) {
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [provider, setProvider] = useState(currentConfig?.provider || 'Google Gemini');
  const [apiKey, setApiKey] = useState('');
  const [model, setModel] = useState(currentConfig?.model || 'gemini-2.0-flash');
  const [contextHint, setContextHint] = useState('');
  const [copiedHex, setCopiedHex] = useState(null);

  // Close modal on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && showKeyModal) {
        setShowKeyModal(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showKeyModal]);

  const handleSaveKey = async (e) => {
    e.preventDefault();
    if (onSaveConfig) {
      await onSaveConfig({ enabled: true, provider, apiKey, model });
    }
    setShowKeyModal(false);
  };

  const copyHex = (hex) => {
    if (!hex) return;
    navigator.clipboard.writeText(hex);
    setCopiedHex(hex);
    setTimeout(() => setCopiedHex(null), 1500);
  };

  const hasApiKey = currentConfig?.has_key;

  return (
    <div className="bg-slate-900/70 rounded-2xl border border-slate-800/80 p-4 shadow-xl backdrop-blur-md flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-200">
            Historical AI Vision Guide
          </h3>
        </div>
        <button
          onClick={() => setShowKeyModal(true)}
          className={`flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-medium rounded-lg border transition-colors cursor-pointer focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:outline-none ${
            hasApiKey
              ? 'bg-purple-950/40 border-purple-800/60 text-purple-300 hover:bg-purple-900/60'
              : 'bg-slate-800/80 border-slate-700 text-slate-300 hover:text-white'
          }`}
        >
          <Key className="w-3 h-3" />
          {hasApiKey ? 'Key Active' : 'Add API Key'}
        </button>
      </div>

      {/* Main Vision Content */}
      {!hasApiKey ? (
        <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-center flex flex-col items-center gap-2.5">
          <p className="text-xs text-slate-300 leading-relaxed">
            Connect a <strong>Google Gemini (Free Tier)</strong> or <strong>OpenAI</strong> API key to inspect photos for authentic era dyes, military pigments, and period lighting.
          </p>
          <button
            onClick={() => setShowKeyModal(true)}
            className="mt-1 px-4 py-1.5 text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-all shadow-md shadow-purple-600/20 cursor-pointer focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:outline-none"
          >
            Configure AI Vision Key
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Action Row */}
          <div className="flex gap-2">
            <button
              onClick={() => onRunAnalysis(contextHint)}
              disabled={!hasImage || isAnalyzing}
              className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold bg-purple-600 hover:bg-purple-500 text-white rounded-xl transition-all disabled:opacity-40 shadow-md shadow-purple-600/15 cursor-pointer focus-visible:ring-2 focus-visible:ring-purple-400 focus-visible:outline-none"
            >
              {isAnalyzing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Researching Era...
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  Inspect Period Pigments
                </>
              )}
            </button>

            <button
              onClick={onRunCritique}
              disabled={!hasImage || isCritiquing}
              className="flex items-center gap-1.5 py-2 px-3 text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl transition-all disabled:opacity-40 cursor-pointer focus-visible:ring-2 focus-visible:ring-amber-400 focus-visible:outline-none"
              title="Critique skin tones and color balance"
            >
              {isCritiquing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Layers className="w-3.5 h-3.5" />}
              Critique
            </button>
          </div>

          {/* Context Clue Input */}
          <div className="relative">
            <input
              type="text"
              placeholder="Historical clue (e.g. '1920s Berlin', 'WWII Pacific Fleet')..."
              value={contextHint}
              onChange={(e) => setContextHint(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
            />
          </div>

          {/* Analysis Results Display */}
          {aiAnalysis && (
            <div className="p-3.5 rounded-xl bg-slate-950/90 border border-purple-900/60 space-y-3 shadow-inner">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400">
                  Identified Era
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-purple-900/80 text-purple-200 border border-purple-700/60 shadow-sm">
                  {aiAnalysis.era || 'Archival Period'}
                </span>
              </div>

              <p className="text-xs text-slate-300">
                <strong className="text-slate-100">Setting:</strong> {aiAnalysis.setting} • <strong className="text-slate-100">Mood:</strong> {aiAnalysis.overall_mood}
              </p>

              {aiAnalysis.colorist_notes && (
                <div className="text-xs text-slate-200 italic border-l-2 border-purple-500 pl-2.5 py-1 leading-relaxed bg-purple-950/30 rounded-r">
                  "{aiAnalysis.colorist_notes}"
                </div>
              )}

              {/* Swatches with Click-to-Copy */}
              {aiAnalysis.palette && aiAnalysis.palette.length > 0 && (
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Authentic Period Dyes (Click to Copy Hex):
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {aiAnalysis.palette.map((p, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => copyHex(p.hex)}
                        title={`${p.element}: ${p.historical_color || ''} (${p.hex}) — ${p.reason || ''}. Click to copy.`}
                        className="flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 px-2 py-1 rounded-md border border-slate-800 text-[11px] text-slate-200 transition-colors cursor-pointer group"
                      >
                        <span
                          className="w-2.5 h-2.5 rounded-full border border-white/40 shadow-sm shrink-0"
                          style={{ backgroundColor: p.hex || '#888' }}
                        />
                        <span className="font-semibold text-slate-200">{p.element}:</span>
                        <span className="text-slate-400">{p.historical_color}</span>
                        {copiedHex === p.hex ? (
                          <Check className="w-3 h-3 text-emerald-400" />
                        ) : (
                          <span className="font-mono text-[9px] text-slate-500 group-hover:text-purple-300">
                            {p.hex}
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Apply Recommended Grading Button */}
              <button
                onClick={() => onApplyBiases({
                  sat: aiAnalysis.saturation_bias || 1.0,
                  con: aiAnalysis.contrast_bias || 1.0,
                  temp: aiAnalysis.color_temperature || 0
                })}
                className="w-full mt-2 py-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-all flex items-center justify-center gap-1.5 shadow-md shadow-emerald-600/15 cursor-pointer focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:outline-none"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                Apply AI Recommended Grading ({aiAnalysis.saturation_bias || 1.0}× sat, {aiAnalysis.color_temperature || 0 > 0 ? `+${aiAnalysis.color_temperature}` : aiAnalysis.color_temperature || 0} temp)
              </button>
            </div>
          )}

          {/* Critique Results Display */}
          {aiCritique && (
            <div className="p-3.5 rounded-xl bg-slate-950/90 border border-emerald-900/60 space-y-2 shadow-inner">
              <div className="flex items-center gap-1.5 text-emerald-400 text-xs font-semibold">
                <ShieldCheck className="w-4 h-4" />
                Skin Tone & Vibrancy Review
              </div>
              <p className="text-xs text-slate-200 italic leading-relaxed">
                "{aiCritique.critique_summary}"
              </p>
              <div className="text-[11px] text-slate-400 font-mono">
                Applied deltas: Sat {aiCritique.saturation_delta >= 0 ? `+${aiCritique.saturation_delta}` : aiCritique.saturation_delta}, Temp {aiCritique.temperature_delta >= 0 ? `+${aiCritique.temperature_delta}` : aiCritique.temperature_delta}
              </div>
            </div>
          )}
        </div>
      )}

      {/* API Key Modal with Escape listener */}
      {showKeyModal && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-150"
          onClick={() => setShowKeyModal(false)}
        >
          <div
            className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Key className="w-5 h-5 text-purple-400" />
                <h3 className="font-semibold text-slate-100 text-sm">
                  Historical Vision Configuration
                </h3>
              </div>
              <button
                onClick={() => setShowKeyModal(false)}
                className="text-slate-400 hover:text-slate-200 text-sm p-1 rounded hover:bg-slate-800 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSaveKey} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="text-slate-200 font-semibold">Vision AI Provider</label>
                <select
                  value={provider}
                  onChange={(e) => {
                    const prov = e.target.value;
                    setProvider(prov);
                    if (prov === 'Google Gemini') setModel('gemini-2.0-flash');
                    else if (prov === 'OpenAI') setModel('gpt-4o-mini');
                    else if (prov === 'Anthropic') setModel('claude-3-5-haiku-20241022');
                    else if (prov === 'OpenRouter') setModel('google/gemini-2.0-flash-001');
                  }}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="Google Gemini">Google Gemini (Recommended - Free Tier Available)</option>
                  <option value="OpenAI">OpenAI (GPT-4o-mini / GPT-4o)</option>
                  <option value="Anthropic">Anthropic (Claude 3.5 Haiku)</option>
                  <option value="OpenRouter">OpenRouter</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-slate-200 font-semibold">Model Identifier</label>
                <input
                  type="text"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 font-mono text-xs focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <label className="text-slate-200 font-semibold">API Key</label>
                  <a
                    href={provider === 'Google Gemini' ? 'https://aistudio.google.com/app/apikey' : 'https://platform.openai.com/api-keys'}
                    target="_blank"
                    rel="noreferrer"
                    className="text-purple-400 hover:text-purple-300 font-semibold underline text-[11px]"
                  >
                    Get Free Key →
                  </a>
                </div>
                <input
                  type="password"
                  placeholder="Paste your API key here..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 font-mono text-xs focus:outline-none focus:border-purple-500"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  100% Private: Key is stored locally in <code>~/.dolce_colore/ai_config.json</code> and sent only to the vision endpoint.
                </p>
              </div>

              <div className="flex gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowKeyModal(false)}
                  className="flex-1 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-lg transition-colors shadow-md shadow-purple-600/20 cursor-pointer"
                >
                  Save Configuration
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
