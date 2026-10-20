import React from "react";
import { Film, Shield } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-white/8 bg-[#090807] text-stone-400 py-16 text-xs font-sans">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 mb-14">
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-amber-400 to-rose-400 p-[1px]">
                <div className="w-full h-full bg-[#110e0c] rounded-[10px] flex items-center justify-center">
                  <Film className="w-4 h-4 text-amber-200" />
                </div>
              </div>
              <span className="font-semibold text-base tracking-tight text-white">
                AutoCut<span className="font-serif italic text-primary"> AI</span>
              </span>
            </div>

            <p className="text-sm text-stone-400 max-w-sm leading-relaxed">
              Autonomous AI video editing for creative storytellers. Upload raw multicam footage, describe your vision, and get a polished 4K timeline in minutes.
            </p>

            <div className="flex items-center gap-3 text-stone-400 pt-2">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 hover:text-white flex items-center justify-center transition-colors"
                aria-label="GitHub Repository"
              >
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
              </a>
              <a
                href="https://x.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 hover:text-white flex items-center justify-center transition-colors"
                aria-label="X / Twitter"
              >
                <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>
              <a
                href="https://youtube.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 hover:text-white flex items-center justify-center transition-colors"
                aria-label="YouTube Channel"
              >
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                </svg>
              </a>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="text-[11px] font-mono font-semibold uppercase tracking-[0.16em] text-white">
              Product
            </h4>
            <ul className="space-y-2">
              <li>
                <a href="#demo" className="hover:text-white transition-colors">
                  Interactive Demo
                </a>
              </li>
              <li>
                <a href="#how-it-works" className="hover:text-white transition-colors">
                  How It Works
                </a>
              </li>
              <li>
                <a href="#before-after" className="hover:text-white transition-colors">
                  Before & After
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-white transition-colors">
                  Capabilities
                </a>
              </li>
              <li>
                <a href="#comparison" className="hover:text-white transition-colors">
                  Comparison Matrix
                </a>
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="text-[11px] font-mono font-semibold uppercase tracking-[0.16em] text-white">
              Architecture
            </h4>
            <ul className="space-y-2">
              <li>
                <a href="#workflow" className="hover:text-white transition-colors">
                  Pipeline Graph
                </a>
              </li>
              <li>
                <a href="#intelligence" className="hover:text-white transition-colors">
                  Cut Decision Schema
                </a>
              </li>
              <li>
                <a href="https://ffmpeg.org" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">
                  MLT & FFmpeg Core
                </a>
              </li>
              <li>
                <a href="https://thrine.app" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">
                  Thrine Visuals
                </a>
              </li>
              <li>
                <a href="#faq" className="hover:text-white transition-colors">
                  Developer FAQ
                </a>
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="text-[11px] font-mono font-semibold uppercase tracking-[0.16em] text-white">
              Security & Terms
            </h4>
            <ul className="space-y-2">
              <li className="flex items-center gap-1.5 text-teal-300">
                <Shield className="w-3.5 h-3.5" />
                <span>Zero Training Guarantee</span>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Security Disclosures
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-white/6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-stone-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
            <span>All GPU rendering clusters operational</span>
          </div>
          <p>© 2026 AutoCut AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
