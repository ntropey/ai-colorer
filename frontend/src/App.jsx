import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import CompareSlider from './components/CompareSlider';
import AdjustmentSliders from './components/AdjustmentSliders';
import VisionPanel from './components/VisionPanel';
import VideoStudio from './components/VideoStudio';
import BatchStudio from './components/BatchStudio';
import SplashScreen from './components/SplashScreen';
import AboutModal from './components/AboutModal';
import LicenseModal from './components/LicenseModal';
import HelpModal from './components/HelpModal';
import { Upload, Sparkles, Zap, ShieldCheck, Download, RefreshCw, Cpu, Layers } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function App() {
  const [activeTab, setActiveTab] = useState('photo');
  const [systemStatus, setSystemStatus] = useState(null);
  const [license, setLicense] = useState(null);
  const [showSplash, setShowSplash] = useState(true);
  const [showAbout, setShowAbout] = useState(false);
  const [showLicense, setShowLicense] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  // Photo State
  const [currentFile, setCurrentFile] = useState(null);
  const [originalUrl, setOriginalUrl] = useState(null);
  const [colorizedUrl, setColorizedUrl] = useState(null);
  const [isColorizing, setIsColorizing] = useState(false);
  const [modelKey, setModelKey] = useState('ddcolor-tiny');
  const [metrics, setMetrics] = useState(null);

  // Tuning Sliders State
  const [saturation, setSaturation] = useState(1.0);
  const [contrast, setContrast] = useState(1.0);
  const [temperature, setTemperature] = useState(0);
  const [brightness, setBrightness] = useState(0);

  // Vision AI State
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [aiCritique, setAiCritique] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isCritiquing, setIsCritiquing] = useState(false);

  const fileInputRef = useRef(null);

  // Fetch initial system status & hardware info
  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/system/status');
      if (res.ok) {
        const data = await res.json();
        setSystemStatus(data);
        if (data.license) {
          setLicense(data.license);
        }
      }
    } catch (err) {
      console.warn('API server not yet connected:', err);
    }
  };

  const fetchLicense = async () => {
    try {
      const res = await fetch('/api/license/status');
      if (res.ok) {
        const data = await res.json();
        setLicense(data);
      }
    } catch (err) {
      console.warn('Failed to fetch license status:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  // Handle Photo Upload
  const handlePhotoUpload = async (file) => {
    if (!file) return;
    setCurrentFile(file);
    setIsColorizing(true);
    setAiAnalysis(null);
    setAiCritique(null);

    // Create client preview
    const tempUrl = URL.createObjectURL(file);
    setOriginalUrl(tempUrl);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_key', modelKey);
    formData.append('saturation', saturation);
    formData.append('contrast', contrast);
    formData.append('brightness', brightness);
    formData.append('temperature', temperature);

    try {
      const res = await fetch('/api/colorize/photo', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) throw new Error('Colorization failed');
      const data = await res.json();
      setColorizedUrl(data.colorized_url);
      setOriginalUrl(data.original_url);
      setMetrics(data.metrics);
      if (data.ai_analysis) setAiAnalysis(data.ai_analysis);
      confetti({ particleCount: 50, spread: 60, origin: { y: 0.8 } });
    } catch (err) {
      console.error('Error colorizing image:', err);
    } finally {
      setIsColorizing(false);
    }
  };

  // Load a historical sample
  const handleSelectSample = async (samplePath) => {
    try {
      const response = await fetch(samplePath);
      const blob = await response.blob();
      const fileName = samplePath.split('/').pop();
      const file = new File([blob], fileName, { type: blob.type });
      handlePhotoUpload(file);
    } catch (err) {
      console.error('Failed to load sample:', err);
    }
  };

  // Real-time server sync on adjustment change (debounced)
  const adjustTimeoutRef = useRef(null);
  const handleApplyInstant = (deltas) => {
    if (adjustTimeoutRef.current) clearTimeout(adjustTimeoutRef.current);
    adjustTimeoutRef.current = setTimeout(async () => {
      try {
        const formData = new FormData();
        formData.append('saturation', deltas.sat !== undefined ? deltas.sat : saturation);
        formData.append('contrast', deltas.con !== undefined ? deltas.con : contrast);
        formData.append('brightness', deltas.bri !== undefined ? deltas.bri : brightness);
        formData.append('temperature', deltas.temp !== undefined ? deltas.temp : temperature);

        const res = await fetch('/api/adjust', {
          method: 'POST',
          body: formData
        });
        if (res.ok) {
          const data = await res.json();
          setColorizedUrl(data.colorized_url);
        }
      } catch (err) {
        console.error('Adjust error:', err);
      }
    }, 150);
  };

  // Run AI Vision historical inspection
  const handleRunAiAnalysis = async (contextHint) => {
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('context_hint', contextHint || '');
      const res = await fetch('/api/ai/analyze', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        const data = await res.json();
        setAiAnalysis(data);
      }
    } catch (err) {
      console.error('AI Analysis failed:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Run AI Vision critique
  const handleRunAiCritique = async () => {
    setIsCritiquing(true);
    try {
      const res = await fetch('/api/ai/critique', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setAiCritique(data);
        if (data.saturation_delta || data.temperature_delta) {
          const newSat = Math.max(0.5, Math.min(2.0, saturation + (data.saturation_delta || 0)));
          const newTemp = Math.max(-25, Math.min(25, temperature + (data.temperature_delta || 0)));
          setSaturation(newSat);
          setTemperature(newTemp);
          handleApplyInstant({ sat: newSat, temp: newTemp });
        }
      }
    } catch (err) {
      console.error('AI Critique failed:', err);
    } finally {
      setIsCritiquing(false);
    }
  };

  // Apply AI recommended biases
  const handleApplyBiases = ({ sat, con, temp }) => {
    if (sat) setSaturation(sat);
    if (con) setContrast(con);
    if (temp !== undefined) setTemperature(temp);
    handleApplyInstant({ sat, con, temp });
  };

  // Save AI Config
  const handleSaveConfig = async ({ enabled, provider, apiKey, model }) => {
    const formData = new FormData();
    formData.append('enabled', enabled);
    formData.append('provider', provider);
    formData.append('api_key', apiKey);
    formData.append('model', model);
    try {
      await fetch('/api/config/ai', { method: 'POST', body: formData });
      fetchStatus();
    } catch (err) {
      console.error('Failed to save config:', err);
    }
  };

  // Handle Download
  const handleDownload = () => {
    if (!colorizedUrl) return;
    const a = document.createElement('a');
    a.href = colorizedUrl;
    a.download = `dolce_colore_${currentFile?.name || 'restored'}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-amber-500 selection:text-slate-950">
      {/* Cinematic Startup Splash Screen */}
      {showSplash && (
        <SplashScreen
          isReady={Boolean(systemStatus)}
          onFinish={() => setShowSplash(false)}
        />
      )}

      {/* About & Revisited Labs Modal */}
      <AboutModal
        isOpen={showAbout}
        onClose={() => setShowAbout(false)}
        license={license}
        onOpenLicense={() => setShowLicense(true)}
        hardwareLabel={systemStatus?.hardware || 'DirectML GPU'}
      />

      {/* Serial Number & License Management Modal */}
      <LicenseModal
        isOpen={showLicense}
        onClose={() => setShowLicense(false)}
        license={license}
        onLicenseUpdated={fetchLicense}
      />

      {/* Keyboard Shortcuts & Quick Guide Modal */}
      <HelpModal
        isOpen={showHelp}
        onClose={() => setShowHelp(false)}
      />

      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        hardwareLabel={systemStatus?.hardware || 'ONNX Engine Active'}
        hasVisionKey={systemStatus?.ai_config?.has_key}
        onSelectSample={handleSelectSample}
        license={license}
        onOpenAbout={() => setShowAbout(true)}
        onOpenLicense={() => setShowLicense(true)}
        onOpenHelp={() => setShowHelp(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {activeTab === 'photo' && (
          <div className="space-y-6">
            {!colorizedUrl && !isColorizing ? (
              /* Drag & Drop Hero Upload */
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  if (e.dataTransfer.files?.[0]) handlePhotoUpload(e.dataTransfer.files[0]);
                }}
                onClick={() => fileInputRef.current?.click()}
                className="h-[520px] border-2 border-dashed border-slate-800 hover:border-amber-500/60 bg-slate-900/40 hover:bg-slate-900/70 rounded-3xl flex flex-col items-center justify-center gap-4 cursor-pointer transition-all p-8 text-center backdrop-blur-md shadow-2xl group"
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => handlePhotoUpload(e.target.files?.[0])}
                />
                <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 group-hover:scale-110 transition-transform shadow-lg shadow-amber-500/5">
                  <Upload className="w-8 h-8" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-slate-100">
                    Drop Black-and-White Photo Here
                  </h2>
                  <p className="text-xs text-slate-400 mt-1 max-w-md">
                    Instant 1-Click Neural Colorization. Runs 100% locally on your machine with zero cloud upload.
                  </p>
                </div>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-[11px] text-slate-500">Or try an archival classic:</span>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectSample('/samples/Audrey Hepburn.jpg');
                    }}
                    className="text-[11px] font-medium text-amber-400 hover:underline px-2 py-0.5 rounded bg-slate-800 border border-slate-700"
                  >
                    Audrey Hepburn
                  </button>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectSample('/samples/Helen Keller meeting Charlie Chaplin in 1919.jpg');
                    }}
                    className="text-[11px] font-medium text-amber-400 hover:underline px-2 py-0.5 rounded bg-slate-800 border border-slate-700"
                  >
                    Chaplin & Keller 1919
                  </button>
                </div>
              </div>
            ) : (
              /* Photo Studio Canvas & Sidebar Grid */
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Comparison Canvas (2 Columns) */}
                <div className="lg:col-span-2 flex flex-col gap-4">
                  {isColorizing ? (
                    <div className="h-[520px] rounded-2xl bg-slate-900/60 border border-slate-800 flex flex-col items-center justify-center gap-3">
                      <RefreshCw className="w-8 h-8 text-amber-400 animate-spin" />
                      <p className="text-sm font-semibold text-slate-300">
                        Restoring Historical Chrominance...
                      </p>
                      <span className="text-xs text-slate-500">
                        Running local ONNX neural inference
                      </span>
                    </div>
                  ) : (
                    <CompareSlider
                      originalUrl={originalUrl}
                      colorizedUrl={colorizedUrl}
                      saturation={saturation}
                      contrast={contrast}
                      temperature={temperature}
                      brightness={brightness}
                      onDownload={handleDownload}
                    />
                  )}

                  {/* Telemetry Status Bar */}
                  {metrics && !isColorizing && (
                    <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-slate-900/60 border border-slate-800 text-[11px] text-slate-400 font-mono">
                      <div className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                        <span>Rendered in <strong>{metrics.elapsed_ms}ms</strong></span>
                        <span>•</span>
                        <span>{metrics.width}×{metrics.height} px</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          className="text-amber-400 hover:underline font-sans font-semibold text-xs"
                        >
                          Upload New Photo
                        </button>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => handlePhotoUpload(e.target.files?.[0])}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Right Control Panels (1 Column) */}
                <div className="space-y-4">
                  {/* Model Selector Card */}
                  <div className="bg-slate-900/60 rounded-2xl border border-slate-800/80 p-4 shadow-xl backdrop-blur-md space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                        Neural Model
                      </span>
                      <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 px-2 py-0.5 rounded-full">
                        ONNX Runtime
                      </span>
                    </div>
                    <select
                      value={modelKey}
                      onChange={(e) => {
                        const val = e.target.value;
                        setModelKey(val);
                        if (currentFile) handlePhotoUpload(currentFile);
                      }}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200"
                    >
                      <option value="ddcolor-tiny">DDColor-T Tiny (Fast & Lightweight - Recommended)</option>
                      <option value="ddcolor-large">DDColor-L 512 (Photorealistic Detail)</option>
                    </select>
                  </div>

                  {/* Real-time Adjustment Sliders */}
                  <AdjustmentSliders
                    saturation={saturation}
                    setSaturation={setSaturation}
                    contrast={contrast}
                    setContrast={setContrast}
                    temperature={temperature}
                    setTemperature={setTemperature}
                    brightness={brightness}
                    setBrightness={setBrightness}
                    onApplyInstant={handleApplyInstant}
                    disabled={isColorizing || !colorizedUrl}
                  />

                  {/* AI Historical Vision Guide */}
                  <VisionPanel
                    aiAnalysis={aiAnalysis}
                    aiCritique={aiCritique}
                    onRunAnalysis={handleRunAiAnalysis}
                    onRunCritique={handleRunAiCritique}
                    onApplyBiases={handleApplyBiases}
                    onSaveConfig={handleSaveConfig}
                    currentConfig={systemStatus?.ai_config}
                    isAnalyzing={isAnalyzing}
                    isCritiquing={isCritiquing}
                    hasImage={Boolean(colorizedUrl)}
                  />
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'video' && (
          <VideoStudio hardware={systemStatus?.hardware} />
        )}

        {activeTab === 'batch' && (
          <BatchStudio />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/90 py-3 px-6 text-center text-xs text-slate-600 flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center gap-1.5 text-slate-500">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
          <span>100% Private & Offline Colorization • No telemetry • No cloud upload</span>
        </div>
        <div className="flex items-center gap-3 text-slate-500 font-mono text-[11px]">
          <button
            onClick={() => setShowAbout(true)}
            className="hover:text-amber-400 transition-colors cursor-pointer"
          >
            Revisited Labs
          </button>
          <span>•</span>
          <button
            onClick={() => setShowLicense(true)}
            className="hover:text-amber-400 transition-colors cursor-pointer"
          >
            {license?.is_pro ? 'Pro Active' : 'Community Edition'}
          </button>
          <span>•</span>
          <span>v2.0 Native</span>
        </div>
      </footer>
    </div>
  );
}
