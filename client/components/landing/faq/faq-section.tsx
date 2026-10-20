import React from "react";
import { FAQ_ITEMS } from "@/lib/constants/faq";
import { FaqAccordionItem } from "./faq-accordion-item";
import { Badge } from "@/components/ui/badge";
import { HelpCircle } from "lucide-react";

export function FaqSection() {
  return (
    <section className="py-24 relative overflow-hidden" id="faq">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center mb-16">
          <Badge variant="cyan" className="mb-4">
            <HelpCircle className="w-3 h-3 text-cyan-400" />
            Frequently Asked Questions
          </Badge>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Everything you need to know about{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-300">
              AutoCut AI.
            </span>
          </h2>
          <p className="mt-4 text-base sm:text-lg text-slate-400">
            Straightforward answers about footage retention, privacy, supported codecs, and timeline workflows.
          </p>
        </div>

        {/* Accordion list */}
        <div className="space-y-4">
          {FAQ_ITEMS.map((item) => (
            <FaqAccordionItem key={item.id} item={item} />
          ))}
        </div>
      </div>
    </section>
  );
}
