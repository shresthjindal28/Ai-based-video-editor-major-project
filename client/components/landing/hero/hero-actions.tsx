"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Play, CheckCircle2, ArrowRight } from "lucide-react";

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
    <div className="flex flex-col sm:flex-row items-center justify-center gap-3 w-full max-w-xl mx-auto">
      {submitted ? (
        <div className="flex items-center gap-2 px-5 py-3 rounded-full bg-teal-950/50 border border-teal-500/30 text-teal-100 text-sm font-medium">
          <CheckCircle2 className="w-5 h-5 text-teal-300" />
          <span>You&apos;re on the early access list. 10 free renders unlocked.</span>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex w-full sm:w-auto items-center gap-2 flex-1 p-1.5 rounded-full border border-white/12 bg-white/[0.04] backdrop-blur-md">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Your creator email"
            className="w-full h-10 px-4 rounded-full bg-transparent text-white placeholder-stone-500 text-sm outline-none"
            required
          />
          <Button type="submit" size="md" variant="primary" className="whitespace-nowrap shrink-0">
            <span>Claim Access</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </form>
      )}

      <Button
        type="button"
        variant="secondary"
        size="lg"
        onClick={scrollToDemo}
        className="w-full sm:w-auto"
      >
        <Play className="w-4 h-4 fill-primary text-primary" />
        <span>Watch Demo</span>
      </Button>
    </div>
  );
}
