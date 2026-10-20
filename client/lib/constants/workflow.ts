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
    "number": "01",
    "title": "Bring your footage",
    "description": "Add the interview, supporting shots, and music you want to work with. Keep everything for the story together.",
    "badge": "Start with your selects",
    "iconName": "UploadCloud",
    "detail": "Camera clips, phone recordings, and B-roll"
  },
  {
    "number": "02",
    "title": "Set the brief",
    "description": "Tell us who the video is for, how long it should run, and the feeling you want to leave behind.",
    "badge": "Your creative direction",
    "iconName": "MessageSquareCode",
    "detail": "Try a product reel, interview, or social cutdown"
  },
  {
    "number": "03",
    "title": "Find the story",
    "description": "Pick out the strongest lines and useful supporting shots before getting lost in the details.",
    "badge": "Make the moments count",
    "iconName": "BrainCircuit",
    "detail": "Build around the message you want to land"
  },
  {
    "number": "04",
    "title": "Shape the first cut",
    "description": "Get a starting sequence with tighter dialogue and cutaways, ready for your judgment.",
    "badge": "From footage to sequence",
    "iconName": "GitBranch",
    "detail": "Keep, change, or rethink the suggested choices"
  },
  {
    "number": "05",
    "title": "Refine the finish",
    "description": "Review the pacing, look, captions, and sound together. Give each pass a clear creative goal.",
    "badge": "Make it yours",
    "iconName": "Cpu",
    "detail": "Polish the details that define your style"
  },
  {
    "number": "06",
    "title": "Review for delivery",
    "description": "Watch the cut from start to finish and check the framing for every channel before sharing.",
    "badge": "Your final approval",
    "iconName": "CheckCircle2",
    "detail": "Check captions, sound, and the last frame"
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
    "id": "ingest",
    "label": "Gather your media",
    "sublabel": "Start with the clips and music for this edit.",
    "tech": "Your footage",
    "color": "from-amber-500/20 to-rose-500/10 border-amber-500/30"
  },
  {
    "id": "analysis",
    "label": "Find the highlights",
    "sublabel": "Choose the lines and shots that carry the story.",
    "tech": "Your selects",
    "color": "from-amber-500/20 to-rose-500/10 border-amber-500/30"
  },
  {
    "id": "director",
    "label": "Build the sequence",
    "sublabel": "Turn the brief into a first cut worth refining.",
    "tech": "Your first cut",
    "color": "from-amber-500/20 to-rose-500/10 border-amber-500/30"
  },
  {
    "id": "render",
    "label": "Polish the details",
    "sublabel": "Bring pacing, sound, captions, and color together.",
    "tech": "Your finishing pass",
    "color": "from-amber-500/20 to-rose-500/10 border-amber-500/30"
  },
  {
    "id": "delivery",
    "label": "Review and share",
    "sublabel": "Check the finished edit for its destination.",
    "tech": "Your final say",
    "color": "from-amber-500/20 to-rose-500/10 border-amber-500/30"
  }
];

export const USE_CASES = [
  {
    "title": "YouTube editors",
    "description": "Get through the first assembly of interviews, tutorials, and talking-head videos so you can focus on the moments viewers stay for.",
    "badge": "Build a stronger first cut",
    "tags": [
      "Talking heads",
      "B-roll",
      "Pacing"
    ]
  },
  {
    "title": "Social video teams",
    "description": "Turn one shoot into focused edits for different channels. Give every cutdown a clear hook and a reason to keep watching.",
    "badge": "Make the most of every shoot",
    "tags": [
      "Reels",
      "Shorts",
      "Campaign cutdowns"
    ]
  },
  {
    "title": "Brand and freelance editors",
    "description": "Translate the client brief into a starting sequence, then spend your attention on the choices that make the work feel considered.",
    "badge": "Leave room for your craft",
    "tags": [
      "Product stories",
      "Client revisions",
      "Brand style"
    ]
  },
  {
    "title": "Podcast and interview editors",
    "description": "Bring the strongest parts of a conversation forward, clean up the distractions, and keep the speakers sounding like themselves.",
    "badge": "Keep the conversation natural",
    "tags": [
      "Interviews",
      "Dialogue cleanup",
      "Highlight clips"
    ]
  }
];
