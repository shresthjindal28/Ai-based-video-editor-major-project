"use client";

import React from "react";
import { NAV_LINKS } from "@/lib/constants/navigation";
import { X, Sparkles, Film, ArrowRight } from "lucide-react";

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenWaitlist: () => void;
}

export function MobileMenu({ isOpen, onClose, onOpenWaitlist }: MobileMenuProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col bg-[#07080f]/95 backdrop-blur-2xl md:hidden animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-label="Mobile Navigation Menu"
    >
      {/* Header bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-violet-900/30">
            <Film className="w-4 h-4 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight text-white">AutoCut<span className="text-violet-400">.ai</span></span>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
          aria-label="Close menu"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {/* Nav items */}
      <nav className="flex flex-col p-6 space-y-4 flex-1 overflow-y-auto">
        {NAV_LINKS.map((link) => (
          <a
            key={link.href}
            href={link.href}
            onClick={onClose}
            className="flex items-center justify-between text-lg font-medium text-slate-200 hover:text-violet-400 py-2 border-b border-white/5 transition-colors"
          >
            <span>{link.label}</span>
            <ArrowRight className="w-4 h-4 text-slate-500" />
          </a>
        ))}
      </nav>

      {/* Footer CTA */}
      <div className="p-6 border-t border-white/10 flex flex-col gap-3">
        <button
          onClick={() => {
            onClose();
            onOpenWaitlist();
          }}
          className="w-full h-12 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 via-violet-500 to-indigo-600 font-semibold text-white shadow-lg shadow-violet-950/50 cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          <span>Get Early Access</span>
        </button>
        <p className="text-center text-xs text-slate-500">Free 10 4K exports during private beta.</p>
      </div>
    </div>
  );
}
