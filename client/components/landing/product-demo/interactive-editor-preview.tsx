"use client";

import React, { useState, useEffect, useRef } from "react";
import { SAMPLE_RAW_CLIPS, DEMO_PRESET_PROMPTS, TIMELINE_CUTS } from "@/lib/constants/demo-data";
import { TimelineTracks } from "./timeline-tracks";
import {
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  CheckCircle2,
  Film,
  Scissors,
} from "lucide-react";
import { Button } from "@/components/ui/button";

export function InteractiveEditorPreview() {
  const [activePrompt, setActivePrompt] = useState(DEMO_PRESET_PROMPTS[0]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStage, setProcessingStage] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSecond, setActiveSecond] = useState(0);
  const [duration, setDuration] = useState(8);
  const [videoError, setVideoError] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const processingTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const selectedCut = TIMELINE_CUTS[1];

  const stages = [
    "Getting the sample clips ready...",
    "Finding the strongest lines and trimming long pauses...",
    "Choosing supporting shots for the story...",
    "Bringing the pacing, music, and look together...",
    "Sample first cut ready for your review"
  ];

  const handleRunAi = () => {
    if (videoRef.current) videoRef.current.currentTime = 0;
    setIsProcessing(true);
    setProcessingStage(0);
    setIsPlaying(false);

    let stage = 0;
    if (processingTimer.current) clearInterval(processingTimer.current);
    processingTimer.current = setInterval(() => {
      stage++;
      if (stage < stages.length) {
        setProcessingStage(stage);
      } else {
        if (processingTimer.current) clearInterval(processingTimer.current);
        setIsProcessing(false);
        setIsPlaying(true);
        setActiveSecond(0);
      }
    }, 700);
  };

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;
    if (isPlaying && !isProcessing) {
      video.play().catch(() => setIsPlaying(false));
    } else {
      video.pause();
    }
  }, [isPlaying, isProcessing]);

  useEffect(() => () => {
    if (processingTimer.current) clearInterval(processingTimer.current);
  }, []);

  const formatTime = (seconds: number) => {
    const whole = Math.floor(seconds);
    return `${Math.floor(whole / 60).toString().padStart(2, "0")}:${(whole % 60).toString().padStart(2, "0")}`;
  };

  return (
    <div className="w-full rounded-[2rem] border border-white/10 bg-[#110e0c] shadow-2xl shadow-amber-950/30 overflow-hidden">
      {/* Top App Header / Bar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-3 border-b border-white/10 bg-[#161210] gap-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-yellow-500/80 inline-block" />
            <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
          </div>
          <span className="text-xs font-mono text-stone-400">
            AutoCut Project: <span className="text-white font-medium">Kitchen_Stories.auto</span>
          </span>
          <span className="hidden sm:inline-block px-2 py-0.5 rounded-full text-[10px] font-mono bg-primary/15 text-primary border border-primary/30">
            Cooking reel · Sample
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              if (videoRef.current) videoRef.current.currentTime = 0;
              setActiveSecond(0);
              setIsPlaying(false);
            }}
            className="p-1.5 text-stone-400 hover:text-white rounded-full hover:bg-white/5 transition-colors cursor-pointer"
            title="Reset preview"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
          <div className="text-xs font-mono text-primary bg-primary/10 border border-primary/25 px-2.5 py-1 rounded-full">
            {`${formatTime(activeSecond)} / ${formatTime(duration)}`}
          </div>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-0 border-b border-white/10">
        {/* Left Column: Media Bin & Presets */}
        <div className="lg:col-span-4 border-r border-white/10 p-4 bg-[#14110f]/50 flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-stone-200 uppercase tracking-wider flex items-center gap-1.5">
                <Film className="w-3.5 h-3.5 text-primary" />
                Raw Footage Bin (4 Clips)
              </span>
                  <span className="text-[10px] text-stone-500 font-mono">Sample media</span>
            </div>

            <div className="space-y-2">
              {SAMPLE_RAW_CLIPS.map((clip) => (
                <div
                  key={clip.id}
                  className="p-2.5 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.05] transition-colors flex items-center justify-between group"
                >
                  <div className="flex items-center gap-2.5">
                    <div className={`w-9 h-7 rounded-md bg-gradient-to-br ${clip.thumbnailColor} border border-white/10 flex items-center justify-center text-[10px] font-mono text-stone-300`}>
                      REC
                    </div>
                    <div>
                      <p className="text-xs font-medium text-stone-200 group-hover:text-white truncate max-w-[140px] sm:max-w-[170px]">
                        {clip.name}
                      </p>
                      <p className="text-[10px] text-stone-500 font-mono">
                        {clip.tag} • {clip.duration}
                      </p>
                    </div>
                  </div>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded-full bg-white/5 text-stone-400">
                    {clip.resolution}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Prompt Director Input */}
          <div className="pt-2 border-t border-white/10">
            <label className="text-xs font-semibold text-stone-200 uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              Your editing brief
            </label>
            <div className="space-y-2">
              <textarea
                value={activePrompt}
                onChange={(e) => setActivePrompt(e.target.value)}
                rows={3}
                className="w-full text-xs font-sans rounded-2xl bg-black/60 border border-white/15 p-2.5 text-stone-200 placeholder-stone-500 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/40 resize-none leading-relaxed"
                placeholder="Describe your editing intent..."
              />
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[10px]">
                <span className="text-stone-500 whitespace-nowrap">Presets:</span>
                {DEMO_PRESET_PROMPTS.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActivePrompt(p)}
                    className="px-2 py-0.5 rounded-full bg-white/5 hover:bg-white/10 text-stone-300 whitespace-nowrap border border-white/10 cursor-pointer"
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
                  <span>Building Sample Cut...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 mr-1" />
                  <span>Build First Cut</span>
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Right Column: Player & AI Cut Inspector */}
        <div className="lg:col-span-8 flex flex-col justify-between bg-black">
          {/* Video Player Display */}
          <div className="relative aspect-video w-full bg-gradient-to-b from-[#181410] to-[#0c0a09] flex items-center justify-center overflow-hidden">
            <video
              ref={videoRef}
              src="/videos/cooking-preview.mp4"
              poster="/videos/cooking-preview.jpg"
              className={`absolute inset-0 h-full w-full object-cover ${isProcessing ? "invisible" : ""}`}
              muted
              loop
              playsInline
              preload="metadata"
              aria-label="Cooking reel sample: a chef frying ingredients in a skillet"
              onLoadedMetadata={(event) => setDuration(event.currentTarget.duration)}
              onTimeUpdate={(event) => setActiveSecond(event.currentTarget.currentTime)}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onError={() => { setVideoError(true); setIsPlaying(false); }}
            />
            {isProcessing ? (
              <div className="flex flex-col items-center justify-center p-6 text-center max-w-md animate-in fade-in duration-300">
                <div className="w-12 h-12 rounded-2xl bg-primary/15 border border-primary/40 flex items-center justify-center mb-4 text-primary animate-pulse">
                  <Sparkles className="w-6 h-6" />
                </div>
                <p className="text-sm font-semibold text-white mb-2">Shaping your sample edit</p>
                <p className="text-xs font-mono text-primary bg-primary/10 border border-primary/25 px-3 py-1.5 rounded-lg">
                  {stages[processingStage]}
                </p>
                <div className="w-48 h-1.5 bg-white/10 rounded-full mt-4 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-amber-400 to-rose-400 transition-all duration-500"
                    style={{ width: `${((processingStage + 1) / stages.length) * 100}%` }}
                  />
                </div>
              </div>
            ) : (
              <div className="relative w-full h-full flex items-center justify-center group">
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20 pointer-events-none" />
                {videoError && <p role="alert" className="absolute inset-x-4 top-16 text-center text-sm text-white">The sample could not load. Refresh to try again.</p>}

                {/* Subtitle Kinetic Overlay */}
                <div className="absolute bottom-12 inset-x-8 text-center pointer-events-none z-10">
                  <span className="inline-block px-3 py-1 rounded bg-black/80 backdrop-blur-md border border-white/10 text-white font-bold text-sm sm:text-base tracking-wide drop-shadow-md">
                    A little heat. <span className="text-primary">A lot of flavor.</span>
                  </span>
                </div>

                {/* Video Info Overlays */}
                <div className="absolute top-3 left-3 z-10 flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-black/60 backdrop-blur-md text-[10px] font-mono text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Warm film look
                  </span>
                  <span className="px-2 py-0.5 rounded bg-black/60 backdrop-blur-md text-[10px] font-mono text-stone-300 border border-white/10">
                    Cooking reel · Muted preview
                  </span>
                </div>

                {/* Play / Pause Center Overlay Button */}
                <button
                  onClick={() => setIsPlaying((playing) => !playing)}
                  disabled={videoError}
                  className="relative z-10 w-16 h-16 rounded-full bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-md flex items-center justify-center text-white transition-transform hover:scale-110 active:scale-95 shadow-xl shadow-black/60 cursor-pointer"
                  aria-label={isPlaying ? "Pause cooking video" : "Play cooking video"}
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
          <div className="px-4 py-2.5 bg-[#14110f] border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-stone-400 font-mono text-[11px] flex items-center gap-1">
                <Scissors className="w-3 h-3 text-primary" />
                Suggested cut:
              </span>
              <span className="px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium border border-primary/20 text-[11px]">
                {selectedCut.label} ({selectedCut.time})
              </span>
            </div>

            <div className="flex items-center gap-1.5 text-[10px] text-stone-400 font-mono">
              <CheckCircle2 className="w-3.5 h-3.5 text-teal-300" />
              <span>Bring the cooking details closer</span>
            </div>
          </div>
        </div>
      </div>

      {/* Multi-Track Interactive Timeline */}
      <TimelineTracks
        activeSecond={activeSecond}
        totalSeconds={duration}
      />
    </div>
  );
}
