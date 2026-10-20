"use client";

import React, { useState } from "react";
import { Sparkles, ArrowRight, CheckCircle2, ShieldCheck, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CtaSectionProps {
  onOpenWaitlist?: () => void;
}

export function CtaSection({ onOpenWaitlist }: CtaSectionProps) {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setSubmitted(true);
    if (onOpenWaitlist) {
      setTimeout(onOpenWaitlist, 500);
    }
  };

  return (
    <section className="py-24 sm:py-32 relative overflow-hidden" id="cta">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="relative rounded-3xl border border-violet-500/30 bg-gradient-to-b from-[#121426]/90 via-[#0d0f1c]/95 to-[#080911] p-8 sm:p-14 text-center shadow-2xl shadow-violet-950/40 backdrop-blur-2xl overflow-hidden">
          {/* Internal atmospheric glow */}
          <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-96 h-96 bg-gradient-to-r from-violet-600/30 to-cyan-500/20 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />

          <div className="relative z-10 max-w-2xl mx-auto">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium bg-violet-500/10 text-violet-300 border border-violet-500/20 mb-6">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              Private Beta Now Open
            </span>

            <h2 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-[1.1]">
              Turn your clips into a{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-fuchsia-300 to-cyan-300">
                story.
              </span>
            </h2>

            <p className="mt-5 text-base sm:text-lg text-slate-300/90 leading-relaxed">
              Stop drowning in raw footage and tedious cuts. Claim early access to AutoCut AI and deliver broadcast-grade first cuts in under 2 minutes.
            </p>

            {submitted ? (
              <div className="mt-8 flex items-center justify-center gap-2 p-4 rounded-xl bg-violet-950/60 border border-violet-500/40 text-violet-200 text-sm font-medium">
                <CheckCircle2 className="w-5 h-5 text-cyan-400" />
                <span>You're registered for beta access! Check your inbox for activation details.</span>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3 max-w-md mx-auto">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email..."
                  required
                  className="w-full sm:flex-1 h-12 px-4 rounded-xl bg-white/[0.06] border border-white/20 focus:border-violet-400 focus:ring-2 focus:ring-violet-500/30 text-white placeholder-slate-400 text-sm outline-none transition-all shadow-inner backdrop-blur-md"
                />
                <Button type="submit" size="lg" variant="primary" className="w-full sm:w-auto">
                  <span>Get Started</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </form>
            )}

            <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400 font-mono">
              <div className="flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                <span>10 Free 4K Exports Included</span>
              </div>
              <span className="text-white/20">•</span>
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>No Credit Card Required</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
