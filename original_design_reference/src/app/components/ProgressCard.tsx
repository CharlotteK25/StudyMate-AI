interface ProgressBarProps {
  label: string;
  value: number;
  color?: string;
}

function ProgressBar({ label, value, color = "#4ade80" }: ProgressBarProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-500">{label}</span>
        <span className="text-xs font-medium text-gray-700">{value}%</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

const subjects = [
  { label: "Mathematics", value: 82, color: "#4ade80" },
  { label: "Physics", value: 67, color: "#86efac" },
  { label: "Chemistry", value: 74, color: "#4ade80" },
  { label: "History", value: 91, color: "#86efac" },
  { label: "Literature", value: 58, color: "#4ade80" },
];

export function StudyProgressCard() {
  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] p-5 shadow-sm flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-gray-900">Study Progress</h3>
          <p className="text-xs text-gray-400 mt-0.5">% completed this week</p>
        </div>
        <div className="w-10 h-10 rounded-xl bg-[#f0fdf4] flex items-center justify-center">
          <span className="text-lg">📚</span>
        </div>
      </div>
      <div className="flex flex-col gap-3">
        {subjects.map((s) => (
          <ProgressBar key={s.label} label={s.label} value={s.value} color={s.color} />
        ))}
      </div>
    </div>
  );
}
