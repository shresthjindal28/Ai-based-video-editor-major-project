"use client";

import React, { useState } from "react";
import { X, Sparkles, CheckCircle2, ArrowRight } from "lucide-react";
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
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-label="Join AutoCut AI Private Beta"
    >
      <div className="relative w-full max-w-md rounded-2xl border border-violet-500/30 bg-[#0e111d] p-6 shadow-2xl shadow-violet-950/50">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {submitted ? (
          <div className="py-6 flex flex-col items-center text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">You're On The Private Beta List</h3>
            <p className="text-sm text-slate-300">
              We've dispatched an invitation packet to <span className="text-cyan-300 font-mono">{email}</span>. Your key unlocks 10 free 4K renders and NLE XML exports.
            </p>
            <div className="p-3 rounded-xl bg-white/5 border border-white/10 w-full text-center">
              <span className="text-xs font-mono text-slate-400">Invitation Ticket:</span>
              <p className="text-sm font-mono font-bold text-violet-300 mt-1">AUTOCUT-VIP-2026</p>
            </div>
            <Button onClick={onClose} variant="primary" className="w-full">
              Back to Experience
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-violet-600/20 border border-violet-500/30 flex items-center justify-center text-cyan-400">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Claim Early Access</h3>
                <p className="text-xs text-slate-400">Limited rollout • 10 complimentary 4K exports</p>
              </div>
            </div>

            <p className="text-sm text-slate-300 leading-relaxed">
              Experience the autonomous video director before public release. Connect your Sony, Apple, or Canon footage and cut in minutes.
            </p>

            <form onSubmit={handleSubmit} className="space-y-3 pt-2">
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1.5">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex@studio.com"
                  required
                  className="w-full h-11 px-3.5 rounded-xl bg-black/60 border border-white/15 focus:border-violet-400 focus:ring-2 focus:ring-violet-500/30 text-white placeholder-slate-500 text-sm outline-none transition-all"
                />
              </div>

              <Button type="submit" variant="primary" className="w-full h-11">
                <span>Unlock Early Access</span>
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </form>

            <p className="text-[11px] text-center text-slate-500 font-mono">
              Zero credit card required. No spam guaranteed.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
