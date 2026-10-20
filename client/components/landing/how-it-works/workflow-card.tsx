import React from "react";
import { WorkflowStep } from "@/lib/constants/workflow";
import { UploadCloud, MessageSquareCode, BrainCircuit, GitBranch, Cpu, CheckCircle2 } from "lucide-react";
import { Card } from "@/components/ui/card";

const iconMap = {
  UploadCloud,
  MessageSquareCode,
  BrainCircuit,
  GitBranch,
  Cpu,
  CheckCircle2,
};

export function WorkflowCard({ step }: { step: WorkflowStep }) {
  const Icon = iconMap[step.iconName] || Cpu;

  return (
    <Card className="relative p-6 flex flex-col justify-between group hover:bg-[#181410]/90">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-3xl font-serif italic text-gradient-primary">
            {step.number}
          </span>
          <div className="w-10 h-10 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary group-hover:scale-110 transition-all">
            <Icon className="w-5 h-5" />
          </div>
        </div>

        <span className="inline-block px-2 py-0.5 rounded-full text-[10px] font-mono bg-white/5 text-stone-300 border border-white/10 mb-2">
          {step.badge}
        </span>

        <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-primary transition-colors">
          {step.title}
        </h3>

        <p className="text-sm text-stone-400 leading-relaxed mb-4">
          {step.description}
        </p>
      </div>

      <div className="pt-3 border-t border-white/6 text-[11px] font-mono text-stone-400 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-teal-300" />
        <span className="truncate">{step.detail}</span>
      </div>
    </Card>
  );
}
