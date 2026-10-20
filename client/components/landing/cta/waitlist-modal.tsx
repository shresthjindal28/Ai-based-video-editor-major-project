"use client";

import React, { useState } from "react";
import { X, CheckCircle2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WaitlistModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function WaitlistModal({ isOpen, onClose }: WaitlistModalProps) {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setSubmitted(true);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-xl"
      role="dialog"
      aria-modal="true"
      aria-label="Join AutoCut AI Private Beta"
    >
      <div className="relative w-full max-w-md rounded-3xl border border-primary/25 bg-[#14110e] p-6 shadow-2xl shadow-amber-950/40">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-full text-stone-400 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {submitted ? (
          <div className="py-6 flex flex-col items-center text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-teal-500/15 border border-teal-500/30 flex items-center justify-center text-teal-300">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-serif text-white">You&apos;re on the private beta list</h3>
            <p className="text-sm text-stone-300">
              We&apos;ve dispatched an invitation packet to <span className="text-primary font-mono">{email}</span>. Explore a faster starting point for your next edit.
            </p>
            <div className="p-3 rounded-2xl bg-white/5 border border-white/10 w-full text-center">
              <span className="text-xs font-mono text-stone-400">Invitation ticket</span>
              <p className="text-sm font-mono font-bold text-primary mt-1">AUTOCUT-VIP-2026</p>
            </div>
            <Button onClick={onClose} variant="primary" className="w-full">
              Back to the page
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-serif text-white">Claim early access</h3>
              <p className="text-xs text-stone-400 mt-1">Early access for video editors</p>
            </div>

            <p className="text-sm text-stone-300 leading-relaxed">
              Spend more of your editing day on the story. Join the beta to explore first cuts, dialogue cleanup, and social cutdowns.
            </p>

            <form onSubmit={handleSubmit} className="space-y-3 pt-2">
              <div>
                <label className="block text-xs font-mono text-stone-400 mb-1.5">
                  Email address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex@studio.com"
                  required
                  className="w-full h-11 px-3.5 rounded-full bg-black/50 border border-white/12 focus:border-primary/60 focus:ring-2 focus:ring-primary/20 text-white placeholder-stone-500 text-sm outline-none transition-all"
                />
              </div>

              <Button type="submit" variant="primary" className="w-full h-11">
                <span>Unlock Early Access</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </form>

            <p className="text-[11px] text-center text-stone-500 font-mono">
              Zero credit card required. No spam.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
