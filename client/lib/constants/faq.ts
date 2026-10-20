export interface FAQItem {
  id: string;
  question: string;
  answer: string;
  category: "General" | "Formats & Export" | "Workflow & Revisions" | "Privacy";
}

export const FAQ_ITEMS: FAQItem[] = [
  {
    "id": "faq-1",
    "category": "General",
    "question": "Who is AutoCut AI for?",
    "answer": "Video editors working on interviews, YouTube videos, brand stories, podcasts, and social cutdowns. It is designed to help with the first assembly and repetitive cleanup while leaving creative decisions with you."
  },
  {
    "id": "faq-2",
    "category": "Workflow & Revisions",
    "question": "Will I still have control over the edit?",
    "answer": "Your brief sets the direction, and the first cut is a starting point. Review the story, pacing, shot choices, and captions before deciding what belongs in the finished video."
  },
  {
    "id": "faq-3",
    "category": "Workflow & Revisions",
    "question": "How should I write my editing brief?",
    "answer": "Include the audience, target length, destination, and tone. For example: make a 45-second product reel, open with the strongest benefit, use the detail shots, and keep the music subtle under dialogue."
  },
  {
    "id": "faq-4",
    "category": "Formats & Export",
    "question": "Can I use footage from different cameras?",
    "answer": "Plan your edit around the camera clips, phone recordings, and supporting shots you already have. Confirm supported file types and upload limits in the beta before preparing a large project."
  },
  {
    "id": "faq-5",
    "category": "Formats & Export",
    "question": "Can I finish in my usual editing software?",
    "answer": "If you need a Premiere Pro, Resolve, or Final Cut Pro handoff, confirm the available timeline export options with the beta team before starting. The preview on this page does not create downloadable project files."
  },
  {
    "id": "faq-6",
    "category": "Privacy",
    "question": "What should I check before uploading client footage?",
    "answer": "Confirm your client has approved the workflow and review the beta terms for storage, access, and deletion. Do this before uploading confidential, embargoed, or licensed material."
  },
  {
    "id": "faq-7",
    "category": "General",
    "question": "Is the preview on this page a real edit?",
    "answer": "The interactive preview demonstrates a sample brief and editing sequence. Its progress and timeline are simulated; it does not process your footage. Beta availability, pricing, and export limits will be shared with invited editors."
  }
];
