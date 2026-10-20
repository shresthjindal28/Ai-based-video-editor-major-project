export interface WorkflowStep {
  number: string;
  title: string;
  description: string;
  badge: string;
  iconName: "UploadCloud" | "MessageSquareCode" | "BrainCircuit" | "GitBranch" | "Cpu" | "CheckCircle2";
  detail: string;
}

export const HOW_IT_WORKS_STEPS: WorkflowStep[] = [
  {
    number: "01",
    title: "Upload Raw Footage",
    description: "Drop in your multi-cam takes, 4K camera files, drone clips, or phone recordings. We support Sony S-Log, Apple Log, MP4, and ProRes.",
    badge: "Direct Cloud Ingest",
    iconName: "UploadCloud",
    detail: "Up to 8K resolution accepted with rapid proxy generation"
  },
  {
    number: "02",
    title: "Describe Your Vision",
    description: "Type your editing goal in plain English: target duration, pacing style, musical mood, color grading preference, and hook requirements.",
    badge: "Natural Language Prompt",
    iconName: "MessageSquareCode",
    detail: "Presets available for Reels, YouTube essays, and promos"
  },
  {
    number: "03",
    title: "AI Understands Context",
    description: "Multi-modal vision and acoustic models transcribe speech, map facial focus, detect awkward pauses, and identify emotional highlights.",
    badge: "Multi-Modal Vision & Audio",
    iconName: "BrainCircuit",
    detail: "Frame-by-frame transcript & audio spectral energy analysis"
  },
  {
    number: "04",
    title: "Grounded Timeline Planning",
    description: "The AI Director builds a structured Decision List (EDL): synchronizing A-roll dialogue, weaving B-roll cutaways, and timing cuts to beat drops.",
    badge: "Explainable Edit Graph",
    iconName: "GitBranch",
    detail: "Full visibility into every transition, zoom, and ducking decision"
  },
  {
    number: "05",
    title: "Hardware-Accelerated Render",
    description: "Our dedicated GPU rendering pipeline applies 3D LUTs, denoises audio, adds kinetic subtitles, and executes cuts in native resolution.",
    badge: "GPU Render Engine",
    iconName: "Cpu",
    detail: "10x faster than real-time rendering on high-throughput clusters"
  },
  {
    number: "06",
    title: "Review, Refine & Export",
    description: "Preview in the web player, adjust cuts or caption styles with prompt tweaks, or export an XML/FCPXML file to DaVinci Resolve & Premiere Pro.",
    badge: "Zero Vendor Lock-in",
    iconName: "CheckCircle2",
    detail: "Download ready-to-post MP4 or raw NLE project files"
  }
];

export interface PipelineNode {
  id: string;
  label: string;
  sublabel: string;
  tech: string;
  color: string;
}

export const ARCHITECTURE_PIPELINE: PipelineNode[] = [
  {
    id: "ingest",
    label: "Ingest & Proxy",
    sublabel: "Ultra-fast chunked upload & proxy encoding",
    tech: "FFmpeg Hardware Proxies",
    color: "from-blue-500/20 to-blue-600/10 border-blue-500/30"
  },
  {
    id: "analysis",
    label: "Sensory Analysis",
    sublabel: "Speech-to-text, facial tracking & beat detection",
    tech: "Whisper + Vision AI + Librosa",
    color: "from-violet-500/20 to-violet-600/10 border-violet-500/30"
  },
  {
    id: "director",
    label: "AI Video Director",
    sublabel: "Synthesizes narrative arc & cut decision list",
    tech: "Semantic Timeline Reasoning",
    color: "from-fuchsia-500/20 to-fuchsia-600/10 border-fuchsia-500/30"
  },
  {
    id: "render",
    label: "High-Throughput Render",
    sublabel: "GPU compositing, 3D LUTs & kinetic captions",
    tech: "MLT Framework + NVENC",
    color: "from-cyan-500/20 to-cyan-600/10 border-cyan-500/30"
  },
  {
    id: "delivery",
    label: "Master Delivery",
    sublabel: "Instant 4K master + Resolve / Premiere XML",
    tech: "FCPXML / ProRes / H.265",
    color: "from-emerald-500/20 to-emerald-600/10 border-emerald-500/30"
  }
];

export const USE_CASES = [
  {
    title: "Solo Creators & YouTubers",
    description: "Turn 2 hours of raw vlog or tutorial takes into an engaging 12-minute video with tight pacing, zero dead air, and automated zooms.",
    badge: "Save 15+ hrs/week",
    tags: ["Longform to Short", "Jump-Cut Removal", "Kinetic Subtitles"]
  },
  {
    title: "Growth & Social Marketing Teams",
    description: "Transform webinar recordings and customer interviews into dozens of punchy TikToks, Shorts, and LinkedIn video clips in minutes.",
    badge: "10x Output Velocity",
    tags: ["9:16 Auto-Reframe", "Hook Optimization", "Viral Captions"]
  },
  {
    title: "Travel & Adventure Filmmakers",
    description: "Auto-sync high-framerate drone and gimbal footage to musical beat drops, applying filmic LUTs while preserving original dynamic range.",
    badge: "Cinematic Aesthetic",
    tags: ["Beat-Matched Cuts", "Log Color Grade", "Speed Ramps"]
  },
  {
    title: "Podcast & Talk Show Studios",
    description: "Effortlessly edit multi-camera interviews. AutoCut AI switches between camera angles based on active speaker detection and facial cues.",
    badge: "Multi-Camera Sync",
    tags: ["Speaker Tracking", "Noise Reduction", "Auto Sound Ducking"]
  }
];
