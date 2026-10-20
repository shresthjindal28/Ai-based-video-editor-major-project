"use client";

import React from "react";
import { motion } from "motion/react";
import { HeroBadge } from "./hero-badge";
import { HeroActions } from "./hero-actions";
import { ThrineHero } from "../visuals/thrine-hero";
import { ShieldCheck, Zap, Video, Sparkles } from "lucide-react";

interface HeroSectionProps {
  onOpenWaitlist?: () => void;
}

export function HeroSection({ onOpenWaitlist }: HeroSectionProps) {
  return (
    <section className="relative pt-32 pb-20 md:pt-44 md:pb-32 overflow-hidden" id="hero">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 flex flex-col items-center text-center">
        {/* Top Badge */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <HeroBadge />
        </motion.div>

        {/* Primary Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-6xl md:text-7xl lg:text-8xl font-black tracking-tight text-white max-w-5xl leading-[1.08]"
        >
          Your footage. Your vision.{" "}
          <span className="block text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-fuchsia-300 to-cyan-300">
            Edited by AI.
          </span>
        </motion.h1>

        {/* Value Proposition Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 text-base sm:text-xl text-slate-300/90 max-w-2xl font-normal leading-relaxed"
        >
          Upload raw clips, describe the story you want, and let AutoCut AI synchronize
          dialogue, cut dead-air, weave B-roll, grade color, and deliver a polished 4K video in minutes.
        </motion.p>

        {/* Actions / CTA Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 w-full"
        >
          <HeroActions onOpenWaitlist={onOpenWaitlist} />
        </motion.div>

        {/* Social Proof / Trust Indicators */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-6 text-xs text-slate-400 font-mono"
        >
          <div className="flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>Under 2-Minute First Cut</span>
          </div>
          <span className="text-white/20">•</span>
          <div className="flex items-center gap-1.5">
            <Video className="w-3.5 h-3.5 text-violet-400" />
            <span>Sony S-Log3 & Apple Log</span>
          </div>
          <span className="text-white/20">•</span>
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Zero Data Model Training</span>
          </div>
        </motion.div>

        {/* 3D Visual Centerpiece (Thrine Hero with self-hosted canvas fallback) */}
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.45 }}
          className="mt-14 w-full max-w-5xl"
        >
          <ThrineHero />
        </motion.div>
      </div>
    </section>
  );
}
