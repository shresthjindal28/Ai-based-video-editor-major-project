"use client";

import React from "react";
import { motion } from "motion/react";
import { HeroBadge } from "./hero-badge";
import { HeroActions } from "./hero-actions";
import { ThrineHero } from "../visuals/thrine-hero";
import { ShieldCheck, Zap, Video } from "lucide-react";

interface HeroSectionProps {
  onOpenWaitlist?: () => void;
}

export function HeroSection({ onOpenWaitlist }: HeroSectionProps) {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden" id="hero">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <HeroBadge />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="font-serif text-5xl sm:text-6xl md:text-7xl lg:text-[5.4rem] tracking-tight text-[#fff8ee] max-w-5xl leading-[1.05]"
        >
          Less time cutting.{" "}
          <span className="block italic text-gradient-primary mt-1">More time creating.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 text-base sm:text-xl text-stone-300/90 max-w-2xl font-normal leading-relaxed"
        >
          Get past the repetitive part of the edit. Bring your footage and brief; AutoCut AI helps tighten takes, place B-roll, and build a first cut you can make your own.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 w-full"
        >
          <HeroActions onOpenWaitlist={onOpenWaitlist} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-5 text-xs text-stone-400 font-mono"
        >
          <div className="flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5 text-primary" />
            <span>A head start on your first cut</span>
          </div>
          <span className="text-white/15">•</span>
          <div className="flex items-center gap-1.5">
            <Video className="w-3.5 h-3.5 text-rose-300" />
            <span>Your footage. Your style.</span>
          </div>
          <span className="text-white/15">•</span>
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-300" />
            <span>You have the final say</span>
          </div>
        </motion.div>

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
