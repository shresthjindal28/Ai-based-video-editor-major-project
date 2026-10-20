export interface NavItem {
  label: string;
  href: string;
  badge?: string;
}

export const NAV_LINKS: NavItem[] = [
  { label: "Product", href: "#demo" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Before & After", href: "#before-after" },
  { label: "Editing Tools", href: "#features" },
  { label: "Your Workflow", href: "#workflow" },
  { label: "Comparison", href: "#comparison" },
  { label: "FAQ", href: "#faq" },
];
