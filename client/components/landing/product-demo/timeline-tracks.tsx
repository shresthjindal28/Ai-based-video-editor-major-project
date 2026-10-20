"use client";

import React from "react";
import { Volume2, Type, Video, Film } from "lucide-react";

interface TimelineTracksProps {
  activeSecond: number;
  totalSeconds: number;
}

export function TimelineTracks({ activeSecond, totalSeconds }: TimelineTracksProps) {
  const progressPercent = (activeSecond / totalSeconds) * 100;

  return (
    <div className="w-full bg-[#100e0c] border-t border-white/10 p-3 sm:p-4 select-none font-mono text-xs">
      {/* Timecode header with scrubber head */}
      <div className="relative h-6 border-b border-white/10 mb-2 flex items-center justify-between text-[10px] text-stone-500">
        {[0, 0.25, 0.5, 0.75, 1].map((fraction) => (
          <span key={fraction}>00:{Math.floor(totalSeconds * fraction).toString().padStart(2, "0")}</span>
        ))}

        {/* Playhead line */}
        <div
          className="absolute top-0 bottom-0 w-[2px] bg-primary z-20 transition-all duration-100 ease-linear"
          style={{ left: `${progressPercent}%` }}
        >
          <div className="w-2.5 h-2.5 bg-primary -translate-x-[4px] -top-1 rotate-45" />
        </div>
      </div>

      <div className="space-y-1.5">
        {/* Track V2: B-Roll Cutaways */}
        <div className="flex items-center gap-2 h-7 bg-white/[0.02] rounded px-2">
          <div className="w-16 flex items-center gap-1 text-[10px] text-stone-400 shrink-0">
            <Film className="w-3 h-3 text-rose-300" />
            <span>V2 B-Roll</span>
          </div>
          <div className="flex-1 relative h-5 rounded overflow-hidden bg-black/40">
            <div
              className="absolute left-[18%] w-[22%] h-full bg-gradient-to-r from-rose-600/40 to-orange-600/40 border border-rose-400/40 rounded flex items-center px-1 text-[9px] text-rose-100"
            >
              Skillet_Closeup.mp4
            </div>
            <div
              className="absolute left-[70%] w-[18%] h-full bg-gradient-to-r from-rose-600/40 to-orange-600/40 border border-rose-400/40 rounded flex items-center px-1 text-[9px] text-rose-100"
            >
              Ingredients_Detail.mov
            </div>
          </div>
        </div>

        {/* Track V1: Primary A-Roll */}
        <div className="flex items-center gap-2 h-7 bg-white/[0.02] rounded px-2">
          <div className="w-16 flex items-center gap-1 text-[10px] text-stone-400 shrink-0">
            <Video className="w-3 h-3 text-primary" />
            <span>V1 A-Roll</span>
          </div>
          <div className="flex-1 relative h-5 rounded overflow-hidden bg-black/40 flex gap-0.5">
            <div className="w-[18%] h-full bg-amber-500/30 border border-amber-500/40 rounded flex items-center px-1 text-[9px] text-amber-100 truncate">
              Take 01 [Heat]
            </div>
            <div className="w-[22%] h-full bg-amber-500/20 border border-amber-500/30 rounded flex items-center px-1 text-[9px] text-amber-200 truncate">
              Take 02 [Sizzle]
            </div>
            <div className="w-[30%] h-full bg-amber-500/30 border border-amber-500/40 rounded flex items-center px-1 text-[9px] text-amber-100 truncate">
              Take 03 [Stir]
            </div>
            <div className="flex-1 h-full bg-amber-500/20 border border-amber-500/30 rounded flex items-center px-1 text-[9px] text-amber-200 truncate">
              Take 04 [Finish]
            </div>
          </div>
        </div>

        {/* Track T1: Kinetic Subtitles */}
        <div className="flex items-center gap-2 h-7 bg-white/[0.02] rounded px-2">
          <div className="w-16 flex items-center gap-1 text-[10px] text-stone-400 shrink-0">
            <Type className="w-3 h-3 text-amber-400" />
            <span>T1 Text</span>
          </div>
          <div className="flex-1 relative h-5 rounded overflow-hidden bg-black/40">
            <div className="absolute left-[3%] w-[35%] h-full bg-amber-500/20 border border-amber-500/30 rounded flex items-center px-1 text-[9px] text-amber-200">
              A little heat.
            </div>
            <div className="absolute left-[45%] w-[48%] h-full bg-amber-500/20 border border-amber-500/30 rounded flex items-center px-1 text-[9px] text-amber-200">
              A lot of flavor.
            </div>
          </div>
        </div>

        {/* Track A1 & A2: Audio waveforms */}
        <div className="flex items-center gap-2 h-7 bg-white/[0.02] rounded px-2">
          <div className="w-16 flex items-center gap-1 text-[10px] text-stone-400 shrink-0">
            <Volume2 className="w-3 h-3 text-emerald-400" />
            <span>A1 Audio</span>
          </div>
          <div className="flex-1 relative h-5 rounded overflow-hidden bg-black/40 flex items-center px-1">
            {/* Simulated soundwave */}
            <div className="w-full h-3 flex items-center gap-[2px]">
              {Array.from({ length: 48 }).map((_, i) => {
                const height = 15 + Math.sin(i * 0.4) * 50 + (i % 3 === 0 ? 30 : 0);
                const isDucked = i > 12 && i < 24;
                return (
                  <div
                    key={i}
                    className={`flex-1 rounded-sm transition-all ${
                      isDucked ? "bg-emerald-500/25 h-[25%]" : "bg-emerald-400/70"
                    }`}
                    style={{ height: `${Math.min(100, Math.max(20, height))}%` }}
                  />
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
