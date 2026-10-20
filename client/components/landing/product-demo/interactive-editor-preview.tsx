"use client";

import React, { useState, useEffect } from "react";
import { SAMPLE_RAW_CLIPS, DEMO_PRESET_PROMPTS, TIMELINE_CUTS } from "@/lib/constants/demo-data";
import { TimelineTracks } from "./timeline-tracks";
import {
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  Sliders,
  CheckCircle2,
  Film,
  Scissors,
  Layers,
  ArrowRight,
  Maximize2,
  Volume2
} from "lucide-react";
import { Button } from "@/components/ui/button";

export function InteractiveEditorPreview() {
  const [activePrompt, setActivePrompt] = useState(DEMO_PRESET_PROMPTS[0]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSecond, setActiveSecond] = useState(14);
  const [selectedCut, setSelectedCut] = useState(TIMELINE_CUTS[1]);

  const stages = [
    "Ingesting 4K S-Log3 clips & generating lightweight proxies...",
    "Whisper transcribing speech & stripping 4.2s awkward pauses...",
    "Gemini Vision detecting emotion peaks & matching drone B-roll...",
    "Aligning audio cuts with bass drop & applying Kodak 2383 3D LUT...",
    "Master timeline generated • 45s Launch Cut Ready"
  ];

  const handleRunAi = () => {
    setIsProcessing(true);
    setProcessingStage(0);
    setIsPlaying(false);

    let stage = 0;
    const interval = setInterval(() => {
      stage++;
      if (stage < stages.length) {
        setProcessingStage(stage);
      } else {
        clearInterval(interval);
        setIsProcessing(false);
        setIsPlaying(true);
        setActiveSecond(0);
      }
    }, 700);
  };

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isPlaying) {
      timer = setInterval(() => {
        setActiveSecond((prev) => (prev >= 45 ? 0 : prev + 1));
      }, 500);
    }
    return () => clearInterval(timer);
  }, [isPlaying]);

  return (
    <div className="w-full rounded-2xl border border-white/10 bg-[#090b14] shadow-2xl shadow-violet-950/40 overflow-hidden">
      {/* Top App Header / Bar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-3 border-b border-white/10 bg-[#0c0e18] gap-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-yellow-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
          </div>
          <span className="text-xs font-mono text-slate-400">
            AutoCut Project: <span className="text-white font-medium">Coastal_Launch_Cut.auto</span>
          </span>
          <span className="hidden sm:inline-block px-2 py-0.5 rounded text-[10px] font-mono bg-violet-500/20 text-violet-300 border border-violet-500/30">
            4K ProRes 422
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setActiveSecond(0);
              setIsPlaying(false);
            }}
            className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-white/5 transition-colors cursor-pointer"
            title="Reset preview"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <div className="text-xs font-mono text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-2.5 py-1 rounded">
            {`00:${activeSecond.toString().padStart(2, "0")}:18 / 00:45:00`}
          </div>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-0 border-b border-white/10">
        {/* Left Column: Media Bin & Presets */}
        <div className="lg:col-span-4 border-r border-white/10 p-4 bg-[#0a0c16]/50 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
                <Film className="w-3.5 h-3.5 text-violet-400" />
                Raw Footage Bin (4 Clips)
              </span>
              <span className="text-[10px] text-slate-500 font-mono">11.4 GB Ingested</span>
            </div>

            <div className="space-y-2">
              {SAMPLE_RAW_CLIPS.map((clip) => (
                <div
                  key={clip.id}
                  className="p-2.5 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] transition-colors flex items-center justify-between group"
                >
                  <div className="flex items-center gap-2.5">
                    <div className={`w-9 h-7 rounded bg-gradient-to-br ${clip.thumbnailColor} border border-white/10 flex items-center justify-center text-[10px] font-mono text-slate-300`}>
                      REC
                    </div>
                    <div>
                      <p className="text-xs font-medium text-slate-200 group-hover:text-white truncate max-w-[140px] sm:max-w-[170px]">
                        {clip.name}
                      </p>
                      <p className="text-[10px] text-slate-500 font-mono">
                        {clip.tag} • {clip.duration}
                      </p>
                    </div>
                  </div>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-white/5 text-slate-400">
                    {clip.resolution}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Prompt Director Input */}
          <div className="pt-2 border-t border-white/10">
            <label className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              Director Vision Prompt
            </label>
            <div className="space-y-2">
              <textarea
                value={activePrompt}
                onChange={(e) => setActivePrompt(e.target.value)}
                rows={3}
                className="w-full text-xs font-sans rounded-xl bg-black/60 border border-white/15 p-2.5 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-violet-500/60 focus:ring-1 focus:ring-violet-500/40 resize-none leading-relaxed"
                placeholder="Describe your editing intent..."
              />
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[10px]">
                <span className="text-slate-500 whitespace-nowrap">Presets:</span>
                {DEMO_PRESET_PROMPTS.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActivePrompt(p)}
                    className="px-2 py-0.5 rounded-full bg-white/5 hover:bg-white/10 text-slate-300 whitespace-nowrap border border-white/10 cursor-pointer"
                  >
                    Preset {idx + 1}
                  </button>
                ))}
              </div>
            </div>

            <Button
              onClick={handleRunAi}
              disabled={isProcessing}
              variant="primary"
              className="w-full mt-3 h-10 text-xs"
            >
              {isProcessing ? (
                <>
                  <span className="inline-block w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin mr-1" />
                  <span>Autonomous Processing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 mr-1 text-cyan-300" />
                  <span>Generate Autonomous Cut</span>
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Right Column: Player & AI Cut Inspector */}
        <div className="lg:col-span-8 flex flex-col justify-between bg-black">
          {/* Video Player Display */}
          <div className="relative aspect-video w-full bg-gradient-to-b from-[#0e111a] to-[#06070b] flex items-center justify-center overflow-hidden">
            {isProcessing ? (
              <div className="flex flex-col items-center justify-center p-6 text-center max-w-md animate-in fade-in duration-300">
                <div className="w-12 h-12 rounded-2xl bg-violet-600/20 border border-violet-500/40 flex items-center justify-center mb-4 text-violet-300 animate-pulse">
                  <Sparkles className="w-6 h-6" />
                </div>
                <p className="text-sm font-semibold text-white mb-2">AutoCut AI Reasoning</p>
                <p className="text-xs font-mono text-cyan-300 bg-cyan-950/60 border border-cyan-800/40 px-3 py-1.5 rounded-lg">
                  {stages[processingStage]}
                </p>
                <div className="w-48 h-1.5 bg-white/10 rounded-full mt-4 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-violet-500 to-cyan-400 transition-all duration-500"
                    style={{ width: `${((processingStage + 1) / stages.length) * 100}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="relative w-full h-full flex items-center justify-center group">
                {/* Simulated Cinematic Video Frame */}
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-violet-950/40 via-[#070912] to-black" />

                {/* Subtitle Kinetic Overlay */}
                <div className="absolute bottom-12 inset-x-8 text-center pointer-events-none z-10">
                  <span className="inline-block px-3 py-1 rounded bg-black/80 backdrop-blur-md border border-white/10 text-white font-bold text-sm sm:text-base tracking-wide drop-shadow-md">
                    "We built this autonomous editor <span className="text-cyan-400">from the ground up</span>"
                  </span>
                </div>

                {/* Video Info Overlays */}
                <div className="absolute top-3 left-3 z-10 flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-black/60 backdrop-blur-md text-[10px] font-mono text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Kodak 2383 LUT Active
                  </span>
                  <span className="px-2 py-0.5 rounded bg-black/60 backdrop-blur-md text-[10px] font-mono text-slate-300 border border-white/10">
                    Auto-Duck: -18dB
                  </span>
                </div>

                {/* Play / Pause Center Overlay Button */}
                <button
                  onClick={() => setIsPlaying(!isPlaying)}
                  className="relative z-10 w-16 h-16 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-md flex items-center justify-center text-white transition-transform hover:scale-110 active:scale-95 shadow-xl shadow-black/60 cursor-pointer"
                  aria-label={isPlaying ? "Pause simulated playback" : "Play simulated playback"}
                >
                  {isPlaying ? (
                    <Pause className="w-7 h-7 text-white fill-white" />
                  ) : (
                    <Play className="w-7 h-7 text-white fill-white translate-x-0.5" />
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Cut Reasoning Inspector Bar */}
          <div className="px-4 py-2.5 bg-[#0b0e18] border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-mono text-[11px] flex items-center gap-1">
                <Scissors className="w-3 h-3 text-violet-400" />
                Active Cut Decision:
              </span>
              <span className="px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 font-medium border border-violet-500/20 text-[11px]">
                {selectedCut.label} ({selectedCut.time})
              </span>
            </div>

            <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-mono">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
              <span>Grounded in speech pace & beat drop</span>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Track Interactive Timeline */}
      <TimelineTracks
        isPlaying={isPlaying}
        activeSecond={activeSecond}
        totalSeconds={45}
      />
    </div>
  );
}
