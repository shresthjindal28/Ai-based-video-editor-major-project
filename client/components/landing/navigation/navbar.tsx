"use client";

import React, { useState } from "react";
import { NAV_LINKS } from "@/lib/constants/navigation";
import { useScrollPosition } from "@/hooks/use-scroll-position";
import { MobileMenu } from "./mobile-menu";
import { Film, Menu, ArrowRight } from "lucide-react";
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
          isScrolled ? "py-3" : "py-5"
        }`}
      >
        <div
          className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between rounded-full transition-all duration-300 ${
            isScrolled
              ? "bg-[#110e0c]/80 backdrop-blur-xl border border-white/10 shadow-lg shadow-black/30 py-2.5 px-4 sm:px-5"
              : "bg-transparent py-1"
          }`}
        >
          <a
            href="#"
            className="flex items-center gap-2.5 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/70 rounded-full p-1"
          >
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-amber-400 via-orange-400 to-rose-400 p-[1px] shadow-lg shadow-amber-900/30">
              <div className="w-full h-full bg-[#110e0c] rounded-[14px] flex items-center justify-center">
                <Film className="w-4 h-4 text-amber-200 group-hover:text-teal-200 transition-colors" />
              </div>
            </div>
            <span className="font-semibold text-lg tracking-tight text-[#f6f1e8]">
              AutoCut
              <span className="font-serif italic text-primary ml-1">AI</span>
            </span>
          </a>

          <nav
            className="hidden lg:flex items-center gap-0.5 px-2 py-1 rounded-full border border-white/8 bg-white/[0.03] backdrop-blur-md"
            aria-label="Main Navigation"
          >
            {NAV_LINKS.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="px-3 py-1.5 text-[13px] font-medium text-stone-300 hover:text-white hover:bg-white/8 rounded-full transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/70"
              >
                {item.label}
              </a>
            ))}
          </nav>

          <div className="hidden sm:flex items-center gap-3">
            <a
              href="#demo"
              className="text-sm font-medium text-stone-300 hover:text-white px-3 py-1.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/70 rounded-full"
            >
              Sign In
            </a>
            <Button size="sm" variant="primary" onClick={handleWaitlistClick}>
              <span>Get Started</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </div>

          <button
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 rounded-full text-stone-300 hover:text-white hover:bg-white/5 lg:hidden cursor-pointer"
            aria-label="Open mobile navigation menu"
          >
            <Menu className="w-6 h-6" />
          </button>
        </div>
      </header>

      <MobileMenu
        isOpen={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        onOpenWaitlist={handleWaitlistClick}
      />
    </>
  );
}
