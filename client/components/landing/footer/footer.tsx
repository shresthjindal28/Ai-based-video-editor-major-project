import { Film } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-white/8 bg-[#090807] text-stone-400 py-14 text-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between gap-10">
        <div className="max-w-sm">
          <a href="#hero" className="flex items-center gap-2 text-white font-semibold text-lg"><Film className="w-5 h-5 text-primary" /> AutoCut AI</a>
          <p className="mt-4 leading-relaxed">A head start on the edit. More room for your craft. Built for the people who turn footage into stories.</p>
          <p className="mt-6 text-xs text-stone-500">© 2026 AutoCut AI. All rights reserved.</p>
        </div>
        <nav aria-label="Footer" className="grid grid-cols-2 gap-x-12 gap-y-4 content-start">
          <a href="#demo" className="hover:text-white">Try the preview</a>
          <a href="#workflow" className="hover:text-white">Your workflow</a>
          <a href="#features" className="hover:text-white">Editing tools</a>
          <a href="#intelligence" className="hover:text-white">Creative control</a>
          <a href="#how-it-works" className="hover:text-white">How it works</a>
          <a href="#faq" className="hover:text-white">Questions, answered</a>
        </nav>
      </div>
    </footer>
  );
}
