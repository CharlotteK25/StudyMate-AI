import { FileText, CreditCard, Upload, Brain } from "lucide-react";

const stats = [
  {
    label: "Recent Notes",
    value: "24",
    sub: "3 added today",
    icon: FileText,
    bg: "#f0fdf4",
    color: "#16a34a",
    trend: "+12%",
  },
  {
    label: "Flashcards Generated",
    value: "156",
    sub: "18 reviewed today",
    icon: CreditCard,
    bg: "#eff6ff",
    color: "#2563eb",
    trend: "+8%",
  },
  {
    label: "Files Uploaded",
    value: "47",
    sub: "2 uploaded today",
    icon: Upload,
    bg: "#fdf4ff",
    color: "#9333ea",
    trend: "+5%",
  },
  {
    label: "AI Summaries",
    value: "31",
    sub: "4 generated today",
    icon: Brain,
    bg: "#fff7ed",
    color: "#ea580c",
    trend: "+18%",
  },
];

export function StatsCards() {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((s) => {
        const Icon = s.icon;
        return (
          <div
            key={s.label}
            className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] p-4 shadow-sm flex flex-col gap-3 hover:shadow-md transition-shadow duration-200"
          >
            <div className="flex items-center justify-between">
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ backgroundColor: s.bg }}
              >
                <Icon size={17} style={{ color: s.color }} />
              </div>
              <span className="text-xs font-medium text-[#16a34a] bg-[#f0fdf4] px-2 py-0.5 rounded-lg">
                {s.trend}
              </span>
            </div>
            <div>
              <div className="text-2xl font-semibold text-gray-900">{s.value}</div>
              <div className="text-xs text-gray-400 mt-0.5">{s.label}</div>
              <div className="text-xs text-gray-300 mt-0.5">{s.sub}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
