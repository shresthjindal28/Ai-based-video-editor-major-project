import React from "react";
import { FeatureItem } from "@/lib/constants/features";
import { Scissors, Sliders, Volume2, Type, Eye, Maximize2, Check, ArrowUpRight } from "lucide-react";
import { Card } from "@/components/ui/card";

const iconMap = {
  Scissors,
  Sliders,
  Volume2,
  Type,
  Eye,
  Maximize2,
  Sparkles: Scissors,
  Cpu: Scissors,
};

export function FeatureBentoCard({ feature }: { feature: FeatureItem }) {
  const Icon = iconMap[feature.iconName] || Scissors;

  return (
    <Card className="p-6 flex flex-col justify-between group hover:border-violet-500/30 hover:bg-[#101222]/90 transition-all duration-300">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="w-11 h-11 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-300 group-hover:scale-105 group-hover:bg-violet-500/20 group-hover:text-cyan-300 transition-all">
            <Icon className="w-5 h-5" />
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
            {feature.badge}
          </span>
        </div>

        <p className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
          {feature.category}
        </p>

        <h3 className="text-xl font-bold text-white mb-2.5 group-hover:text-violet-200 transition-colors">
          {feature.title}
        </h3>

        <p className="text-sm text-slate-400 leading-relaxed mb-6">
          {feature.description}
        </p>
      </div>

      <div className="space-y-2 pt-4 border-t border-white/5">
        {feature.details.map((detail, idx) => (
          <div key={idx} className="flex items-center gap-2 text-xs text-slate-300">
            <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span>{detail}</span>
          </div>
        ))}

        {feature.metric && (
          <div className="mt-3 pt-2 text-[11px] font-mono text-violet-300 flex items-center justify-between">
            <span>Benchmark:</span>
            <span className="font-semibold text-white bg-white/5 px-2 py-0.5 rounded border border-white/10">
              {feature.metric}
            </span>
          </div>
        )}
      </div>
    </Card>
  );
}
