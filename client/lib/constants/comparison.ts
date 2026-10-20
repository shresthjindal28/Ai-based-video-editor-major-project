export interface ComparisonRow {
  feature: string;
  manual: string;
  templateAi: string;
  autocut: string;
  highlight?: boolean;
}

export const COMPARISON_DATA: ComparisonRow[] = [
  {
    "feature": "Starting point",
    "manual": "Build the sequence from scratch",
    "templateAi": "Start from a preset structure",
    "autocut": "Start with your footage and creative brief",
    "highlight": true
  },
  {
    "feature": "Repetitive cuts",
    "manual": "Find and trim each pause yourself",
    "templateAi": "Work within the chosen template",
    "autocut": "Use suggested trims as a starting point",
    "highlight": false
  },
  {
    "feature": "B-roll",
    "manual": "Find each supporting shot manually",
    "templateAi": "Choose slots in the template",
    "autocut": "Review cutaways suggested for the dialogue",
    "highlight": false
  },
  {
    "feature": "Creative direction",
    "manual": "Make every decision yourself",
    "templateAi": "Adapt your story to the preset",
    "autocut": "Set the direction and refine the first cut",
    "highlight": true
  },
  {
    "feature": "Review",
    "manual": "Review your assembled sequence",
    "templateAi": "Review the filled template",
    "autocut": "Review the suggested sequence before finishing",
    "highlight": false
  }
];
