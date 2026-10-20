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
    <Card className="relative p-6 flex flex-col justify-between group hover:border-violet-500/40 hover:bg-[#111422]/90 transition-all duration-300">
      <div>
        <div className="flex items-center justify-between mb-4">
          <span className="text-3xl font-black font-mono text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-400">
            {step.number}
          </span>
          <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center text-violet-300 group-hover:scale-110 group-hover:text-cyan-300 group-hover:border-cyan-500/30 transition-all">
            <Icon className="w-5 h-5" />
          </div>
        </div>

        <span className="inline-block px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 text-slate-300 border border-white/10 mb-2">
          {step.badge}
        </span>

        <h3 className="text-lg font-bold text-white mb-2 group-hover:text-violet-200 transition-colors">
          {step.title}
        </h3>

        <p className="text-sm text-slate-400 leading-relaxed mb-4">
          {step.description}
        </p>
      </div>

      <div className="pt-3 border-t border-white/5 text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
        <span className="truncate">{step.detail}</span>
      </div>
    </Card>
  );
}
