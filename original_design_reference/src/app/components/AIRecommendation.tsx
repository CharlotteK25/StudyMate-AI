import { Sparkles, RefreshCw } from "lucide-react";
import { useState } from "react";

const recommendations = [
  "Focus on reviewing your Chemistry formulas — your scores dipped 8% this week. Try 15 minutes of targeted flashcard review before tomorrow's session.",
  "Great progress in Mathematics! Your consistency is paying off. Consider tackling harder practice problems to push toward 95%.",
  "Your Physics scores have been climbing steadily. Keep up the momentum with daily 10-minute revision sessions.",
  "You've been studying for 3 days straight — well done! Consider spacing your History review across shorter, more frequent sessions.",
];

export function AIRecommendation() {
  const [idx, setIdx] = useState(0);
  const [spinning, setSpinning] = useState(false);

  const refresh = () => {
    setSpinning(true);
    setTimeout(() => {
      setIdx((i) => (i + 1) % recommendations.length);
      setSpinning(false);
    }, 600);
  };

  return (
    <div className="bg-gradient-to-br from-[#f0fdf4] to-[#eff6ff] rounded-2xl border border-[rgba(0,0,0,0.07)] p-5 shadow-sm flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-white flex items-center justify-center shadow-sm">
            <Sparkles size={14} className="text-[#9333ea]" />
          </div>
          <h3 className="text-gray-900">AI Recommendation</h3>
        </div>
        <button
          onClick={refresh}
          className="p-1.5 rounded-lg bg-white hover:bg-gray-50 text-gray-400 hover:text-gray-700 transition-all shadow-sm"
          aria-label="Refresh recommendation"
        >
          <RefreshCw size={13} className={spinning ? "animate-spin" : ""} />
        </button>
      </div>
      <p className="text-xs text-gray-600 leading-relaxed">{recommendations[idx]}</p>
      <div className="flex items-center gap-2 mt-1">
        <button className="text-xs bg-[#4ade80] text-white px-3 py-1.5 rounded-lg hover:bg-[#22c55e] transition-colors font-medium">
          Apply Tip
        </button>
        <button className="text-xs text-gray-500 hover:text-gray-700 px-3 py-1.5 rounded-lg hover:bg-white transition-all">
          Dismiss
        </button>
      </div>
    </div>
  );
}
