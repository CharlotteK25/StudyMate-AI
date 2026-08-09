import { useState } from "react";
import { BookOpen, LayoutDashboard, FileText, CreditCard, HelpCircle, MessageCircle, User, Menu, X, BarChart2, Lightbulb } from "lucide-react";

const navLinks = [
  { label: "Dashboard", icon: LayoutDashboard, href: "#dashboard" },
  { label: "Notes", icon: FileText, href: "#notes" },
  { label: "Flashcards", icon: CreditCard, href: "#flashcards" },
  { label: "Quiz", icon: HelpCircle, href: "#quiz" },
  { label: "AI Chat", icon: MessageCircle, href: "#ai-chat" },
  { label: "Analytics", icon: BarChart2, href: "#analytics" },
  { label: "Recommendations", icon: Lightbulb, href: "#recommendations" },
  { label: "Profile", icon: User, href: "#profile" },
];

interface NavBarProps {
  activeLink: string;
  onLinkClick: (label: string) => void;
}

export function NavBar({ activeLink, onLinkClick }: NavBarProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 w-full bg-white border-b border-[rgba(0,0,0,0.08)] shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <a href="#dashboard" className="flex items-center gap-2 shrink-0" onClick={() => onLinkClick("Dashboard")}>
          <div className="w-8 h-8 rounded-lg bg-[#4ade80] flex items-center justify-center">
            <BookOpen size={16} className="text-white" />
          </div>
          <span className="font-semibold text-gray-900 text-sm tracking-tight">StudyMate AI</span>
        </a>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {navLinks.map(({ label, icon: Icon, href }) => {
            const isActive = activeLink === label;
            return (
              <a
                key={label}
                href={href}
                onClick={() => onLinkClick(label)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
                  isActive
                    ? "bg-[#f0fdf4] text-[#16a34a] font-medium"
                    : "text-gray-500 hover:text-gray-900 hover:bg-gray-100"
                }`}
              >
                <Icon size={15} />
                {label}
              </a>
            );
          })}
        </div>

        {/* Avatar */}
        <div className="hidden md:flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#bbf7d0] flex items-center justify-center text-[#15803d] text-xs font-semibold">
            JS
          </div>
        </div>

        {/* Mobile toggle */}
        <button
          className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden border-t border-[rgba(0,0,0,0.08)] bg-white px-4 py-3 flex flex-col gap-1">
          {navLinks.map(({ label, icon: Icon, href }) => {
            const isActive = activeLink === label;
            return (
              <a
                key={label}
                href={href}
                onClick={() => { onLinkClick(label); setMobileOpen(false); }}
                className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-all ${
                  isActive
                    ? "bg-[#f0fdf4] text-[#16a34a] font-medium"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                <Icon size={16} />
                {label}
              </a>
            );
          })}
        </div>
      )}
    </nav>
  );
}
