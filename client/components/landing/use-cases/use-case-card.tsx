import React from "react";
import { Card } from "@/components/ui/card";
import { Sparkles } from "lucide-react";

interface UseCase {
  title: string;
  description: string;
  badge: string;
  tags: string[];
}

export function UseCaseCard({ useCase }: { useCase: UseCase }) {
  return (
    <Card className="p-6 flex flex-col justify-between group hover:bg-[#181410]/90">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">
            {useCase.badge}
          </span>
          <Sparkles className="w-4 h-4 text-stone-500 group-hover:text-teal-300 transition-colors" />
        </div>

        <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-primary transition-colors">
          {useCase.title}
        </h3>

        <p className="text-sm text-stone-400 leading-relaxed mb-6">
          {useCase.description}
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5 pt-4 border-t border-white/6">
        {useCase.tags.map((tag, idx) => (
          <span
            key={idx}
            className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/5 text-stone-300 border border-white/10"
          >
            {tag}
          </span>
        ))}
      </div>
    </Card>
  );
}
