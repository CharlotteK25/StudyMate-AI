import { Upload, FileText, Layers, BookOpen, Sparkles, MessageSquare } from "lucide-react";
import { useState } from "react";

const actions = [
  { label: "Upload Notes", icon: Upload, color: "#16a34a", bg: "#f0fdf4", hoverBg: "#dcfce7" },
  { label: "Generate Summary", icon: Sparkles, color: "#9333ea", bg: "#fdf4ff", hoverBg: "#f3e8ff" },
  { label: "Generate Formulas", icon: Layers, color: "#2563eb", bg: "#eff6ff", hoverBg: "#dbeafe" },
  { label: "Create Flashcards", icon: CreditCardIcon, color: "#ea580c", bg: "#fff7ed", hoverBg: "#ffedd5" },
  { label: "Start Quiz", icon: BookOpen, color: "#0891b2", bg: "#ecfeff", hoverBg: "#cffafe" },
  { label: "Ask AI", icon: MessageSquare, color: "#db2777", bg: "#fdf2f8", hoverBg: "#fce7f3" },
];

function CreditCardIcon({ size, style }: { size: number; style?: React.CSSProperties }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" style={style}>
      <rect width="20" height="14" x="2" y="5" rx="2" />
      <line x1="2" x2="22" y1="10" y2="10" />
    </svg>
  );
}

export function QuickActions() {
  const [active, setActive] = useState<string | null>(null);

  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] p-5 shadow-sm flex flex-col gap-4">
      <div>
        <h3 className="text-gray-900">Quick Actions</h3>
        <p className="text-xs text-gray-400 mt-0.5">Jump into your study tasks</p>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
        {actions.map((a) => {
          const Icon = a.icon;
          const isActive = active === a.label;
          return (
            <button
              key={a.label}
              onClick={() => setActive(isActive ? null : a.label)}
              className="flex flex-col items-center gap-2 p-3 rounded-xl border border-transparent transition-all duration-150 cursor-pointer group"
              style={{
                backgroundColor: isActive ? a.hoverBg : a.bg,
                borderColor: isActive ? a.color + "40" : "transparent",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor = a.hoverBg;
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLButtonElement).style.backgroundColor = isActive ? a.hoverBg : a.bg;
              }}
            >
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center transition-transform duration-150 group-hover:scale-110"
                style={{ backgroundColor: a.color + "20" }}
              >
                <Icon size={17} style={{ color: a.color }} />
              </div>
              <span className="text-xs text-center text-gray-600 leading-tight">{a.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
