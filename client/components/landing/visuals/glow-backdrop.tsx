import React from "react";

export function GlowBackdrop() {
  return (
    <div className="fixed inset-0 pointer-events-none z-[-1] overflow-hidden" aria-hidden="true">
      {/* Top central ambient glow */}
      <div className="absolute -top-[300px] left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-b from-violet-600/15 via-cyan-500/10 to-transparent rounded-full blur-[120px]" />
      {/* Mid page subtle glow */}
      <div className="absolute top-[35%] -left-[300px] w-[700px] h-[700px] bg-violet-900/10 rounded-full blur-[140px]" />
      <div className="absolute top-[60%] -right-[300px] w-[700px] h-[700px] bg-cyan-900/10 rounded-full blur-[140px]" />
      {/* Subtle grid pattern overlay */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30" />
      {/* Film grain subtle overlay */}
      <div className="absolute inset-0 film-grain pointer-events-none" />
    </div>
  );
}
