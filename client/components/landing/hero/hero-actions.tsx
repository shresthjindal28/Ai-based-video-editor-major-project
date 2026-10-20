"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Sparkles, Play, CheckCircle2, ArrowRight } from "lucide-react";

interface HeroActionsProps {
  onOpenWaitlist?: () => void;
}

export function HeroActions({ onOpenWaitlist }: HeroActionsProps) {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setSubmitted(true);
    setTimeout(() => {
      if (onOpenWaitlist) onOpenWaitlist();
    }, 400);
  };

  const scrollToDemo = () => {
    document.getElementById("demo")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full max-w-xl mx-auto">
      {submitted ? (
        <div className="flex items-center gap-2 px-5 py-3 rounded-xl bg-violet-950/60 border border-violet-500/40 text-violet-200 text-sm font-medium animate-in fade-in duration-300">
          <CheckCircle2 className="w-5 h-5 text-cyan-400" />
          <span>You're on the early access list! 10 free renders unlocked.</span>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex w-full sm:w-auto items-center gap-2 flex-1">
          <div className="relative flex-1">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your creator email..."
              className="w-full h-12 px-4 rounded-xl bg-white/[0.06] border border-white/15 focus:border-violet-400 focus:ring-2 focus:ring-violet-500/30 text-white placeholder-slate-400 text-sm outline-none transition-all shadow-inner backdrop-blur-md"
              required
            />
          </div>
          <Button type="submit" size="lg" variant="primary" className="whitespace-nowrap">
            <Sparkles className="w-4 h-4 mr-1 text-cyan-300" />
            <span>Claim Access</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </form>
      )}

      <Button
        type="button"
        variant="secondary"
        size="lg"
        onClick={scrollToDemo}
        className="w-full sm:w-auto text-slate-300 hover:text-white"
      >
        <Play className="w-4 h-4 mr-1 text-violet-400 fill-violet-400" />
        <span>Watch Demo</span>
      </Button>
    </div>
  );
}
