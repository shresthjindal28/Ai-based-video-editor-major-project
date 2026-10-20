export interface ComparisonRow {
  feature: string;
  manual: string;
  templateAi: string;
  autocut: string;
  highlight?: boolean;
}

export const COMPARISON_DATA: ComparisonRow[] = [
  {
    feature: "Time per 10-Minute Video",
    manual: "4 to 8 hours of tedious cutting",
    templateAi: "10-20 mins (rigid templates)",
    autocut: "Under 2 minutes autonomous cut",
    highlight: true,
  },
  {
    feature: "Story & Narrative Awareness",
    manual: "High (human editor)",
    templateAi: "None (random cuts or rigid rules)",
    autocut: "High (multi-modal vision + speech understanding)",
    highlight: true,
  },
  {
    feature: "B-Roll Cutaway Sequencing",
    manual: "Manual scrubbing through hours of footage",
    templateAi: "Unrelated stock footage fillers",
    autocut: "Contextual matching using your own footage",
    highlight: true,
  },
  {
    feature: "Color Grading & Log Support",
    manual: "Manual node tree & LUT adjustments",
    templateAi: "Generic filters only (distorts skins)",
    autocut: "Hardware-accurate 3D LUTs for Sony/Canon/Apple Log",
    highlight: false,
  },
  {
    feature: "Timeline Flexibility",
    manual: "Full manual control",
    templateAi: "Locked black box MP4 export only",
    autocut: "Interactive web timeline + Premiere / Resolve XML export",
    highlight: true,
  },
  {
    feature: "Audio Pacing & Beat Sync",
    manual: "Manual keyframing & cut aligning",
    templateAi: "Cuts at fixed arbitrary intervals",
    autocut: "Spectral beat detection + sidechain dialogue ducking",
    highlight: false,
  },
  {
    feature: "Privacy & Model Training",
    manual: "Local files on drive",
    templateAi: "Frequently trained on uploaded media",
    autocut: "Zero training on user assets; encrypted ephemeral processing",
    highlight: false,
  },
];
