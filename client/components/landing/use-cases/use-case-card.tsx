import React from "react";
import { Card } from "@/components/ui/card";
import { Sparkles, ArrowRight } from "lucide-react";

interface UseCase {
  title: string;
  description: string;
  badge: string;
  tags: string[];
}

export function UseCaseCard({ useCase }: { useCase: UseCase }) {
  return (
    <Card className="p-6 flex flex-col justify-between group hover:border-violet-500/40 hover:bg-[#101322]/90 transition-all duration-300">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20">
            {useCase.badge}
          </span>
          <Sparkles className="w-4 h-4 text-slate-500 group-hover:text-cyan-400 transition-colors" />
        </div>

        <h3 className="text-xl font-bold text-white mb-3 group-hover:text-violet-200 transition-colors">
          {useCase.title}
        </h3>

        <p className="text-sm text-slate-400 leading-relaxed mb-6">
          {useCase.description}
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5 pt-4 border-t border-white/5">
        {useCase.tags.map((tag, idx) => (
          <span
            key={idx}
            className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-slate-300 border border-white/10"
          >
            {tag}
          </span>
        ))}
      </div>
    </Card>
  );
}
