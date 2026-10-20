import React from "react";
import { ComparisonTable } from "./comparison-table";
import { Badge } from "@/components/ui/badge";
import { Scale } from "lucide-react";

export function ComparisonSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="comparison">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-16">
          <Badge variant="violet" className="mb-4">
            <Scale className="w-3 h-3" />
            Clear Advantage
          </Badge>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-[#fff8ee] leading-tight">
            How AutoCut AI stacks up against{" "}
            <span className="italic text-gradient-primary">traditional workflows.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-stone-400">
            Real autonomy without the black-box limitations of template generators. Keep your creative control while reclaiming hundreds of editing hours.
          </p>
        </div>

        <div className="max-w-5xl mx-auto">
          <ComparisonTable />
        </div>
      </div>
    </section>
  );
}
