import type { Metadata } from "next";
import { Geist_Mono, Instrument_Serif, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta",
  subsets: ["latin"],
});

const instrumentSerif = Instrument_Serif({
  variable: "--font-instrument",
  subsets: ["latin"],
  weight: "400",
  style: ["normal", "italic"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AutoCut AI — Autonomous AI Video Editor",
  description:
    "Upload raw footage, describe your vision, and get a polished 4K video. Autonomous multi-modal video editing with frame-accurate pacing, Sony S-Log & Apple Log grading, and studio sound.",
  keywords: [
    "AI video editor",
    "autonomous video editing",
    "AutoCut AI",
    "multi-modal video AI",
    "Sony S-Log grading",
    "Premiere Pro XML export",
    "DaVinci Resolve XML",
  ],
  authors: [{ name: "AutoCut AI Team" }],
  openGraph: {
    title: "AutoCut AI — Autonomous AI Video Editor",
    description: "Your footage. Your vision. Edited by AI in under 2 minutes.",
    url: "https://autocut.ai",
    siteName: "AutoCut AI",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "AutoCut AI — Autonomous AI Video Editor",
    description: "Upload raw footage, describe the edit, get a polished 4K video.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${plusJakarta.variable} ${instrumentSerif.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground selection:bg-primary/40 selection:text-primary-foreground">
        {children}
      </body>
    </html>
  );
}
