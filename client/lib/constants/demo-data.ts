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
    name: "A-Cam_Interview_SLog3.mov",
    duration: "04:12",
    tag: "Talking Head",
    resolution: "4K DCI",
    fps: "24fps",
    thumbnailColor: "from-blue-600/30 to-slate-900",
  },
  {
    id: "clip-2",
    name: "Drone_Coastal_Flyover_4K.mp4",
    duration: "01:45",
    tag: "B-Roll Scenery",
    resolution: "4K UHD",
    fps: "60fps",
    thumbnailColor: "from-emerald-600/30 to-slate-900",
  },
  {
    id: "clip-3",
    name: "B-Cam_Product_Macro_Shots.mov",
    duration: "02:30",
    tag: "B-Roll Detail",
    resolution: "4K DCI",
    fps: "120fps",
    thumbnailColor: "from-purple-600/30 to-slate-900",
  },
  {
    id: "clip-4",
    name: "Gimbal_BehindTheScenes.mp4",
    duration: "03:15",
    tag: "Action / Motion",
    resolution: "4K UHD",
    fps: "60fps",
    thumbnailColor: "from-amber-600/30 to-slate-900",
  },
];

export const DEMO_PRESET_PROMPTS = [
  "Create a fast-paced 45s launch reel: cut dead-air, sync hook to beat drop, warm Kodak 2383 grade, and punch-in on key insights.",
  "Turn the interview into a high-retention 60s YouTube Short: vertical 9:16 reframe, kinetic captions, and sound effects on transitions.",
  "Make a documentary-style montage: subtle J-cuts, ambient audio ducking, slow push-ins, and soft film contrast.",
];

export const TIMELINE_CUTS: CutMarker[] = [
  { id: "cut-1", time: "00:03", label: "Cold Hook Cut", action: "punch-in" },
  { id: "cut-2", time: "00:08", label: "Drone B-Roll Cutaway", action: "b-roll" },
  { id: "cut-3", time: "00:16", label: "Silence Trim (-2.1s)", action: "trim" },
  { id: "cut-4", time: "00:24", label: "Bass Drop Transition", action: "audio-duck" },
  { id: "cut-5", time: "00:32", label: "Macro Detail Punch", action: "b-roll" },
  { id: "cut-6", time: "00:41", label: "Outro Fade & Title", action: "color-grade" },
];
