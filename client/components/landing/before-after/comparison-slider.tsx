"use client";

import React, { useState, useRef, useCallback } from "react";
import { Sliders, Volume2, VolumeX, Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";

export function ComparisonSlider() {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [activeTab, setActiveTab] = useState<"visual" | "audio">("visual");
  const containerRef = useRef<HTMLDivElement | null>(null);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const percent = Math.min(Math.max((x / rect.width) * 100, 5), 95);
      setSliderPosition(percent);
    },
    []
  );

  const handleTouchMove = (e: React.TouchEvent) => {
    handleMove(e.touches[0].clientX);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      handleMove(e.clientX);
    }
  };

  return (
    <div className="w-full flex flex-col items-center">
      {/* Mode Switcher */}
      <div className="flex items-center gap-2 p-1 rounded-xl bg-white/5 border border-white/10 mb-6">
        <button
          onClick={() => setActiveTab("visual")}
          className={`px-4 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
            activeTab === "visual"
              ? "bg-violet-600 text-white shadow-md shadow-violet-900/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Visual & Color Grading
        </button>
        <button
          onClick={() => setActiveTab("audio")}
          className={`px-4 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
            activeTab === "audio"
              ? "bg-violet-600 text-white shadow-md shadow-violet-900/40"
              : "text-slate-400 hover:text-white"
          }`}
        >
          Voice Isolation & Sound Design
        </button>
      </div>

      {/* Main Interactive Comparison Container */}
      <div
        ref={containerRef}
        onMouseDown={() => setIsDragging(true)}
        onMouseUp={() => setIsDragging(false)}
        onMouseLeave={() => setIsDragging(false)}
        onMouseMove={handleMouseMove}
        onTouchMove={handleTouchMove}
        className="relative w-full aspect-[16/10] sm:aspect-[16/9] max-h-[540px] rounded-2xl overflow-hidden border border-white/15 shadow-2xl shadow-violet-950/30 select-none cursor-ew-resize bg-[#090b14]"
        role="region"
        aria-label="Before and after video comparison slider"
      >
        {/* Right Layer (After: AutoCut AI Master) - Fully visible underneath */}
        <div className="absolute inset-0 bg-gradient-to-tr from-[#121422] via-[#1a1230] to-[#091b29] flex items-center justify-center p-6">
          {/* Visual simulation of graded, punchy frame */}
          <div className="w-full h-full flex flex-col items-center justify-center relative">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-violet-500/20 via-cyan-500/10 to-transparent" />
            
            {/* Subject Simulation */}
            <div className="relative z-10 flex flex-col items-center">
              <div className="w-28 h-28 sm:w-36 sm:h-36 rounded-full bg-gradient-to-tr from-amber-200 via-rose-300 to-amber-100 shadow-2xl shadow-amber-500/20 border-2 border-amber-300/40 flex items-center justify-center text-slate-900 font-bold text-xs">
                Cinematic Lighting
              </div>
              <div className="mt-4 px-4 py-1.5 rounded-lg bg-black/80 backdrop-blur-md border border-cyan-400/40 text-cyan-300 font-mono text-xs sm:text-sm font-bold shadow-lg">
                AutoCut Master • Kodak 2383 LUT • Studio Audio
              </div>
            </div>

            {/* After details tags */}
            <div className="absolute top-4 right-4 z-20 flex flex-col gap-2 items-end">
              <span className="px-3 py-1 rounded-full bg-cyan-500/20 border border-cyan-400/40 text-cyan-300 font-mono text-[11px] font-bold">
                AFTER: AutoCut AI
              </span>
              <div className="hidden sm:flex flex-col gap-1 items-end text-[10px] text-slate-300 font-mono bg-black/60 p-2 rounded border border-white/10">
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Voice Isolation (-35dB hiss)
                </span>
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> 3D Rec.709 Color Grade
                </span>
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Word-by-word Subtitles
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Left Layer (Before: Raw S-Log3 Footage) - Clipped by sliderPosition */}
        <div
          className="absolute inset-0 overflow-hidden bg-[#1a1b1f] border-r border-cyan-400/80"
          style={{ width: `${sliderPosition}%` }}
        >
          <div
            className="absolute inset-0 w-full h-full flex items-center justify-center p-6 bg-gradient-to-br from-[#16171a] to-[#202227] filter grayscale-[45%] brightness-[85%] contrast-[75%]"
            style={{ width: containerRef.current?.clientWidth || "100%" }}
          >
            {/* Flat uncalibrated simulation */}
            <div className="relative z-10 flex flex-col items-center">
              <div className="w-28 h-28 sm:w-36 sm:h-36 rounded-full bg-slate-400/60 border border-slate-500/40 flex items-center justify-center text-slate-300 font-mono text-xs">
                Flat Log Profile
              </div>
              <div className="mt-4 px-4 py-1.5 rounded-lg bg-black/70 border border-white/10 text-slate-400 font-mono text-xs sm:text-sm">
                Raw S-Log3 • Awkward Pauses • Room Hum
              </div>
            </div>

            {/* Before details tags */}
            <div className="absolute top-4 left-4 z-20 flex flex-col gap-2 items-start">
              <span className="px-3 py-1 rounded-full bg-slate-700/80 border border-slate-500 text-slate-200 font-mono text-[11px] font-bold">
                BEFORE: Raw Ingest
              </span>
              <div className="hidden sm:flex flex-col gap-1 items-start text-[10px] text-slate-400 font-mono bg-black/60 p-2 rounded border border-white/10">
                <span className="text-red-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> Unprocessed Log Gamma
                </span>
                <span className="text-red-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> 8.4s Dead Silence & Stutters
                </span>
                <span className="text-red-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> Unmixed 60Hz AC Hum
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Divider scrubber line & handle */}
        <div
          className="absolute top-0 bottom-0 w-[2px] bg-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.8)] z-30"
          style={{ left: `${sliderPosition}%` }}
        >
          <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-9 h-9 rounded-full bg-cyan-400 text-black flex items-center justify-center shadow-lg shadow-cyan-950/80 border-2 border-white">
            <Sliders className="w-4 h-4 rotate-90" />
          </div>
        </div>
      </div>

      {/* Instructional helper below slider */}
      <p className="mt-3 text-xs text-slate-400 font-mono flex items-center gap-1.5">
        <Sliders className="w-3.5 h-3.5 text-cyan-400" />
        <span>Drag slider horizontally or swipe to inspect the transformation</span>
      </p>
    </div>
  );
}
