import React, { useState, useEffect, useRef } from 'react';
import { Film, Upload, Play, Download, CheckCircle2, AlertCircle, Clock, Zap, Layers } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function VideoStudio({ hardware }) {
  const [videoFile, setVideoFile] = useState(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState(null);
  const [modelKey, setModelKey] = useState('ddcolor-tiny');
  const [mode, setMode] = useState('preview-5s');
  const [customDuration, setCustomDuration] = useState(5);
  const [resolution, setResolution] = useState('original');
  const [sideBySide, setSideBySide] = useState(false);
  const [saturation, setSaturation] = useState(1.0);
  const [temperature, setTemperature] = useState(0);

  // Job State
  const [jobId, setJobId] = useState(null);
  const [jobState, setJobState] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [outputVideoUrl, setOutputVideoUrl] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const fileInputRef = useRef(null);

  const handleFileChange = (file) => {
    if (!file) return;
    setVideoFile(file);
    setVideoPreviewUrl(URL.createObjectURL(file));
    setOutputVideoUrl(null);
    setErrorMsg(null);
    setJobState(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const startColorization = async () => {
    if (!videoFile || isProcessing) return;
    setIsProcessing(true);
    setErrorMsg(null);
    setOutputVideoUrl(null);

    const formData = new FormData();
    formData.append('file', videoFile);
    formData.append('model_key', modelKey);
    formData.append('mode', mode);
    formData.append('custom_duration', customDuration);
    formData.append('resolution', resolution);
    formData.append('side_by_side', sideBySide);
    formData.append('saturation', saturation);
    formData.append('temperature', temperature);

    try {
      const res = await fetch('/api/colorize/video', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) throw new Error('Failed to initiate video colorization job');
      const data = await res.json();
      setJobId(data.job_id);
    } catch (err) {
      setErrorMsg(err.message);
      setIsProcessing(false);
    }
  };

  // Poll job status
  useEffect(() => {
    if (!jobId || !isProcessing) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/video/status/${jobId}`);
        if (!res.ok) return;
        const data = await res.json();
        setJobState(data);

        if (data.status === 'completed') {
          setIsProcessing(false);
          setOutputVideoUrl(data.output_url);
          confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
          clearInterval(interval);
        } else if (data.status === 'failed') {
          setIsProcessing(false);
          setErrorMsg(data.error || 'Video rendering failed.');
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 800);

    return () => clearInterval(interval);
  }, [jobId, isProcessing]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Settings / Controls Column */}
      <div className="space-y-4">
        <div className="bg-slate-900/60 rounded-2xl border border-slate-800/80 p-5 shadow-xl backdrop-blur-md space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800/60 pb-3">
            <Film className="w-4 h-4 text-amber-400" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
              Cinema Video Colorizer
            </h3>
          </div>

          {/* Mode Selection */}
          <div className="space-y-1.5 text-xs">
            <label className="text-slate-300 font-medium">Export Mode</label>
            <select
              value={mode}
              disabled={isProcessing}
              onChange={(e) => setMode(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 focus:outline-none focus:border-amber-500"
            >
              <option value="preview-5s">Preview: First 5 Seconds (Quick Test)</option>
              <option value="preview-10s">Preview: First 10 Seconds</option>
              <option value="custom">Custom Duration (Seconds)</option>
              <option value="full">Full Archival Movie (Complete Render)</option>
            </select>
          </div>

          {mode === 'custom' && (
            <div className="space-y-1 text-xs">
              <label className="text-slate-400">Duration in Seconds</label>
              <input
                type="number"
                min="1"
                max="3600"
                value={customDuration}
                disabled={isProcessing}
                onChange={(e) => setCustomDuration(parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-slate-200"
              />
            </div>
          )}

          {/* Resolution Downscale */}
          <div className="space-y-1.5 text-xs">
            <label className="text-slate-300 font-medium">Output Resolution</label>
            <select
              value={resolution}
              disabled={isProcessing}
              onChange={(e) => setResolution(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200"
            >
              <option value="original">Original Source Resolution</option>
              <option value="720p">Downscale to 720p (Faster Throughput)</option>
              <option value="480p">Downscale to 480p (Ultra-Fast Laptop)</option>
            </select>
          </div>

          {/* Side by side toggle */}
          <label className="flex items-center gap-2.5 text-xs text-slate-300 cursor-pointer pt-1">
            <input
              type="checkbox"
              checked={sideBySide}
              disabled={isProcessing}
              onChange={(e) => setSideBySide(e.target.checked)}
              className="rounded bg-slate-950 border-slate-800 text-amber-500 focus:ring-amber-500"
            />
            <span className="flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-amber-400" />
              Side-by-Side Split Video (B&W Left | Color Right)
            </span>
          </label>

          {/* Saturation Slider */}
          <div className="space-y-1 text-xs pt-2 border-t border-slate-800/60">
            <div className="flex justify-between text-slate-400">
              <span>Saturation Boost</span>
              <span className="font-mono text-amber-400 font-semibold">{saturation.toFixed(2)}×</span>
            </div>
            <input
              type="range"
              min="0.8"
              max="1.6"
              step="0.05"
              value={saturation}
              disabled={isProcessing}
              onChange={(e) => setSaturation(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
            />
          </div>

          {/* Action Button */}
          <button
            onClick={startColorization}
            disabled={!videoFile || isProcessing}
            className="w-full py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-xl transition-all shadow-lg shadow-amber-500/20 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm"
          >
            {isProcessing ? (
              <>
                <Zap className="w-4 h-4 animate-spin text-slate-950" />
                Rendering Frames...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                Start Video Colorization
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Canvas & Video Player Column */}
      <div className="lg:col-span-2 space-y-4">
        {!videoFile ? (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="h-[460px] border-2 border-dashed border-slate-800 hover:border-amber-500/50 bg-slate-950/40 hover:bg-slate-900/40 rounded-2xl flex flex-col items-center justify-center gap-3 cursor-pointer transition-all p-6 text-center"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/quicktime,video/x-matroska,video/avi"
              className="hidden"
              onChange={(e) => handleFileChange(e.target.files?.[0])}
            />
            <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Upload className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-200">
                Drop vintage movie or archival clip here
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Supports MP4, MOV, MKV, AVI • Automatic Audio Preservation
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-slate-900/60 rounded-2xl border border-slate-800/80 p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Film className="w-4 h-4 text-amber-400" />
                <span className="text-xs font-semibold text-slate-200 truncate max-w-[280px]">
                  {videoFile.name}
                </span>
              </div>
              <button
                onClick={() => handleFileChange(null)}
                className="text-xs text-slate-400 hover:text-rose-400 transition-colors"
              >
                Change Video
              </button>
            </div>

            {/* Video Player Display */}
            <div className="aspect-video w-full rounded-xl overflow-hidden bg-black flex items-center justify-center border border-slate-800">
              <video
                src={outputVideoUrl || videoPreviewUrl}
                controls
                className="w-full h-full object-contain"
              />
            </div>

            {/* Live Progress Bar and Throughput telemetry */}
            {isProcessing && jobState && (
              <div className="p-4 rounded-xl bg-slate-950/80 border border-amber-500/30 space-y-3">
                <div className="flex items-center justify-between text-xs font-medium">
                  <span className="flex items-center gap-1.5 text-amber-300">
                    <Zap className="w-4 h-4 animate-bounce text-amber-400" />
                    Colorizing Frame {jobState.frame} of {jobState.total} ({jobState.progress}%)
                  </span>
                  <span className="text-slate-400 font-mono">
                    {jobState.fps} FPS • ETA: {jobState.eta_s}s
                  </span>
                </div>

                <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-amber-500 to-rose-500 h-full rounded-full transition-all duration-300 shadow-md shadow-amber-500/50"
                    style={{ width: `${jobState.progress}%` }}
                  />
                </div>
              </div>
            )}

            {outputVideoUrl && (
              <div className="flex items-center justify-between p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-800/40">
                <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold">
                  <CheckCircle2 className="w-4 h-4" />
                  Video Render Complete! Original Audio Preserved.
                </div>
                <a
                  href={outputVideoUrl}
                  download="dolce_colore_restored.mp4"
                  className="flex items-center gap-1.5 px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg transition-all shadow-md shadow-emerald-500/20"
                >
                  <Download className="w-4 h-4" />
                  Download MP4
                </a>
              </div>
            )}

            {errorMsg && (
              <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-950/50 border border-rose-800/50 text-rose-300 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
                {errorMsg}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
