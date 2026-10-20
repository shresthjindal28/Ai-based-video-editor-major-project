import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "violet" | "cyan" | "muted" | "outline";
}

export function Badge({ className, variant = "violet", children, ...props }: BadgeProps) {
  const variants = {
    violet: "bg-violet-500/10 text-violet-300 border-violet-500/20",
    cyan: "bg-cyan-500/10 text-cyan-300 border-cyan-500/20",
    muted: "bg-white/5 text-slate-300 border-white/10",
    outline: "bg-transparent text-slate-300 border-white/20",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border tracking-wide uppercase font-mono",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
