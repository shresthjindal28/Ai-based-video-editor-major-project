export interface NavItem {
  label: string;
  href: string;
  badge?: string;
}

export const NAV_LINKS: NavItem[] = [
  { label: "Product", href: "#demo" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Before & After", href: "#before-after" },
  { label: "Capabilities", href: "#features" },
  { label: "Architecture", href: "#workflow" },
  { label: "Comparison", href: "#comparison" },
  { label: "FAQ", href: "#faq" },
];
