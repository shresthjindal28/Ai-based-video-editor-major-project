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
            <Network className="w-3 h-3 text-violet-400" />
            System Architecture
          </Badge>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            The Autonomous Editing{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-300">
              Pipeline.
            </span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-slate-400">
            A battle-tested distributed engine combining Whisper speech recognition, Gemini multimodal vision tokens, and C++ MLT rendering.
          </p>
        </div>

        {/* Interactive Architecture Graph */}
        <div className="max-w-5xl mx-auto">
          <WorkflowPipelineGraph />
        </div>
      </div>
    </section>
  );
}
