export interface FeatureItem {
  id: string;
  title: string;
  category: string;
  description: string;
  iconName: "Scissors" | "Sparkles" | "Sliders" | "Volume2" | "Type" | "Maximize2" | "Eye" | "Cpu";
  badge: string;
  metric?: string;
  details: string[];
}

export const CAPABILITIES: FeatureItem[] = [
  {
    id: "smart-cuts",
    title: "Autonomous Jump-Cut & Pacing Engine",
    category: "Editing Core",
    description: "Detects false starts, stuttering, awkward pauses, and dead-air with millisecond precision while keeping natural speech rhythm intact.",
    iconName: "Scissors",
    badge: "99.2% Accuracy",
    metric: "-85% editing time",
    details: ["Filler word & silence stripping", "Dynamic jump-cut angle switching", "Natural conversational cadence matching"]
  },
  {
    id: "color-grading",
    title: "Cinematic 3D LUTs & Tone Mapping",
    category: "Visuals",
    description: "Intelligently converts Sony S-Log, Canon C-Log, Apple ProRes Log, or standard rec.709 into balanced, film-grade cinematic looks.",
    iconName: "Sliders",
    badge: "HDR & Rec.709",
    metric: "40+ Studio Profiles",
    details: ["Automated exposure & skin tone preservation", "Kodak 2383 & modern film emulations", "Dynamic scene-to-scene contrast balancing"]
  },
  {
    id: "studio-audio",
    title: "Studio Voice Isolation & Audio Ducking",
    category: "Audio",
    description: "Separates dialogue from wind and hum, automatically adds ambient riser effects, and ducks background music behind every speech phrase.",
    iconName: "Volume2",
    badge: "Broadcast Loudness",
    metric: "-35dB noise removal",
    details: ["Multi-band voice clarity enhancement", "Automated beat drops on cut points", "Dynamic sidechain music ducking"]
  },
  {
    id: "kinetic-captions",
    title: "Kinetic Captions & Subtitles",
    category: "Typography",
    description: "Generates frame-accurate, word-by-word highlighted captions with custom fonts, dynamic emoji accents, and viral kinetic motion styles.",
    iconName: "Type",
    badge: "50+ Languages",
    metric: "Zero transcription lag",
    details: ["Word-level timing synchronization", "Dynamic punch-in text highlights", "Exportable SRT, VTT, and burned-in tracks"]
  },
  {
    id: "b-roll-insertion",
    title: "Context-Aware B-Roll Insertion",
    category: "Intelligence",
    description: "Analyzes spoken topics and inserts relevant secondary footage or zooms right when listener attention needs a visual shift.",
    iconName: "Eye",
    badge: "Multi-Modal AI",
    metric: "Contextual relevancy",
    details: ["Shot composition analysis", "Seamless J-cut and L-cut audio overlap", "Automated smooth optical flow transitions"]
  },
  {
    id: "smart-reframe",
    title: "Multi-Aspect Smart Reframe",
    category: "Delivery",
    description: "One-click conversion between 16:9 cinematic horizontal, 9:16 TikTok/Reels vertical, and 1:1 square with intelligent speaker tracking.",
    iconName: "Maximize2",
    badge: "Active Subject Track",
    metric: "Zero keyframing required",
    details: ["Face & action centering", "Adaptive zoom & pan interpolation", "Maintains high resolution headroom"]
  }
];

export const AI_INTELLIGENCE_HIGHLIGHTS = [
  {
    title: "Multi-Modal Vision & Speech Grounding",
    description: "AutoCut AI does not blindly guess cut points. It understands the emotional curve of dialogue, gestures, and audio dynamics simultaneously.",
    metric: "120 FPS scene analysis",
  },
  {
    title: "Explainable Cut Decision Lists",
    description: "Every cut, zoom, and audio duck comes with rationale metadata. You can inspect why a clip was trimmed or tweak the decision in one click.",
    metric: "100% NLE Timeline Compatible",
  },
  {
    title: "Native Premiere & Resolve Roundtrip",
    description: "Not locked into our web preview. Download Final Cut Pro XML or DaVinci Resolve timelines to finish your grade in your favorite professional suite.",
    metric: "XML / FCPXML / EDL",
  },
];
