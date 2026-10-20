import React from "react";
import { Sparkles } from "lucide-react";

export function HeroBadge() {
  return (
    <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-primary/25 bg-primary/10 backdrop-blur-md">
      <span className="flex h-2 w-2 relative">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
      </span>
      <span className="text-[11px] font-mono font-medium text-primary tracking-[0.14em] uppercase">
        Private Beta 2.0
      </span>
      <span className="text-white/20">•</span>
      <span className="text-xs font-medium text-stone-300 hidden sm:inline-flex items-center gap-1">
        <Sparkles className="w-3 h-3 text-teal-300" />
        Multi-modal grounded timeline
      </span>
    </div>
  );
}
