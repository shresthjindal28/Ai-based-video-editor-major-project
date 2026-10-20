import React from "react";
import { AI_INTELLIGENCE_HIGHLIGHTS } from "@/lib/constants/features";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Brain, Sparkles, FileCode, Workflow, CheckCircle2 } from "lucide-react";

export function AiIntelligenceSection() {
  return (
    <section className="py-24 relative overflow-hidden bg-[#070912]/80 border-y border-white/5" id="intelligence">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Text Narrative */}
          <div className="lg:col-span-5 space-y-6">
            <Badge variant="cyan">
              <Brain className="w-3 h-3 text-cyan-400" />
              Grounded AI Engine
            </Badge>

            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
              An AI editor that understands{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-cyan-300">
                story arc and pacing.
              </span>
            </h2>

            <p className="text-base text-slate-300 leading-relaxed">
              Most automated tools blindly trim every silence or insert random stock b-roll. AutoCut AI parses the semantic narrative of your footage, timing cuts to sentence punchlines, audio downbeats, and dramatic pauses.
            </p>

            <div className="space-y-4 pt-2">
              {AI_INTELLIGENCE_HIGHLIGHTS.map((item, idx) => (
                <div key={idx} className="p-4 rounded-xl border border-white/10 bg-white/[0.02]">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                      <Sparkles className="w-3.5 h-3.5 text-violet-400" />
                      {item.title}
                    </h3>
                    <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
                      {item.metric}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {item.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Right Architecture Inspection Mockup */}
          <div className="lg:col-span-7">
            <Card glow className="p-6">
              <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
                <div className="flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-violet-400" />
                  <span className="text-xs font-mono font-medium text-slate-200">
                    AutoCut_DecisionList_v2.json
                  </span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Schema Validated
                </span>
              </div>

              {/* Formatted Code / JSON inspection showing explainable reasoning */}
              <div className="bg-black/70 rounded-xl p-4 font-mono text-xs overflow-x-auto border border-white/5 space-y-1.5 text-slate-300">
                <p className="text-slate-500">{"// Grounded cut decision list generated from prompt & vision tokens"}</p>
                <p>
                  <span className="text-violet-400">"sequence_intent"</span>: <span className="text-amber-300">"High-retention product launch intro"</span>,
                </p>
                <p>
                  <span className="text-violet-400">"speech_cadence"</span>: {"{"}
                </p>
                <p className="pl-4">
                  <span className="text-cyan-400">"silence_threshold_ms"</span>: <span className="text-emerald-300">450</span>,
                </p>
                <p className="pl-4">
                  <span className="text-cyan-400">"retained_breaths"</span>: <span className="text-amber-300">"natural"</span>,
                </p>
                <p className="pl-4">
                  <span className="text-cyan-400">"awkward_pauses_stripped"</span>: <span className="text-emerald-300">8</span>
                </p>
                <p>{"},"}</p>
                <p>
                  <span className="text-violet-400">"cuts"</span>: [
                </p>
                <p className="pl-4">
                  {"{"} <span className="text-cyan-400">"tc"</span>: <span className="text-amber-300">"00:00:08:12"</span>, <span className="text-cyan-400">"type"</span>: <span className="text-emerald-300">"B-ROLL_CUTAWAY"</span>, <span className="text-cyan-400">"reason"</span>: <span className="text-slate-400">"Topic shifted to coastal test run; sync with drum transient"</span> {"}"},
                </p>
                <p className="pl-4">
                  {"{"} <span className="text-cyan-400">"tc"</span>: <span className="text-amber-300">"00:00:16:04"</span>, <span className="text-cyan-400">"type"</span>: <span className="text-emerald-300">"PUNCH_IN_1.15X"</span>, <span className="text-cyan-400">"reason"</span>: <span className="text-slate-400">"Emphasize founder key thesis"</span> {"}"}
                </p>
                <p>],</p>
                <p>
                  <span className="text-violet-400">"color_pipeline"</span>: {"{"}
                </p>
                <p className="pl-4">
                  <span className="text-cyan-400">"source_gamut"</span>: <span className="text-amber-300">"Sony S-Gamut3.Cine"</span>,
                </p>
                <p className="pl-4">
                  <span className="text-cyan-400">"target_space"</span>: <span className="text-amber-300">"Rec.709 2.4 / Apple ProRes 422"</span>
                </p>
                <p>{"}"}</p>
              </div>

              <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1.5 font-mono text-[11px]">
                  <Workflow className="w-3.5 h-3.5 text-cyan-400" />
                  Deterministic & verifiable decisions
                </span>
                <span className="text-violet-300 font-mono text-[11px]">
                  Exportable to Premiere XML
                </span>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}
