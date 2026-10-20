import React from "react";
import { InteractiveEditorPreview } from "./interactive-editor-preview";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Terminal, Cpu } from "lucide-react";

export function DemoSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="demo">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-14">
          <Badge variant="cyan" className="mb-4">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            Interactive Product Experience
          </Badge>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            From raw clips to finished cut{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-300">
              in one command.
            </span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-slate-400">
            Select a prompt preset below or hit <span className="text-violet-300 font-mono">Generate Autonomous Cut</span> to see AutoCut AI analyze audio waveforms, trim silences, insert B-roll, and grade color in real-time.
          </p>
        </div>

        {/* Studio Mockup Interface */}
        <div className="w-full">
          <InteractiveEditorPreview />
        </div>
      </div>
    </section>
  );
}
