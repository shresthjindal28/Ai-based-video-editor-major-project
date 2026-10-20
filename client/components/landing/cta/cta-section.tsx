"use client";

import React, { useState } from "react";
import { ArrowRight, CheckCircle2, ShieldCheck, Zap } from "lucide-react";
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
        <div className="relative rounded-[2rem] border border-primary/25 bg-gradient-to-b from-[#1d1812] via-[#14110e] to-[#0e0c0a] p-8 sm:p-14 text-center shadow-2xl shadow-amber-950/30 overflow-hidden">
          <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-96 h-96 bg-gradient-to-r from-amber-500/25 to-rose-500/15 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute inset-0 bg-grid-pattern opacity-20 pointer-events-none" />

          <div className="relative z-10 max-w-2xl mx-auto">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-medium bg-primary/10 text-primary border border-primary/25 mb-6 tracking-[0.14em] uppercase">
              Private beta now open
            </span>

            <h2 className="font-serif text-4xl sm:text-5xl lg:text-6xl tracking-tight text-[#fff8ee] leading-[1.1]">
              Turn your clips into a{" "}
              <span className="italic text-gradient-primary">story.</span>
            </h2>

            <p className="mt-5 text-base sm:text-lg text-stone-300/90 leading-relaxed">
              Stop drowning in raw footage and tedious cuts. Claim early access to AutoCut AI and deliver broadcast-grade first cuts in under 2 minutes.
            </p>

            {submitted ? (
              <div className="mt-8 flex items-center justify-center gap-2 p-4 rounded-2xl bg-teal-950/40 border border-teal-500/30 text-teal-100 text-sm font-medium">
                <CheckCircle2 className="w-5 h-5 text-teal-300" />
                <span>You&apos;re registered for beta access. Check your inbox for activation details.</span>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-2 max-w-md mx-auto p-1.5 rounded-full border border-white/12 bg-black/30">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  className="w-full sm:flex-1 h-11 px-4 rounded-full bg-transparent text-white placeholder-stone-500 text-sm outline-none"
                />
                <Button type="submit" size="lg" variant="primary" className="w-full sm:w-auto">
                  <span>Get Started</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </form>
            )}

            <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-stone-400 font-mono">
              <div className="flex items-center gap-1.5">
                <Zap className="w-3.5 h-3.5 text-primary" />
                <span>10 free 4K exports included</span>
              </div>
              <span className="text-white/15">•</span>
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-teal-300" />
                <span>No credit card required</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
