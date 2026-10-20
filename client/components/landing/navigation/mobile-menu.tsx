"use client";

import React from "react";
import { NAV_LINKS } from "@/lib/constants/navigation";
import { X, Film, ArrowRight } from "lucide-react";

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenWaitlist: () => void;
}

export function MobileMenu({ isOpen, onClose, onOpenWaitlist }: MobileMenuProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col bg-[#0c0a09]/96 backdrop-blur-2xl lg:hidden"
      role="dialog"
      aria-modal="true"
      aria-label="Mobile Navigation Menu"
    >
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-amber-400 to-rose-400 flex items-center justify-center">
            <Film className="w-4 h-4 text-[#1a140c]" />
          </div>
          <span className="font-semibold text-lg tracking-tight text-white">
            AutoCut<span className="font-serif italic text-primary"> AI</span>
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-2 rounded-full text-stone-400 hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
          aria-label="Close menu"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      <nav className="flex flex-col p-6 space-y-2 flex-1 overflow-y-auto">
        {NAV_LINKS.map((link) => (
          <a
            key={link.href}
            href={link.href}
            onClick={onClose}
            className="flex items-center justify-between text-lg font-medium text-stone-200 hover:text-primary py-3 border-b border-white/6 transition-colors"
          >
            <span>{link.label}</span>
            <ArrowRight className="w-4 h-4 text-stone-500" />
          </a>
        ))}
      </nav>

      <div className="p-6 border-t border-white/10 flex flex-col gap-3">
        <button
          onClick={() => {
            onClose();
            onOpenWaitlist();
          }}
          className="w-full h-12 flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-[#f3c77a] via-[#e8b86d] to-[#ff8a65] font-semibold text-[#1a140c] cursor-pointer"
        >
          <span>Get Early Access</span>
        </button>
        <p className="text-center text-xs text-stone-500">Free 10 4K exports during private beta.</p>
      </div>
    </div>
  );
}
