import { GlowBackdrop } from "@/components/landing/visuals/glow-backdrop";
import { Navbar } from "@/components/landing/navigation/navbar";
import { HeroSection } from "@/components/landing/hero/hero-section";
import { DemoSection } from "@/components/landing/product-demo/demo-section";
import { HowItWorksSection } from "@/components/landing/how-it-works/how-it-works-section";
import { BeforeAfterSection } from "@/components/landing/before-after/before-after-section";
import { FeaturesSection } from "@/components/landing/features/features-section";
import { AiIntelligenceSection } from "@/components/landing/ai-intelligence/ai-intelligence-section";
import { AiWorkflowSection } from "@/components/landing/ai-workflow/ai-workflow-section";
import { UseCasesSection } from "@/components/landing/use-cases/use-cases-section";
import { ComparisonSection } from "@/components/landing/comparison/comparison-section";
import { FaqSection } from "@/components/landing/faq/faq-section";
import { CtaSection } from "@/components/landing/cta/cta-section";
import { Footer } from "@/components/landing/footer/footer";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-background text-foreground overflow-x-hidden">
      <GlowBackdrop />
      <Navbar />

      <main>
        <HeroSection />
        <DemoSection />
        <HowItWorksSection />
        <BeforeAfterSection />
        <FeaturesSection />
        <AiIntelligenceSection />
        <AiWorkflowSection />
        <UseCasesSection />
        <ComparisonSection />
        <FaqSection />
        <CtaSection />
      </main>

      <Footer />
    </div>
  );
}
