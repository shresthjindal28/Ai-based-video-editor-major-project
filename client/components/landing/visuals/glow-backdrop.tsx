import React from "react";

export function GlowBackdrop() {
  return (
    <div className="fixed inset-0 pointer-events-none z-[-1] overflow-hidden" aria-hidden="true">
      <div className="absolute -top-[280px] left-1/2 -translate-x-1/2 w-[1100px] h-[640px] bg-gradient-to-b from-amber-500/18 via-orange-500/8 to-transparent rounded-full blur-[130px]" />
      <div className="absolute top-[32%] -left-[280px] w-[640px] h-[640px] bg-rose-700/12 rounded-full blur-[140px]" />
      <div className="absolute top-[58%] -right-[260px] w-[680px] h-[680px] bg-teal-800/12 rounded-full blur-[140px]" />
      <div className="absolute inset-0 bg-grid-pattern opacity-40" />
      <div className="absolute inset-0 film-grain pointer-events-none" />
    </div>
  );
}
