export interface RawClip {
  id: string;
  name: string;
  duration: string;
  tag: string;
  resolution: string;
  fps: string;
  thumbnailColor: string;
}

export interface CutMarker {
  id: string;
  time: string;
  label: string;
  action: "trim" | "b-roll" | "punch-in" | "audio-duck" | "color-grade";
}

export const SAMPLE_RAW_CLIPS: RawClip[] = [
  {
    id: "clip-1",
    name: "A-Cam_Chef_Cooking.mov",
    duration: "04:12",
    tag: "Cooking Process",
    resolution: "4K DCI",
    fps: "24fps",
    thumbnailColor: "from-blue-600/30 to-slate-900",
  },
  {
    id: "clip-2",
    name: "Skillet_Closeup.mp4",
    duration: "01:45",
    tag: "Skillet Detail",
    resolution: "4K UHD",
    fps: "60fps",
    thumbnailColor: "from-emerald-600/30 to-slate-900",
  },
  {
    id: "clip-3",
    name: "Ingredients_Detail.mov",
    duration: "02:30",
    tag: "B-Roll Detail",
    resolution: "4K DCI",
    fps: "120fps",
    thumbnailColor: "from-purple-600/30 to-slate-900",
  },
  {
    id: "clip-4",
    name: "Kitchen_BehindTheScenes.mp4",
    duration: "03:15",
    tag: "Action / Motion",
    resolution: "4K UHD",
    fps: "60fps",
    thumbnailColor: "from-amber-600/30 to-slate-900",
  },
];

export const DEMO_PRESET_PROMPTS = [
  "Make a short cooking reel: open on the sizzling skillet, bring the food details closer, and finish with warm color and bold captions.",
  "Create a recipe teaser for Reels: focus on the pan, highlight the preparation, and keep the captions short and easy to read.",
  "Make a calm kitchen story: hold on the cooking details, use a warm look, and let the preparation set the pace.",
];

export const TIMELINE_CUTS: CutMarker[] = [
  { id: "cut-1", time: "00:03", label: "Cold Hook Cut", action: "punch-in" },
  { id: "cut-2", time: "00:08", label: "Skillet Detail Cutaway", action: "b-roll" },
  { id: "cut-3", time: "00:16", label: "Silence Trim (-2.1s)", action: "trim" },
  { id: "cut-4", time: "00:24", label: "Bass Drop Transition", action: "audio-duck" },
  { id: "cut-5", time: "00:32", label: "Macro Detail Punch", action: "b-roll" },
  { id: "cut-6", time: "00:41", label: "Outro Fade & Title", action: "color-grade" },
];
