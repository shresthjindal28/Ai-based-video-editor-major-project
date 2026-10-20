"use client";

import React, { useState } from "react";
import { ARCHITECTURE_PIPELINE, PipelineNode } from "@/lib/constants/workflow";
import { ArrowRight, Cpu, Layers, HardDrive, CheckCircle2, Sparkles, Terminal } from "lucide-react";

export function WorkflowPipelineGraph() {
  const [activeNode, setActiveNode] = useState<PipelineNode>(ARCHITECTURE_PIPELINE[2]);

  const nodeDetails: Record<string, { inputs: string; engine: string; output: string }> = {
    ingest: {
      inputs: "4K / 8K RAW Clips, S-Log3, Apple Log, ProRes MOV",
      engine: "Hardware NVDEC chunked transcode into 1080p proxy buffers",
      output: "Zero-latency streaming proxies + audio stems",
    },
    analysis: {
      inputs: "Proxy video frames + 48kHz audio track",
      engine: "Whisper speech transcription + Gemini Vision scene tags + Librosa beat detection",
      output: "Frame-by-frame JSON metadata of faces, topic tags, and audio transients",
    },
    director: {
      inputs: "User prompt instructions + sensory metadata graph",
      engine: "Multi-Modal Narrative Planner generating Cut Decision Graph",
      output: "Validated JSON Decision List with cut timecodes, zoom levels, and B-roll indices",
    },
    render: {
      inputs: "Original camera masters + Cut Decision List + 3D LUT cubes",
      engine: "MLT C++ framework compositor + GPU NVENC acceleration",
      output: "Multi-track rendered video with audio sidechain ducking & burned subtitles",
    },
    delivery: {
      inputs: "Rendered frames & synchronized audio",
      engine: "Container packager + Final Cut Pro XML / DaVinci Resolve exporter",
      output: "Apple ProRes 422 4K Master, MP4 H.265 web stream, FCPXML timeline",
    },
  };

  const currentDetail = nodeDetails[activeNode.id];

  return (
    <div className="w-full flex flex-col items-center">
      {/* Interactive Horizontal Pipeline Nodes */}
      <div className="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-8">
        {ARCHITECTURE_PIPELINE.map((node, index) => {
          const isSelected = activeNode.id === node.id;
          return (
            <button
              key={node.id}
              onClick={() => setActiveNode(node)}
              className={`p-4 rounded-xl text-left border transition-all cursor-pointer relative ${
                isSelected
                  ? "bg-violet-950/40 border-violet-500 shadow-lg shadow-violet-900/30"
                  : "bg-[#0b0e1a]/80 border-white/10 hover:border-white/20 hover:bg-white/[0.04]"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono font-bold text-slate-400">
                  STAGE 0{index + 1}
                </span>
                {isSelected && (
                  <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                )}
              </div>
              <p className={`text-sm font-bold mb-1 ${isSelected ? "text-white" : "text-slate-200"}`}>
                {node.label}
              </p>
              <p className="text-[11px] text-slate-400 font-mono truncate">
                {node.tech}
              </p>
            </button>
          );
        })}
      </div>

      {/* Detail Inspector Card for the selected stage */}
      <div className="w-full rounded-2xl border border-violet-500/30 bg-gradient-to-b from-[#0e1120] to-[#080912] p-6 shadow-xl backdrop-blur-xl">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-violet-500/20 border border-violet-500/30 flex items-center justify-center text-cyan-300">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                {activeNode.label}
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30">
                  {activeNode.tech}
                </span>
              </h3>
              <p className="text-xs text-slate-400">{activeNode.sublabel}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-950/40 px-3 py-1 rounded-lg border border-emerald-800/40">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>GPU Accelerated Node</span>
          </div>
        </div>

        {/* Input -> Processing -> Output Flow */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-black/50 border border-white/10">
            <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400 mb-2">
              <HardDrive className="w-3.5 h-3.5 text-violet-400" />
              <span>Input Data</span>
            </div>
            <p className="text-xs text-slate-200 font-mono leading-relaxed">
              {currentDetail.inputs}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-violet-950/20 border border-violet-500/20">
            <div className="flex items-center gap-1.5 text-xs font-mono text-violet-300 mb-2">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Execution Engine</span>
            </div>
            <p className="text-xs text-slate-200 font-mono leading-relaxed">
              {currentDetail.engine}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-black/50 border border-white/10">
            <div className="flex items-center gap-1.5 text-xs font-mono text-cyan-400 mb-2">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>Generated Artifact</span>
            </div>
            <p className="text-xs text-slate-200 font-mono leading-relaxed">
              {currentDetail.output}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
