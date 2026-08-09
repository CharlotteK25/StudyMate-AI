import { Flame, CheckCircle2, Circle, Clock, Target } from "lucide-react";

const tasks = [
  { label: "Update Today 11:00 pm", done: true },
  { label: "Correct study sessions", done: false },
  { label: "Review flashcard deck", done: false },
  { label: "Complete physics quiz", done: false },
];

const todayGoal = {
  label: "Today's Study Goal",
  target: 3,
  current: 2,
  unit: "hours",
};

export function Sidebar() {
  return (
    <div className="flex flex-col gap-4">
      {/* Study Streak */}
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] p-5 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-gray-900">Learning Streak</h3>
          <Flame size={18} className="text-orange-400" />
        </div>
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold text-gray-900">3.1</span>
          <span className="text-sm text-gray-400">days</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">Learning days this week</p>
        <div className="mt-3 flex gap-1.5">
          {["M", "T", "W", "T", "F", "S", "S"].map((d, i) => (
            <div
              key={i}
              className={`flex-1 h-6 rounded-md flex items-center justify-center text-xs font-medium transition-all ${
                i < 3
                  ? "bg-[#4ade80] text-white"
                  : i === 3
                  ? "bg-[#bbf7d0] text-[#16a34a]"
                  : "bg-gray-100 text-gray-400"
              }`}
            >
              {d}
            </div>
          ))}
        </div>
      </div>

      {/* Today's Goal */}
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-3">
          <Target size={16} className="text-[#16a34a]" />
          <h3 className="text-gray-900">Today's Study Goal</h3>
        </div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-500">{todayGoal.current} / {todayGoal.target} {todayGoal.unit}</span>
          <span className="text-xs font-medium text-[#16a34a]">{Math.round((todayGoal.current / todayGoal.target) * 100)}%</span>
        </div>
        <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full bg-[#4ade80] transition-all duration-700"
            style={{ width: `${(todayGoal.current / todayGoal.target) * 100}%` }}
          />
        </div>
      </div>

      {/* Upcoming Tasks */}
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] p-5 shadow-sm flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <Clock size={16} className="text-[#2563eb]" />
          <h3 className="text-gray-900">Upcoming Tasks</h3>
        </div>
        <div className="flex flex-col gap-2">
          {tasks.map((t) => (
            <div key={t.label} className="flex items-center gap-2.5 group cursor-pointer">
              {t.done ? (
                <CheckCircle2 size={16} className="text-[#4ade80] shrink-0" />
              ) : (
                <Circle size={16} className="text-gray-300 group-hover:text-[#86efac] shrink-0 transition-colors" />
              )}
              <span
                className={`text-xs leading-snug ${
                  t.done ? "line-through text-gray-300" : "text-gray-600"
                }`}
              >
                {t.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Progress Uploaded */}
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] p-5 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-gray-900">Progress Uploaded</h3>
          <span className="text-xs bg-[#eff6ff] text-[#2563eb] px-2 py-0.5 rounded-lg">This Month</span>
        </div>
        <div className="flex items-baseline gap-1 mb-1">
          <span className="text-3xl font-bold text-gray-900">78</span>
          <span className="text-sm text-gray-400">%</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div className="h-full bg-[#60a5fa] rounded-full" style={{ width: "78%" }} />
        </div>
        <p className="text-xs text-gray-400 mt-2">14 files out of 18 reviewed</p>
      </div>
    </div>
  );
}
