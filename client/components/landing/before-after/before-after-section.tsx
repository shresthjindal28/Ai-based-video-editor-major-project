import React from "react";
import { ComparisonSlider } from "./comparison-slider";
import { Badge } from "@/components/ui/badge";
import { Eye } from "lucide-react";

export function BeforeAfterSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="before-after">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-14">
          <Badge variant="cyan" className="mb-4">
            <Eye className="w-3 h-3" />
            Visual Proof
          </Badge>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-[#fff8ee] leading-tight">
            See the difference{" "}
            <span className="italic text-gradient-primary">frame by frame.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-stone-400">
            Compare flat, unprocessed camera footage with AutoCut AI&apos;s autonomous first-cut: color graded, noise isolated, beat matched, and rhythmically paced.
          </p>
        </div>

        <div className="max-w-5xl mx-auto">
          <ComparisonSlider />
        </div>
      </div>
    </section>
  );
}
