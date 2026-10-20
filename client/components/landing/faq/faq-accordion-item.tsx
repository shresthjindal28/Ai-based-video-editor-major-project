"use client";

import React, { useState } from "react";
import { FAQItem } from "@/lib/constants/faq";
import { ChevronDown } from "lucide-react";

export function FaqAccordionItem({ item }: { item: FAQItem }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="rounded-2xl border border-white/10 bg-[#14110f]/80 backdrop-blur-md overflow-hidden transition-colors hover:border-primary/25">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 text-left text-stone-100 hover:text-white transition-colors cursor-pointer"
        aria-expanded={isOpen}
      >
        <span className="text-base font-semibold pr-4">{item.question}</span>
        <div
          className={`w-7 h-7 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shrink-0 transition-transform duration-200 ${
            isOpen ? "rotate-180 bg-primary/15 text-primary border-primary/30" : "text-stone-400"
          }`}
        >
          <ChevronDown className="w-4 h-4" />
        </div>
      </button>

      {isOpen && (
        <div className="px-5 pb-5 text-sm text-stone-300/90 leading-relaxed border-t border-white/6 pt-4">
          <p>{item.answer}</p>
          <div className="mt-3 flex items-center gap-2">
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/5 text-stone-400">
              Topic: {item.category}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
