import React from "react";
import { InteractiveEditorPreview } from "./interactive-editor-preview";
import { Badge } from "@/components/ui/badge";
import { Sparkles } from "lucide-react";

export function DemoSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="demo">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-14">
          <Badge variant="cyan" className="mb-4">
            <Sparkles className="w-3 h-3" />
            Try the editing preview
          </Badge>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-[#fff8ee] leading-tight">
            From raw clips to finished cut{" "}
            <span className="italic text-gradient-primary">with your direction.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-stone-400">
            Choose a sample brief below, then hit <span className="text-primary font-mono">Build First Cut</span> to walk through an illustrative edit. This demo uses sample clips and simulated progress; it does not process or export video.
          </p>
        </div>

        <div className="w-full">
          <InteractiveEditorPreview />
        </div>
      </div>
    </section>
  );
}
