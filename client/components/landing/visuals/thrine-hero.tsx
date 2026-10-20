"use client";

import React, { useState } from "react";
import { ParticleFallback } from "./particle-fallback";
import { usePrefersReducedMotion } from "@/hooks/use-reduced-motion";
import { Sparkles, Play, ShieldAlert } from "lucide-react";

interface ThrineHeroProps {
  sceneId?: string;
  className?: string;
}

export function ThrineHero({
  sceneId = "106eb259-612f-4de7-95a4-ee2133d3af97",
  className = "",
}: ThrineHeroProps) {
  const [useThrineEmbed, setUseThrineEmbed] = useState(false);
  const [iframeLoaded, setIframeLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const prefersReducedMotion = usePrefersReducedMotion();

  // If user prefers reduced motion, always keep particle-fallback / poster mode
  const canEmbed = !prefersReducedMotion;

  return (
    <div
      className={`relative w-full aspect-[16/10] sm:aspect-[16/9] max-h-[580px] rounded-3xl overflow-hidden border border-white/10 bg-[#07080f]/90 shadow-2xl shadow-violet-950/40 backdrop-blur-md ${className}`}
      aria-label="Cinematic 3D particle bloom visualization"
      role="region"
    >
      {/* Self-hosted particle bloom is always active as immediate backdrop or primary view */}
      <ParticleFallback className="absolute inset-0 z-0" />

      {/* Optional Thrine Live 3D Scene Embed (Free Beta reference) */}
      {useThrineEmbed && canEmbed && !hasError && (
        <div className="absolute inset-0 z-10 transition-opacity duration-700">
          {!iframeLoaded && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm z-20">
              <div className="flex items-center gap-3 text-xs font-mono text-violet-300">
                <span className="inline-block w-2 h-2 rounded-full bg-violet-400 animate-ping" />
                Initializing Thrine 3D Scene...
              </div>
            </div>
          )}
          <iframe
            src={`https://thrine.app/embed/${sceneId}?autoplay=true&controls=false&loop=true`}
            title="Thrine Wild Particle Bloom 3D Scene"
            className={`w-full h-full border-0 transition-opacity duration-500 ${
              iframeLoaded ? "opacity-100" : "opacity-0"
            }`}
            loading="lazy"
            allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
            sandbox="allow-scripts allow-same-origin"
            onLoad={() => setIframeLoaded(true)}
            onError={() => setHasError(true)}
          />
        </div>
      )}

      {/* Decorative gradient scrim to maintain high contrast with foreground copy */}
      <div className="absolute inset-0 z-10 pointer-events-none bg-gradient-to-t from-[#06070b] via-transparent to-transparent opacity-80" />
      <div className="absolute inset-0 z-10 pointer-events-none bg-gradient-to-r from-[#06070b]/60 via-transparent to-[#06070b]/60" />

      {/* Interactive Controls Overlay for Tech Demonstration */}
      <div className="absolute bottom-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 rounded-xl bg-black/60 border border-white/10 backdrop-blur-md">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500" />
          </span>
          <span>Mode: {useThrineEmbed ? "Thrine 3D Embed (Beta)" : "Self-Hosted Particle Bloom"}</span>
        </div>

        <div className="flex items-center gap-2">
          {canEmbed && !hasError && (
            <button
              onClick={() => setUseThrineEmbed(!useThrineEmbed)}
              className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-mono transition-colors border bg-white/5 hover:bg-white/10 text-slate-200 border-white/15 cursor-pointer"
              title="Toggle between self-hosted canvas bloom and external Thrine WebGL scene"
            >
              <Sparkles className="w-3.5 h-3.5 text-violet-400" />
              <span>{useThrineEmbed ? "Switch to Canvas" : "Load Thrine 3D Scene"}</span>
            </button>
          )}

          {hasError && (
            <div className="flex items-center gap-1 text-xs text-amber-400 font-mono">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Fallback Active</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
