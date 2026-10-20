"use client";

import React, { useState } from "react";
import { NAV_LINKS } from "@/lib/constants/navigation";
import { useScrollPosition } from "@/hooks/use-scroll-position";
import { MobileMenu } from "./mobile-menu";
import { Film, Menu, Sparkles, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NavbarProps {
  onOpenWaitlist?: () => void;
}

export function Navbar({ onOpenWaitlist }: NavbarProps) {
  const scrollY = useScrollPosition();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isScrolled = scrollY > 20;

  const handleWaitlistClick = () => {
    if (onOpenWaitlist) {
      onOpenWaitlist();
    } else {
      const cta = document.getElementById("cta");
      cta?.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <>
      <header
        className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
          isScrolled
            ? "bg-[#06070b]/80 backdrop-blur-xl border-b border-white/10 shadow-lg shadow-black/40 py-3.5"
            : "bg-transparent py-5"
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between">
          {/* Logo */}
          <a
            href="#"
            className="flex items-center gap-2.5 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-400 rounded-lg p-1"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-violet-600 via-fuchsia-600 to-cyan-400 p-[1px] shadow-lg shadow-violet-900/30 group-hover:shadow-violet-600/40 transition-shadow">
              <div className="w-full h-full bg-[#090b14] rounded-[11px] flex items-center justify-center">
                <Film className="w-4 h-4 text-violet-300 group-hover:text-cyan-300 transition-colors" />
              </div>
            </div>
            <div className="flex flex-col">
              <span className="font-extrabold text-lg tracking-tight text-white flex items-center gap-1">
                AutoCut
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-400">
                  AI
                </span>
              </span>
            </div>
          </a>

          {/* Desktop Navigation */}
          <nav
            className="hidden md:flex items-center gap-1 px-4 py-1.5 rounded-full border border-white/10 bg-white/[0.03] backdrop-blur-md"
            aria-label="Main Navigation"
          >
            {NAV_LINKS.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="px-3.5 py-1.5 text-xs font-medium text-slate-300 hover:text-white hover:bg-white/10 rounded-full transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-400"
              >
                {item.label}
              </a>
            ))}
          </nav>

          {/* Actions */}
          <div className="hidden sm:flex items-center gap-3">
            <a
              href="#demo"
              className="text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-400 rounded-lg"
            >
              Sign In
            </a>
            <Button
              size="sm"
              variant="primary"
              onClick={handleWaitlistClick}
              className="text-xs px-4 py-2"
            >
              <Sparkles className="w-3.5 h-3.5 mr-1" />
              <span>Get Started</span>
              <ArrowRight className="w-3 h-3 ml-0.5" />
            </Button>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 md:hidden cursor-pointer"
            aria-label="Open mobile navigation menu"
          >
            <Menu className="w-6 h-6" />
          </button>
        </div>
      </header>

      {/* Mobile Menu */}
      <MobileMenu
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        onOpenWaitlist={handleWaitlistClick}
      />
    </>
  );
}
