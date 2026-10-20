import React from "react";
import { COMPARISON_DATA, ComparisonRow } from "@/lib/constants/comparison";
import { Sparkles, Check, X, ShieldAlert } from "lucide-react";

export function ComparisonTable() {
  return (
    <div className="w-full overflow-x-auto rounded-2xl border border-white/10 bg-[#090b14]/90 backdrop-blur-xl shadow-2xl shadow-violet-950/20">
      <table className="w-full text-left border-collapse min-w-[680px]">
        <thead>
          <tr className="border-b border-white/10 bg-[#0e111d]">
            <th className="p-4 sm:p-5 text-xs font-mono uppercase tracking-wider text-slate-400 w-1/4">
              Capability
            </th>
            <th className="p-4 sm:p-5 text-xs font-mono uppercase tracking-wider text-slate-400 w-1/4">
              Manual Editing
            </th>
            <th className="p-4 sm:p-5 text-xs font-mono uppercase tracking-wider text-slate-400 w-1/4">
              Basic AI "Generators"
            </th>
            <th className="p-4 sm:p-5 text-xs font-mono uppercase tracking-wider text-cyan-300 bg-violet-950/30 border-x border-violet-500/20 w-1/4">
              <div className="flex items-center gap-1.5 font-bold">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
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
              <td className="p-4 sm:p-5 font-semibold text-slate-200">
                {row.feature}
              </td>
              <td className="p-4 sm:p-5 text-slate-400 leading-relaxed">
                {row.manual}
              </td>
              <td className="p-4 sm:p-5 text-slate-400 leading-relaxed">
                {row.templateAi}
              </td>
              <td className="p-4 sm:p-5 font-medium text-slate-100 bg-violet-950/20 border-x border-violet-500/20 leading-relaxed">
                <span className="text-cyan-300 font-semibold">{row.autocut}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
