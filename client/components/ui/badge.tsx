import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "violet" | "cyan" | "muted" | "outline";
}

export function Badge({ className, variant = "violet", children, ...props }: BadgeProps) {
  const variants = {
    violet: "bg-primary/10 text-primary border-primary/25",
    cyan: "bg-teal-400/10 text-teal-200 border-teal-400/25",
    muted: "bg-white/5 text-stone-300 border-white/10",
    outline: "bg-transparent text-stone-300 border-white/20",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-medium border tracking-[0.16em] uppercase font-mono",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
