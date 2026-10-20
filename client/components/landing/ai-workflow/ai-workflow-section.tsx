import React from "react";
import { WorkflowPipelineGraph } from "./workflow-pipeline-graph";
import { Badge } from "@/components/ui/badge";
import { Network } from "lucide-react";

export function AiWorkflowSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="workflow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-16">
          <Badge variant="violet" className="mb-4">
            <Network className="w-3 h-3" />
            Built around your process
          </Badge>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-[#fff8ee] leading-tight">
            From first selects to{" "}
            <span className="italic text-gradient-primary">final approval.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-stone-400">
            Explore each part of the edit. See where AutoCut AI can help and where your creative judgment makes the difference.
          </p>
        </div>

        <div className="max-w-5xl mx-auto">
          <WorkflowPipelineGraph />
        </div>
      </div>
    </section>
  );
}
