import React from "react";
import { USE_CASES } from "@/lib/constants/workflow";
import { UseCaseCard } from "./use-case-card";
import { Badge } from "@/components/ui/badge";
import { Users } from "lucide-react";

export function UseCasesSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="use-cases">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-16">
          <Badge variant="cyan" className="mb-4">
            <Users className="w-3 h-3" />
            Built for Modern Storytellers
          </Badge>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-[#fff8ee] leading-tight">
            Tailored workflows for{" "}
            <span className="italic text-gradient-primary">every production need.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-stone-400">
            Whether you are delivering daily shorts, documentary episodes, or commercial client campaigns, AutoCut AI adapts to your creative pacing.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {USE_CASES.map((uc, index) => (
            <UseCaseCard key={index} useCase={uc} />
          ))}
        </div>
      </div>
    </section>
  );
}
