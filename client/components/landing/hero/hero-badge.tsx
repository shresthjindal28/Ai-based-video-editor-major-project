import React from "react";
import { Sparkles } from "lucide-react";

export function HeroBadge() {
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-violet-500/30 bg-violet-500/10 backdrop-blur-md shadow-sm shadow-violet-500/10">
      <span className="flex h-2 w-2 relative">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
        <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-500" />
      </span>
      <span className="text-xs font-mono font-medium text-violet-300 tracking-wide uppercase">
        AutoCut AI 2.0 Private Beta
      </span>
      <span className="text-white/20">•</span>
      <span className="text-xs font-medium text-slate-300 hidden sm:inline flex items-center gap-1">
        <Sparkles className="w-3 h-3 text-cyan-400" />
        Multi-Modal Grounded Timeline
      </span>
    </div>
  );
}
