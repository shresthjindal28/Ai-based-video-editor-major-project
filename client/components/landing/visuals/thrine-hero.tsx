"use client";

import { createElement, useState } from "react";
import Script from "next/script";
import { ParticleFallback } from "./particle-fallback";
import { usePrefersReducedMotion } from "@/hooks/use-reduced-motion";

export function ThrineHero({ className = "" }: { className?: string }) {
  const prefersReducedMotion = usePrefersReducedMotion();
  const [playScene, setPlayScene] = useState(false);
  const [hasError, setHasError] = useState(false);
  const showScene = (!prefersReducedMotion || playScene) && !hasError;

  return (
    <div className={`relative w-full overflow-hidden rounded-[2rem] border border-white/10 bg-[#110e0c] shadow-2xl ${className}`}>
      {showScene ? (
        <>
          <Script
            src="https://thrine.app/embed/v1.js"
            type="module"
            strategy="afterInteractive"
            onError={() => setHasError(true)}
          />
          {createElement("model-embed", {
            project: "e_47f3c16edd3ad93f7e0f",
            style: { display: "block", width: "100%", aspectRatio: "1297 / 858" },
            "aria-label": "Interactive 3D scene",
          })}
        </>
      ) : (
        <div className="relative w-full aspect-[1297/858]">
          <ParticleFallback className="absolute inset-0" />
          {!hasError && (
            <button className="absolute bottom-6 left-1/2 -translate-x-1/2 rounded-full border border-white/20 bg-black/70 px-5 py-2 text-sm text-white cursor-pointer" onClick={() => setPlayScene(true)}>
              Play 3D scene
            </button>
          )}
        </div>
      )}
    </div>
  );
}
