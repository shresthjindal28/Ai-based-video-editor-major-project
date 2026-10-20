import { AI_INTELLIGENCE_HIGHLIGHTS } from "@/lib/constants/features";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Scissors, Sparkles } from "lucide-react";

export function AiIntelligenceSection() {
  return (
    <section className="py-24 bg-[#100e0c]/80 border-y border-white/6" id="intelligence">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <Badge variant="cyan"><Sparkles className="w-3 h-3" /> Your taste makes the difference</Badge>
          <h2 className="mt-6 font-serif text-3xl sm:text-4xl text-[#fff8ee]">A useful first cut.<br /><span className="italic text-gradient-primary">An editor still in charge.</span></h2>
          <p className="mt-5 text-stone-300 leading-relaxed">The best edit is more than a shorter timeline. It is knowing when to hold a reaction, let a line breathe, or cut to the detail that says it all.</p>
          <div className="mt-6 space-y-5">
            {AI_INTELLIGENCE_HIGHLIGHTS.map((item) => (
              <div key={item.title}>
                <h3 className="text-white font-semibold">{item.title}</h3>
                <p className="mt-1 text-sm text-stone-400 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
        <Card glow className="p-6 sm:p-8">
          <p className="text-xs uppercase tracking-widest text-primary">Inside an example edit</p>
          <h3 className="mt-3 text-2xl font-serif text-white">A cut with a purpose.</h3>
          <div className="mt-6 space-y-4">
            {[
              ["00:03", "Open on the strongest line", "Bring the main idea forward so the viewer knows why to stay."],
              ["00:08", "Show what the speaker means", "Use the coastal shot to give the dialogue a sense of place."],
              ["00:16", "Keep the pause that matters", "Tighten the false start, but leave the breath before the key point."],
              ["00:41", "Give the ending room to land", "Let the final shot hold before the closing title."],
            ].map(([time, title, description]) => (
              <div key={time} className="rounded-2xl bg-black/40 border border-white/10 p-4">
                <div className="flex gap-3 items-center"><Scissors className="w-4 h-4 text-primary shrink-0" /><span className="text-xs text-primary">{time}</span><h4 className="text-sm text-white">{title}</h4></div>
                <p className="mt-2 text-sm text-stone-400">{description}</p>
              </div>
            ))}
          </div>
          <p className="mt-5 text-xs text-stone-500">Illustrative editing notes. Every suggestion is a starting point for your review.</p>
        </Card>
      </div>
    </section>
  );
}
