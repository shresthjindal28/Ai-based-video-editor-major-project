import React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "cyan";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", children, disabled, ...props }, ref) => {
    const baseStyles =
      "inline-flex items-center justify-center font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/70 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0c0a09] disabled:pointer-events-none disabled:opacity-50 select-none cursor-pointer rounded-full";

    const variants = {
      primary:
        "bg-gradient-to-r from-[#f3c77a] via-[#e8b86d] to-[#ff8a65] text-[#1a140c] shadow-lg shadow-amber-950/40 hover:brightness-110 border border-amber-200/30 active:scale-[0.98]",
      secondary:
        "bg-white/[0.06] hover:bg-white/[0.1] text-[#f6f1e8] border border-white/12 hover:border-white/22 backdrop-blur-md active:scale-[0.98]",
      outline:
        "border border-white/18 hover:border-primary/50 text-stone-200 hover:text-white bg-transparent hover:bg-white/5 active:scale-[0.98]",
      ghost:
        "text-stone-300 hover:text-white hover:bg-white/6 active:scale-[0.98]",
      cyan:
        "bg-gradient-to-r from-teal-400 to-emerald-400 text-[#0c0a09] font-semibold shadow-lg shadow-teal-950/30 hover:brightness-110 active:scale-[0.98]",
    };

    const sizes = {
      sm: "h-8 px-3.5 text-xs gap-1.5",
      md: "h-10 px-5 text-sm gap-2",
      lg: "h-12 px-6 text-base gap-2.5",
    };

    return (
      <button
        ref={ref}
        disabled={disabled}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
