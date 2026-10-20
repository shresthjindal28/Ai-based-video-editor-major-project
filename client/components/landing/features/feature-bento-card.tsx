import React from "react";
import { FeatureItem } from "@/lib/constants/features";
import { Scissors, Sliders, Volume2, Type, Eye, Maximize2, Check } from "lucide-react";
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
    <Card className="p-6 flex flex-col justify-between group hover:bg-[#181410]/90">
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="w-11 h-11 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary group-hover:scale-105 group-hover:bg-primary/15 transition-all">
            <Icon className="w-5 h-5" />
          </div>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-teal-400/10 text-teal-200 border border-teal-400/20">
            {feature.badge}
          </span>
        </div>

        <p className="text-xs font-mono uppercase tracking-[0.14em] text-stone-500 mb-1">
          {feature.category}
        </p>

        <h3 className="text-xl font-semibold text-white mb-2.5 group-hover:text-primary transition-colors">
          {feature.title}
        </h3>

        <p className="text-sm text-stone-400 leading-relaxed mb-6">
          {feature.description}
        </p>
      </div>

      <div className="space-y-2 pt-4 border-t border-white/6">
        {feature.details.map((detail, idx) => (
          <div key={idx} className="flex items-center gap-2 text-xs text-stone-300">
            <Check className="w-3.5 h-3.5 text-teal-300 shrink-0" />
            <span>{detail}</span>
          </div>
        ))}

        {feature.metric && (
          <div className="mt-3 pt-2 text-[11px] font-mono text-primary flex items-center justify-between">
            <span>Benchmark:</span>
            <span className="font-semibold text-white bg-white/5 px-2 py-0.5 rounded-full border border-white/10">
              {feature.metric}
            </span>
          </div>
        )}
      </div>
    </Card>
  );
}
