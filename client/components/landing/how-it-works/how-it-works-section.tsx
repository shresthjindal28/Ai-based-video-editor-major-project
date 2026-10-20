import React from "react";
import { HOW_IT_WORKS_STEPS } from "@/lib/constants/workflow";
import { WorkflowCard } from "./workflow-card";
import { Badge } from "@/components/ui/badge";
import { GitPullRequest } from "lucide-react";

export function HowItWorksSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="how-it-works">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-16">
          <Badge variant="violet" className="mb-4">
            <GitPullRequest className="w-3 h-3" />
            Autonomous Pipeline
          </Badge>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-[#fff8ee] leading-tight">
            How AutoCut AI transforms your footage{" "}
            <span className="italic text-gradient-primary">in 6 steps.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-stone-400">
            From raw camera takes to Final Cut Pro XML or 4K HDR master, AutoCut AI handles the heavy lifting without stripping away your creative direction.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {HOW_IT_WORKS_STEPS.map((step) => (
            <WorkflowCard key={step.number} step={step} />
          ))}
        </div>
      </div>
    </section>
  );
}
