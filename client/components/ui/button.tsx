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
      "inline-flex items-center justify-center font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-400 focus-visible:ring-offset-2 focus-visible:ring-offset-black disabled:pointer-events-none disabled:opacity-50 select-none cursor-pointer rounded-xl";

    const variants = {
      primary:
        "bg-gradient-to-r from-violet-600 via-violet-500 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg shadow-violet-900/30 hover:shadow-violet-700/40 border border-violet-400/20 active:scale-[0.98]",
      secondary:
        "bg-white/10 hover:bg-white/15 text-white border border-white/10 hover:border-white/20 backdrop-blur-md active:scale-[0.98]",
      outline:
        "border border-white/20 hover:border-white/40 text-slate-200 hover:text-white bg-transparent hover:bg-white/5 active:scale-[0.98]",
      ghost:
        "text-slate-300 hover:text-white hover:bg-white/5 active:scale-[0.98]",
      cyan:
        "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-semibold shadow-lg shadow-cyan-900/30 hover:shadow-cyan-700/40 active:scale-[0.98]",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs gap-1.5",
      md: "h-10 px-4 text-sm gap-2",
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
