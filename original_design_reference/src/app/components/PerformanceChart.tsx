import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const data = [
  { day: "Mon", math: 70, physics: 55, chemistry: 62 },
  { day: "Tue", math: 75, physics: 60, chemistry: 68 },
  { day: "Wed", math: 68, physics: 72, chemistry: 65 },
  { day: "Thu", math: 82, physics: 67, chemistry: 74 },
  { day: "Fri", math: 79, physics: 80, chemistry: 71 },
  { day: "Sat", math: 88, physics: 75, chemistry: 80 },
  { day: "Sun", math: 91, physics: 83, chemistry: 85 },
];

export function PerformanceChart() {
  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] p-5 shadow-sm flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-gray-900">Quiz Performance</h3>
          <p className="text-xs text-gray-400 mt-0.5">Score trends this week</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs bg-[#f0fdf4] text-[#16a34a] px-2 py-1 rounded-lg">Weekly</span>
        </div>
      </div>
      <div className="h-44">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} domain={[40, 100]} />
            <Tooltip
              contentStyle={{ borderRadius: "12px", border: "1px solid #e5e7eb", fontSize: 12 }}
              itemStyle={{ color: "#374151" }}
            />
            <Legend wrapperStyle={{ fontSize: 11, paddingTop: 8 }} />
            <Line type="monotone" dataKey="math" stroke="#4ade80" strokeWidth={2} dot={false} name="Math" />
            <Line type="monotone" dataKey="physics" stroke="#60a5fa" strokeWidth={2} dot={false} name="Physics" />
            <Line type="monotone" dataKey="chemistry" stroke="#f472b6" strokeWidth={2} dot={false} name="Chemistry" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
