import React, { useState, useEffect } from 'react';
import { Sparkles, Shield, Cpu } from 'lucide-react';

export default function SplashScreen({ isReady, onFinish }) {
  const [progress, setProgress] = useState(15);
  const [statusText, setStatusText] = useState('Initializing neural engine...');
  const [fadeState, setFadeState] = useState('visible'); // 'visible' | 'fading' | 'hidden'

  useEffect(() => {
    const steps = [
      { pct: 35, text: 'Detecting DirectML GPU acceleration...', delay: 350 },
      { pct: 65, text: 'Calibrating CIE L*a*b* neural weights...', delay: 750 },
      { pct: 90, text: 'Connecting local studio endpoints...', delay: 1100 },
      { pct: 100, text: 'Dolce Colore Studio Ready', delay: 1400 },
    ];

    const timeouts = steps.map((s) =>
      setTimeout(() => {
        setProgress(s.pct);
        setStatusText(s.text);
      }, s.delay)
    );

    // Fade out after completion
    const finishTimeout = setTimeout(() => {
      setFadeState('fading');
      setTimeout(() => {
        setFadeState('hidden');
        if (onFinish) onFinish();
      }, 500);
    }, 1800);

    return () => {
      timeouts.forEach(clearTimeout);
      clearTimeout(finishTimeout);
    };
  }, [onFinish]);

  if (fadeState === 'hidden') return null;

  return (
    <div
      className={`fixed inset-0 z-50 flex flex-col items-center justify-between p-8 bg-[#07090e] transition-opacity duration-500 select-none ${
        fadeState === 'fading' ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      {/* Background ambient glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-32 -left-32 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-32 -right-32 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse" />
      </div>

      {/* Top spacer */}
      <div className="w-full flex justify-between items-center text-[11px] text-slate-500 font-mono">
        <span className="flex items-center gap-1.5">
          <Shield className="w-3.5 h-3.5 text-emerald-400" />
          100% Local & Private AI
        </span>
        <span>v2.0 Native Edition</span>
      </div>

      {/* Center Branding & Progress */}
      <div className="flex flex-col items-center text-center max-w-sm w-full space-y-6 relative z-10">
        {/* Glowing Logo Icon */}
        <div className="relative group">
          <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-amber-500 via-rose-500 to-purple-600 opacity-70 blur-md animate-pulse" />
          <div className="relative w-24 h-24 rounded-2xl bg-slate-950 p-2 border border-slate-800/80 shadow-2xl flex items-center justify-center">
            <img src="/icon.png" alt="Dolce Colore" className="w-20 h-20 rounded-xl object-contain" />
          </div>
        </div>

        {/* Title & Subtitle */}
        <div className="space-y-1.5">
          <h1 className="text-3xl font-black tracking-tight bg-gradient-to-r from-amber-300 via-rose-300 to-purple-300 bg-clip-text text-transparent">
            Dolce Colore
          </h1>
          <p className="text-xs text-slate-400 font-medium tracking-wide">
            Historical Photo & Video Colorizer
          </p>
        </div>

        {/* Progress Bar & Status Text */}
        <div className="w-full space-y-2">
          <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full bg-gradient-to-r from-amber-500 via-rose-500 to-purple-500 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between items-center text-[11px] text-slate-400 font-mono">
            <span className="truncate">{statusText}</span>
            <span className="text-amber-400 font-bold">{progress}%</span>
          </div>
        </div>
      </div>

      {/* Bottom Revisited Labs Credit */}
      <div className="relative z-10 text-center space-y-1">
        <p className="text-[11px] text-slate-500 font-medium">
          Crafted by{' '}
          <span className="text-slate-300 font-semibold hover:text-amber-400 transition-colors">
            Revisited Labs
          </span>
        </p>
        <p className="text-[10px] text-slate-600 font-mono">
          https://revisitedlabs.com
        </p>
      </div>
    </div>
  );
}
