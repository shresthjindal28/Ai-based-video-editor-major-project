import React from "react";

export function HeroPoster({ className = "" }: { className?: string }) {
  return (
    <div
      className={`relative w-full h-full overflow-hidden rounded-3xl bg-[#080912] border border-white/10 ${className}`}
      aria-hidden="true"
    >
      <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 bg-violet-600/25 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 -left-20 w-80 h-80 bg-cyan-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-10 w-96 h-96 bg-fuchsia-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute inset-0 bg-grid-pattern opacity-40 pointer-events-none" />
    </div>
  );
}
