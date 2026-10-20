import React from "react";
import { CAPABILITIES } from "@/lib/constants/features";
import { FeatureBentoCard } from "./feature-bento-card";
import { Badge } from "@/components/ui/badge";
import { SlidersHorizontal } from "lucide-react";

export function FeaturesSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="features">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-16">
          <Badge variant="violet" className="mb-4">
            <SlidersHorizontal className="w-3 h-3" />
            Your editing toolkit
          </Badge>
          <h2 className="font-serif text-4xl sm:text-5xl tracking-tight text-[#fff8ee] leading-tight">
            The repetitive work, handled.{" "}
            <span className="italic text-gradient-primary">The creative choices, yours.</span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-stone-400">
            From tightening dialogue to framing the social cutdown, get help with the tasks that slow down a good edit.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {CAPABILITIES.map((feature) => (
            <FeatureBentoCard key={feature.id} feature={feature} />
          ))}
        </div>
      </div>
    </section>
  );
}
