import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
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
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#06070b] text-[#f3f4f6] selection:bg-violet-600/30 selection:text-white">
        {children}
      </body>
    </html>
  );
}
