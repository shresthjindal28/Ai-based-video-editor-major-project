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
    "id": "smart-cuts",
    "title": "Tighter takes, better pacing",
    "category": "Cutting",
    "description": "Skip the repeated takes and long pauses. Get a cleaner starting point while keeping the moments that give your speaker character.",
    "iconName": "Scissors",
    "badge": "Keep the good takes",
    "metric": "Find your rhythm",
    "details": [
      "Trim pauses and false starts",
      "Keep intentional beats",
      "Review the suggested cuts"
    ]
  },
  {
    "id": "color-grading",
    "title": "Bring the look together",
    "category": "Color",
    "description": "Give your first cut a consistent feel, from the opening shot to the last frame. Keep the final grade in your hands.",
    "iconName": "Sliders",
    "badge": "Set the mood",
    "metric": "A consistent starting look",
    "details": [
      "Balance shots across the edit",
      "Explore warm or clean looks",
      "Refine the grade to your taste"
    ]
  },
  {
    "id": "studio-audio",
    "title": "Let the dialogue lead",
    "category": "Sound",
    "description": "Keep voices clear and music in its place, so your audience can follow the story without reaching for the volume.",
    "iconName": "Volume2",
    "badge": "Dialogue first",
    "metric": "Less time riding levels",
    "details": [
      "Reduce distracting background noise",
      "Lower music beneath speech",
      "Review the mix before delivery"
    ]
  },
  {
    "id": "kinetic-captions",
    "title": "Captions that fit the cut",
    "category": "Captions",
    "description": "Make dialogue easy to follow with readable captions that match the pace and personality of your video.",
    "iconName": "Type",
    "badge": "Make every word count",
    "metric": "Style it your way",
    "details": [
      "Review the transcript",
      "Choose a caption style",
      "Check timing and readability"
    ]
  },
  {
    "id": "b-roll-insertion",
    "title": "Put your B-roll to work",
    "category": "Story",
    "description": "Bring supporting shots into the conversation. Find places where a cutaway adds context, covers a trim, or gives a moment room to breathe.",
    "iconName": "Eye",
    "badge": "Use your own footage",
    "metric": "Give the story context",
    "details": [
      "Match cutaways to the topic",
      "Break up long talking-head sections",
      "Review every placement"
    ]
  },
  {
    "id": "smart-reframe",
    "title": "One story, more screens",
    "category": "Delivery",
    "description": "Adapt your edit for a full-length video, a vertical clip, or a square post while keeping the important action in view.",
    "iconName": "Maximize2",
    "badge": "Made for your channels",
    "metric": "Frame for the destination",
    "details": [
      "Plan horizontal and vertical versions",
      "Keep the subject in focus",
      "Review each crop before export"
    ]
  }
];

export const AI_INTELLIGENCE_HIGHLIGHTS = [
  {
    "title": "Keep the moments that matter",
    "description": "A pause can build tension. A glance can carry the scene. Review the suggestions and keep the beats that make the edit yours.",
    "metric": "Story comes first"
  },
  {
    "title": "A first cut you can question",
    "description": "See the purpose behind a trim or cutaway, then decide whether it serves your brief. Your judgment shapes the finished film.",
    "metric": "You call the cut"
  },
  {
    "title": "Make room for the finishing pass",
    "description": "Start with the structure, then focus on the details: shot choices, caption timing, sound, and the final look.",
    "metric": "Ready for your review"
  }
];
