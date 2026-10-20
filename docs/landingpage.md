# AutoCut AI — Landing Page Technology & Experience Guide

> **Scope:** Marketing/landing page only. This document does **not** change `tools.md`, the editor architecture, the Python services, or the rendering engine.
>
> **Non-negotiable:** Next.js App Router + React + **strict TypeScript** + **Tailwind CSS v4**. Prefer free, self-hostable, source-available components and libraries. No paid UI kits, subscriptions, or paid APIs required to build the landing page.

## 1. Goal

Build a visually exceptional, cinematic, responsive landing page for **AutoCut AI**, an autonomous AI video editor. The website should communicate the product immediately: **upload raw clips, describe the edit, and get a polished video**. It should look like a high-end creative-software product, not a generic AI chatbot or template SaaS.

The landing page is a **marketing experience**, not the actual editing interface. Its 3D scenes, particles, text animations, interactive demonstrations, and scroll effects are frontend presentation only.

## 2. Required Foundation

| Tool | Purpose | Decision | Cost / notes |
|---|---|---|---|
| [Next.js](https://nextjs.org/) | App Router, SEO, routing, image optimization | **Required** | Free/open-source framework; hosting costs depend on provider |
| [React](https://react.dev/) | Component architecture | **Required** | Free |
| [TypeScript](https://www.typescriptlang.org/) | Type safety, maintainable components | **Required** | Free; enable `strict: true`; no JavaScript component files |
| [Tailwind CSS v4](https://tailwindcss.com/) | Styling, responsive layouts, design tokens | **Required** | Free |
| [shadcn/ui](https://ui.shadcn.com/) | Accessible, customizable UI primitives | **Preferred** | Free; install only needed components |
| [Radix UI](https://www.radix-ui.com/primitives) | Accessible dialogs, menus, popovers | **As needed** | Free |
| [Lucide React](https://lucide.dev/) | Consistent SVG icons | **Preferred** | Free |
| [`next/font`](https://nextjs.org/docs/app/api-reference/components/font) | Self-hosted optimized fonts | **Required** | Built into Next.js; check each font license |

**Architecture rule:** Default to React Server Components for static marketing content. Isolate animated elements, Thrine embeds, WebGL scenes, and browser-dependent code in small `"use client"` components. Do not convert the entire landing page into one client component.

## 3. Animation Libraries — Primary Choices

| Tool | Best use | Priority | Free-use rule |
|---|---|---|---|
| [Motion for React](https://motion.dev/docs/react) (`motion`) | Hero entrance, staggered text, scroll reveals, hover effects, transitions | **Primary** | Core library is free; **do not use Motion+ paid UI or private registry** |
| [Lenis](https://lenis.darkroom.engineering/) (`lenis`) | Smooth scrolling and coordinated scroll experiences | **Optional** | Free, MIT; use only if it improves UX and accessibility |
| [React Bits](https://reactbits.dev/) | Animated text, backgrounds, interactive cards, visual accents | **Selected components** | Free for personal/commercial use, **MIT + Commons Clause**; not equivalent to unrestricted MIT; review per-component dependencies |
| [Motion Primitives](https://motion-primitives.com/) | Tasteful animated text, reveal effects, UI microinteractions | **Selected components** | MIT, free; do not duplicate effects already built with Motion |
| [Magic UI](https://magicui.design/) | Marquees, animated beams, borders, visual feature highlights | **Selected free components** | Use free/open components; skip any premium templates |
| [Aceternity UI](https://ui.aceternity.com/) | Spotlight, background beams, 3D cards, animated sections | **Selected free components** | Free component tier exists; **do not use paid blocks or templates** |
| [tsParticles](https://particles.js.org/) | Particle fields, interactive particles, occasional confetti | **Optional** | Free/MIT; avoid running alongside a heavy Thrine hero |
| Native CSS / Tailwind | Hover states, gradients, subtle transforms, simple keyframes | **Always consider first** | No extra dependency or runtime |

**Selection rule:** These are a **component catalog**, not an instruction to install everything. Pick the smallest combination that creates a coherent visual identity. A good default is **Motion + 1–3 curated components + Thrine hero**.

## 4. Thrine — Landing Page Only

**Reference scene:** [Wild Particle Bloom](https://thrine.app/projects/wild-particle-bloom-1?edit=true&id=106eb259-612f-4de7-95a4-ee2133d3af97)

**Official site:** [thrine.app](https://thrine.app/)

Thrine is a **3D scene editor and export/embed service**, **not** a standard npm React component library. Its editor can export images, videos, or website embeds. Use only the official export/embed workflow provided for a scene; **do not invent an npm package, SDK, or embed API**.

### Approved Thrine uses

- **Hero:** A single cinematic particle bloom or atmospheric 3D centerpiece behind or beside the headline.
- **Feature transition:** One secondary scene if it contributes meaningfully to the narrative.
- **Static/mobile fallback:** A compressed poster image or exported short video when interactive rendering is too expensive.

### Integration guidelines

1. Customize the Thrine scene in its editor.
2. Obtain the actual exported embed code, video, or image from Thrine.
3. Wrap the embed in an isolated client component, e.g. `components/landing/visuals/thrine-hero.tsx`.
4. Give the scene a fixed aspect ratio, loading fallback, descriptive accessible label, and appropriate `iframe` title if embedded in a frame.
5. Lazy-load below-the-fold scenes. Do not block the headline or CTA on the scene loading.
6. Disable or replace heavy interactive rendering on low-power devices and when `prefers-reduced-motion` is set.
7. Keep a locally owned fallback asset so the page remains usable if an external embed fails.
8. Verify export rights and commercial usage terms before production release.

**Free-only caveat:** Thrine's terms state that the service is **free during beta**, but may introduce paid plans, limits, or premium features. Therefore it is an **optional enhancement, not a permanent zero-cost dependency**. Never build a critical user flow that requires an active Thrine subscription or hosted embed. If its free terms change, use an exported asset where permitted or replace the visual with self-hosted Three.js/React Three Fiber.

## 5. Advanced 3D / WebGL Alternatives (Free, Self-Hosted)

| Library | Purpose | When to use |
|---|---|---|
| [Three.js](https://threejs.org/) | Core 3D/WebGL graphics | For fully custom, self-hosted scenes |
| [React Three Fiber](https://r3f.docs.pmnd.rs/) (`@react-three/fiber`) | React integration for Three.js | When 3D visuals must respond to React state or user input |
| [Drei](https://github.com/pmndrs/drei) (`@react-three/drei`) | R3F helpers, controls, environment, text | Alongside React Three Fiber |
| [OGL](https://github.com/oframe/ogl) | Lightweight WebGL rendering | For focused shaders and procedural backgrounds |
| [Theatre.js](https://www.theatrejs.com/) | Keyframe and cinematic animation authoring | Optional, only if a custom scene needs choreographed animation |
| [@react-three/postprocessing](https://github.com/pmndrs/react-postprocessing) | Bloom, depth-of-field and postprocessing | Use sparingly; GPU-intensive |

**Important:** Choose **Thrine embed OR custom R3F scene** for the hero by default, **not both**. For React 19 use the compatible stable React Three Fiber major version; do not adopt alpha releases casually.

## 6. Optional Supporting Libraries

| Tool | Use | Notes |
|---|---|---|
| [Embla Carousel](https://www.embla-carousel.com/) | Testimonials, before/after samples, feature cards | Prefer to large carousel frameworks |
| [Lottie React](https://lottiereact.com/) | Lightweight pre-authored vector animations | Optional; verify licenses of animation assets separately |
| [Zod](https://zod.dev/) | Contact/waitlist form validation | Only if landing page has forms |
| [React Hook Form](https://react-hook-form.com/) | Form state | Only if needed; not required for simple CTA |
| [next/image](https://nextjs.org/docs/app/api-reference/components/image) | Responsive image delivery | Built into Next.js |
| [Playwright](https://playwright.dev/) | Cross-browser/responsive tests | Free/open-source |
| [Vitest](https://vitest.dev/) + [Testing Library](https://testing-library.com/) | Component tests | Free/open-source |
| [Lighthouse](https://developer.chrome.com/docs/lighthouse/overview) | Performance, accessibility and SEO audits | Free |

Avoid adding a second state-management framework, large analytics SDKs, a second CSS framework, or an animation library merely to animate one button.

## 7. Landing Page Sections & Suggested Effects

| Section | Content / user goal | Suggested implementation |
|---|---|---|
| **1. Navigation** | Brand, Product, How It Works, Features, FAQ, Sign In, Get Started | shadcn/ui + Tailwind; accessible mobile menu |
| **2. Cinematic Hero** | "Your footage. Your vision. Edited by AI." + short value proposition + CTA | **Thrine Wild Particle Bloom** with a static fallback; Motion text stagger |
| **3. Product Demonstration** | Show raw clips + a natural-language prompt transforming into a finished preview | Custom React/TypeScript sequence; lightweight preview video; not a fake functioning editor |
| **4. How It Works** | Upload → Describe → AI understands → Plan → Render → Refine | Motion scroll reveals; Magic UI/Aceternity free accents |
| **5. Before / After** | Visually prove editing improvements | Embla or accessible comparison slider; actual permitted sample media |
| **6. Professional Capabilities** | Cuts, transitions, grading, sound, captions, motion | Grid with restrained interactive hover and example visuals |
| **7. AI Intelligence** | Scene understanding, shot selection, narrative pacing, grounded timeline | Motion Primitives + small diagrams or animation |
| **8. Editing Workflow** | Prompt → media analysis → editing plan → FFmpeg/MLT rendering | Interactive diagram; no backend required for marketing demo |
| **9. Use Cases** | Creators, travel reels, businesses, marketing, education | Responsive cards; small curated animations |
| **10. Comparison** | Manual editing versus autonomous first cut | Accessible table with truthful claims, no fabricated metrics |
| **11. FAQ** | Supported footage, revisions, privacy, exports, roadmap | shadcn accordion |
| **12. Final CTA** | "Turn your clips into a story." | Motion reveal + clear Get Started button |
| **13. Footer** | Docs, GitHub, privacy, terms, contact | Static, fast, accessible |

**Visual direction:** Dark cinematic background; carefully limited electric violet/cyan highlights; large expressive typography; crisp product UI mockups; spacious layouts; subtle film grain; restrained bloom; one strong hero focal point. Avoid overwhelming the page with unrelated effects.

## 8. Motion Design Rules

- Animate to explain **editing, transformation, or storytelling**—not merely to show off effects.
- Keep headlines and CTAs readable even when all JavaScript is disabled or animations fail.
- Favor `transform` and `opacity` animations over expensive layout changes.
- Respect `prefers-reduced-motion`; provide static alternatives.
- No autoplay audio. Video demos should be muted by default with accessible controls.
- Avoid scroll hijacking and ensure keyboard navigation, focus visibility, and native scrolling work.
- Use only one primary particle/WebGL animation in the initial viewport.
- Never animate every element continuously; pause effects offscreen.
- Keep mobile interactions touch-friendly and avoid hover-only information.
- Ensure sufficient contrast over moving backgrounds with gradients/scrims.

## 9. Performance, Accessibility, SEO

**Performance**
- Serve a lightweight hero poster immediately; load the 3D scene after critical content.
- Prefer responsive `next/image` assets and compressed modern image formats.
- Lazy-load heavy client components and noncritical videos.
- Avoid importing all of Three.js, multiple particle engines, or entire component catalogs for a single visual.
- Test low-end mobile devices, Safari, and reduced-power modes.
- Treat Core Web Vitals as acceptance criteria, not afterthoughts.

**Accessibility**
- Semantic headings, landmarks, accessible navigation, keyboard operation, visible focus rings.
- Reduced-motion support and captions/transcripts for demo videos.
- Avoid flashing effects, scroll traps, autoplay sound, and essential content inside canvas only.

**SEO**
- Metadata, Open Graph images, canonical URL, sitemap, structured content and indexable page copy.
- Static/server-render the primary value proposition and product explanations.

## 10. Suggested Module-Wise Frontend Layout

```text
frontend/
└── src/
    ├── app/
    │   ├── (marketing)/
    │   │   ├── page.tsx
    │   │   └── layout.tsx
    │   └── globals.css
    ├── components/
    │   ├── landing/
    │   │   ├── navigation/
    │   │   ├── hero/
    │   │   ├── product-demo/
    │   │   ├── how-it-works/
    │   │   ├── before-after/
    │   │   ├── features/
    │   │   ├── ai-workflow/
    │   │   ├── use-cases/
    │   │   ├── faq/
    │   │   ├── cta/
    │   │   ├── footer/
    │   │   └── visuals/
    │   │       ├── thrine-hero.tsx
    │   │       ├── hero-poster.tsx
    │   │       └── particle-fallback.tsx
    │   └── ui/
    ├── hooks/
    ├── lib/
    │   └── animations/
    └── styles/
```

Adapt the `frontend/` folder name to the actual repository; do **not** rename an existing app solely to match this example.

## 11. Recommended Installation Strategy

**Start with the essentials** (inside the Next.js frontend directory):

```bash
npm install motion lucide-react
```

Use the existing Next.js, Tailwind, and shadcn setup; do not reinstall them if already present.

**Add only if the design requires them:**

```bash
npm install lenis embla-carousel-react
```

**For a custom self-hosted 3D alternative to Thrine:**

```bash
npm install three @react-three/fiber @react-three/drei
npm install -D @types/three
```

**For optional particle effects instead of Thrine:**

```bash
npm install @tsparticles/react @tsparticles/slim
```

**Copy curated free components** from React Bits, Motion Primitives, Magic UI, or Aceternity UI only after checking their specific license, package dependencies, TypeScript variant, and Tailwind v4 compatibility. Avoid bulk installing four UI collections.

**Thrine:** Do not run an invented `npm install thrine`. Export/embed from the Thrine editor using its actual provided output.

## 12. Cost & Licensing Guardrails

1. **No paid UI kits, premium templates, Motion+, paid animation registries, or subscription-only features.**
2. **Thrine is free only during its current beta** and may change pricing or usage limits; treat it as optional and replaceable.
3. **React Bits is free for personal/commercial use but uses MIT + Commons Clause**; check the license before redistributing components as part of a competing UI library.
4. **Aceternity offers both free components and paid blocks**; only choose explicitly free components.
5. Assets are separate from libraries: fonts, photos, videos, 3D models, sound effects, and Lottie files require their own usage rights.
6. Free/open-source code does not mean zero hosting, bandwidth, storage, or GPU costs.
7. Before release, recheck licenses and third-party terms for the exact versions/assets actually used.

## 13. Build Order

1. Build static, responsive semantic layout and design tokens.
2. Finish mobile navigation, hero messaging, and CTA first.
3. Add product-demo storytelling with actual permitted sample media.
4. Add Motion transitions and a **single** Thrine hero embed with fallback.
5. Add selected free component effects only where they improve clarity.
6. Implement remaining sections, SEO, accessibility, and reduced-motion handling.
7. Audit real mobile performance and eliminate heavy or redundant effects.

## 14. Final Decisions

- **Landing page framework:** Next.js App Router + React + strict TypeScript + Tailwind CSS v4.
- **Primary animation engine:** Motion for React.
- **3D hero preference:** Thrine **Wild Particle Bloom** (optional, beta-only free) with a self-hosted fallback.
- **Curated component sources:** React Bits, Motion Primitives, Magic UI, and Aceternity UI **free components only**.
- **Smooth scroll:** Lenis only if it does not degrade accessibility.
- **Custom WebGL fallback:** Three.js + stable React Three Fiber + Drei, or OGL for simpler shaders.
- **UI base:** shadcn/ui + Radix + Lucide.
- **No backend/AI/editor dependency changes:** This document governs the **marketing landing page only**.

## 15. References

- Thrine: https://thrine.app/ and https://thrine.app/terms
- Motion: https://motion.dev/docs/react
- React Bits: https://github.com/DavidHDev/react-bits
- Motion Primitives: https://github.com/ibelick/motion-primitives
- Magic UI: https://magicui.design/
- Aceternity UI: https://ui.aceternity.com/pricing
- Lenis: https://github.com/darkroomengineering/lenis
- React Three Fiber: https://r3f.docs.pmnd.rs/getting-started/installation
- tsParticles: https://github.com/tsparticles/tsparticles

---

**North star:** The visitor should feel the quality of AutoCut AI within seconds—but the site must remain fast, understandable, accessible, and usable even without its animations.
