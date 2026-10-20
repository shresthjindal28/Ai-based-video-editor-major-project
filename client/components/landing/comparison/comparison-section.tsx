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
            Choose your workflow
          </Badge>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-[#fff8ee] leading-tight">
            Find more room for{" "}
            <span className="italic text-gradient-primary">the work you love.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-stone-400">
            Use a first-cut assistant for the repetitive groundwork, then bring your taste and experience to the finishing pass.
          </p>
        </div>

        <div className="max-w-5xl mx-auto">
          <ComparisonTable />
        </div>
      </div>
    </section>
  );
}
