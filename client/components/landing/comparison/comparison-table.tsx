import React from "react";
import { COMPARISON_DATA } from "@/lib/constants/comparison";
import { Sparkles } from "lucide-react";

export function ComparisonTable() {
  return (
    <div className="w-full overflow-x-auto rounded-3xl border border-white/10 bg-[#110e0c]/90 backdrop-blur-xl shadow-2xl shadow-amber-950/20">
      <table className="w-full text-left border-collapse min-w-[680px]">
        <thead>
          <tr className="border-b border-white/10 bg-[#181410]">
            <th className="p-4 sm:p-5 text-xs font-mono uppercase tracking-wider text-stone-400 w-1/4">
              Capability
            </th>
            <th className="p-4 sm:p-5 text-xs font-mono uppercase tracking-wider text-stone-400 w-1/4">
              From scratch
            </th>
            <th className="p-4 sm:p-5 text-xs font-mono uppercase tracking-wider text-stone-400 w-1/4">
              Template workflow
            </th>
            <th className="p-4 sm:p-5 text-xs font-mono uppercase tracking-wider text-primary bg-primary/8 border-x border-primary/20 w-1/4">
              <div className="flex items-center gap-1.5 font-bold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>AutoCut AI</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5 text-xs sm:text-sm">
          {COMPARISON_DATA.map((row, index) => (
            <tr
              key={index}
              className={`hover:bg-white/[0.02] transition-colors ${
                row.highlight ? "bg-white/[0.01]" : ""
              }`}
            >
              <td className="p-4 sm:p-5 font-semibold text-stone-200">
                {row.feature}
              </td>
              <td className="p-4 sm:p-5 text-stone-400 leading-relaxed">
                {row.manual}
              </td>
              <td className="p-4 sm:p-5 text-stone-400 leading-relaxed">
                {row.templateAi}
              </td>
              <td className="p-4 sm:p-5 font-medium text-stone-100 bg-primary/6 border-x border-primary/15 leading-relaxed">
                <span className="text-primary font-semibold">{row.autocut}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
