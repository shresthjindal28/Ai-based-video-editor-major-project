export interface FAQItem {
  id: string;
  question: string;
  answer: string;
  category: "General" | "Formats & Export" | "Workflow & Revisions" | "Privacy";
}

export const FAQ_ITEMS: FAQItem[] = [
  {
    id: "faq-1",
    category: "Formats & Export",
    question: "What camera formats and color profiles are supported?",
    answer: "AutoCut AI natively supports 8-bit, 10-bit, and 12-bit footage including Apple ProRes, MP4, and MOV up to 8K resolution. It includes built-in color-science transforms for Sony S-Log3/S-Gamut3.Cine, Apple Log, Canon C-Log2/3, Panasonic V-Log, and standard Rec.709 footage."
  },
  {
    id: "faq-2",
    category: "Workflow & Revisions",
    question: "Can I revise the edit, or am I locked into what the AI produces?",
    answer: "You are never locked in. AutoCut AI generates an editable cut decision list. You can ask for prompt adjustments (e.g. 'Make the intro 5 seconds shorter' or 'Add more drone cutaways during the second minute'), manually trim cuts in our web timeline editor, or export a standard Final Cut Pro XML / DaVinci Resolve project to finish in your favorite NLE."
  },
  {
    id: "faq-3",
    category: "Privacy",
    question: "Is my video footage used to train AI models?",
    answer: "Absolutely not. Your footage, audio tracks, and transcripts are strictly processed within isolated, ephemeral GPU instances and are never added to any training dataset for public or foundation models. Once rendering is complete and your session ends, media is retained only according to your project retention preferences."
  },
  {
    id: "faq-4",
    category: "General",
    question: "How does AutoCut AI know when to make cuts?",
    answer: "AutoCut AI uses a multi-modal reasoning engine that coordinates Whisper speech transcription, visual scene segmentation, acoustic energy analysis, and face-tracking. It identifies the conversational intent, strips out verbal hesitations and awkward silences, and cuts on natural linguistic and emotional pauses."
  },
  {
    id: "faq-5",
    category: "Formats & Export",
    question: "What export options and resolutions are available?",
    answer: "You can download master files in H.264, H.265 (HEVC), and Apple ProRes 422 up to 4K 60fps with HDR10/HLG color flags. You can also export SRT/VTT caption files and EDL/XML timeline project files for Premiere Pro, DaVinci Resolve, and Final Cut Pro."
  },
  {
    id: "faq-6",
    category: "Workflow & Revisions",
    question: "How does music beat synchronization work?",
    answer: "You can either upload your own soundtrack or select from our royalty-free library. Our audio analysis pipeline detects transients, downbeats, and tempo shifts, naturally aligning video cuts and punch-in zooms to musical energy peaks while auto-ducking volume underneath voice tracks."
  },
  {
    id: "faq-7",
    category: "General",
    question: "What is the pricing during the private beta?",
    answer: "AutoCut AI is currently free during our private beta. Every invited creator receives 10 complimentary 4K exports and full timeline XML exports. Paid tiers for high-volume enterprise rendering will be introduced later with transparent, usage-based pricing."
  }
];
