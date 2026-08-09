import { useState } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend,
  Area, AreaChart, TooltipProps,
} from "recharts";
import { Flame, CreditCard, BookOpen, TrendingUp, TrendingDown, Minus, Clock, Target, Award } from "lucide-react";

// ─── Data ─────────────────────────────────────────────────────────────────────

const WEEKLY = {
  studyHours: [
    { day: "Mon", hours: 2.5, target: 4 },
    { day: "Tue", hours: 4.0, target: 4 },
    { day: "Wed", hours: 3.2, target: 4 },
    { day: "Thu", hours: 5.1, target: 4 },
    { day: "Fri", hours: 3.8, target: 4 },
    { day: "Sat", hours: 6.0, target: 4 },
    { day: "Sun", hours: 2.0, target: 4 },
  ],
  progress: [
    { label: "Wk 1", score: 62 },
    { label: "Wk 2", score: 68 },
    { label: "Wk 3", score: 71 },
    { label: "Wk 4", score: 75 },
    { label: "Wk 5", score: 79 },
    { label: "Wk 6", score: 83 },
    { label: "Wk 7", score: 88 },
  ],
  mastery: [
    { name: "Biology", value: 82, color: "#4ade80" },
    { name: "Chemistry", value: 67, color: "#60a5fa" },
    { name: "Physics", value: 74, color: "#f472b6" },
    { name: "Maths", value: 91, color: "#fb923c" },
    { name: "History", value: 58, color: "#a78bfa" },
  ],
  metrics: {
    streak: 44,
    flashcards: 25,
    sessions: 1031,
    avgScore: 83,
    hoursTotal: 26.6,
    quizzesTaken: 12,
  },
};

const MONTHLY = {
  studyHours: [
    { day: "Jan", hours: 68, target: 80 },
    { day: "Feb", hours: 72, target: 80 },
    { day: "Mar", hours: 85, target: 80 },
    { day: "Apr", hours: 90, target: 80 },
    { day: "May", hours: 78, target: 80 },
    { day: "Jun", hours: 95, target: 80 },
  ],
  progress: [
    { label: "Jan", score: 58 },
    { label: "Feb", score: 63 },
    { label: "Mar", score: 70 },
    { label: "Apr", score: 74 },
    { label: "May", score: 80 },
    { label: "Jun", score: 88 },
  ],
  mastery: [
    { name: "Biology", value: 86, color: "#4ade80" },
    { name: "Chemistry", value: 71, color: "#60a5fa" },
    { name: "Physics", value: 79, color: "#f472b6" },
    { name: "Maths", value: 94, color: "#fb923c" },
    { name: "History", value: 65, color: "#a78bfa" },
  ],
  metrics: {
    streak: 44,
    flashcards: 156,
    sessions: 1031,
    avgScore: 88,
    hoursTotal: 488,
    quizzesTaken: 48,
  },
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

function Trend({ value, suffix = "%" }: { value: number; suffix?: string }) {
  if (value > 0) return (
    <span className="flex items-center gap-0.5 text-[10px] font-medium text-[#16a34a]">
      <TrendingUp size={10} />+{value}{suffix}
    </span>
  );
  if (value < 0) return (
    <span className="flex items-center gap-0.5 text-[10px] font-medium text-[#dc2626]">
      <TrendingDown size={10} />{value}{suffix}
    </span>
  );
  return (
    <span className="flex items-center gap-0.5 text-[10px] font-medium text-gray-400">
      <Minus size={10} />0{suffix}
    </span>
  );
}

// ─── Custom tooltips ──────────────────────────────────────────────────────────

function BarTip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-[rgba(0,0,0,0.09)] rounded-xl px-3 py-2 shadow-lg text-xs">
      <p className="font-semibold text-gray-700 mb-1">{label}</p>
      <p className="text-[#4ade80]">Studied: <strong>{payload[0]?.value}h</strong></p>
      <p className="text-gray-400">Target: {payload[1]?.value}h</p>
    </div>
  );
}

function LineTip({ active, payload, label }: TooltipProps<number, string>) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-[rgba(0,0,0,0.09)] rounded-xl px-3 py-2 shadow-lg text-xs">
      <p className="font-semibold text-gray-700 mb-1">{label}</p>
      <p className="text-[#60a5fa]">Score: <strong>{payload[0]?.value}%</strong></p>
    </div>
  );
}

// ─── Charts ───────────────────────────────────────────────────────────────────

function StudyHoursChart({ data, view }: { data: typeof WEEKLY["studyHours"]; view: "weekly" | "monthly" }) {
  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-5 flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-gray-900">Study Hours</h3>
          <p className="text-xs text-gray-400 mt-0.5">{view === "weekly" ? "Hours per day this week" : "Hours per month this year"}</p>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-[#4ade80]" />Studied</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-[#e5e7eb]" />Target</span>
        </div>
      </div>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={4} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
            <XAxis dataKey="day" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
            <Tooltip content={<BarTip />} cursor={{ fill: "#f0fdf4", radius: 6 }} />
            <Bar dataKey="hours" radius={[6, 6, 0, 0]} maxBarSize={32}>
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.hours >= entry.target ? "#4ade80" : "#86efac"} />
              ))}
            </Bar>
            <Bar dataKey="target" radius={[6, 6, 0, 0]} fill="#e5e7eb" maxBarSize={32} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function ProgressChart({ data, view }: { data: typeof WEEKLY["progress"]; view: "weekly" | "monthly" }) {
  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-5 flex flex-col gap-4">
      <div>
        <h3 className="text-gray-900">{view === "weekly" ? "Weekly" : "Monthly"} Progress</h3>
        <p className="text-xs text-gray-400 mt-0.5">Average quiz score over time</p>
      </div>
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#60a5fa" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#60a5fa" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" vertical={false} />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} domain={[40, 100]} />
            <Tooltip content={<LineTip />} />
            <Area
              type="monotone"
              dataKey="score"
              stroke="#60a5fa"
              strokeWidth={2.5}
              fill="url(#scoreGrad)"
              dot={{ fill: "#60a5fa", strokeWidth: 0, r: 4 }}
              activeDot={{ r: 6, fill: "#2563eb", strokeWidth: 0 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

const RADIAN = Math.PI / 180;
function CustomLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) {
  if (percent < 0.08) return null;
  const r = innerRadius + (outerRadius - innerRadius) * 0.55;
  const x = cx + r * Math.cos(-midAngle * RADIAN);
  const y = cy + r * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} textAnchor="middle" dominantBaseline="central" fill="white" fontSize={10} fontWeight={700}>
      {Math.round(percent * 100)}%
    </text>
  );
}

function MasteryChart({ data }: { data: typeof WEEKLY["mastery"] }) {
  const avg = Math.round(data.reduce((s, d) => s + d.value, 0) / data.length);
  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-5 flex flex-col gap-4">
      <div>
        <h3 className="text-gray-900">Topic Mastery</h3>
        <p className="text-xs text-gray-400 mt-0.5">Scores by subject</p>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative shrink-0" style={{ width: 140, height: 140 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={38}
                outerRadius={62}
                paddingAngle={3}
                dataKey="value"
                labelLine={false}
                label={CustomLabel}
              >
                {data.map((entry, i) => (
                  <Cell key={i} fill={entry.color} strokeWidth={0} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <span className="text-xl font-bold text-gray-900">{avg}%</span>
            <span className="text-[9px] text-gray-400 leading-tight text-center">avg</span>
          </div>
        </div>
        <div className="flex flex-col gap-1.5 flex-1 min-w-0">
          {data.map((d) => (
            <div key={d.name} className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: d.color }} />
              <span className="text-xs text-gray-600 truncate flex-1">{d.name}</span>
              <span className="text-xs font-semibold text-gray-700 tabular-nums">{d.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Metric card ──────────────────────────────────────────────────────────────

function MetricCard({
  icon: Icon, label, value, sub, color, trend,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  sub: string;
  color: string;
  trend: number;
}) {
  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-4 flex flex-col gap-3 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ backgroundColor: color + "18" }}>
          <Icon size={17} style={{ color }} />
        </div>
        <Trend value={trend} />
      </div>
      <div>
        <div className="text-2xl font-bold text-gray-900 tabular-nums">{value}</div>
        <div className="text-xs font-medium text-gray-700 mt-0.5">{label}</div>
        <div className="text-[10px] text-gray-400 mt-0.5">{sub}</div>
      </div>
    </div>
  );
}

// ─── Subject progress bars ────────────────────────────────────────────────────

function SubjectBreakdown({ data }: { data: typeof WEEKLY["mastery"] }) {
  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-5 flex flex-col gap-4">
      <div>
        <h3 className="text-gray-900">Subject Breakdown</h3>
        <p className="text-xs text-gray-400 mt-0.5">Individual mastery scores</p>
      </div>
      <div className="flex flex-col gap-3">
        {data.map((s) => (
          <div key={s.name} className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-600">{s.name}</span>
              <span className="text-xs font-semibold tabular-nums" style={{ color: s.color }}>{s.value}%</span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width: `${s.value}%`, backgroundColor: s.color }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────

type View = "weekly" | "monthly";

export function Analytics() {
  const [view, setView] = useState<View>("weekly");
  const data = view === "weekly" ? WEEKLY : MONTHLY;

  const weeklyMetrics = [
    { icon: Flame, label: "Learning Streak", value: data.metrics.streak, sub: "days in a row", color: "#f97316", trend: 12 },
    { icon: CreditCard, label: "Flashcards Completed", value: data.metrics.flashcards, sub: view === "weekly" ? "this week" : "this month", color: "#2563eb", trend: 8 },
    { icon: BookOpen, label: "Study Sessions", value: data.metrics.sessions, sub: "total sessions", color: "#9333ea", trend: 5 },
    { icon: Target, label: "Avg Quiz Score", value: `${data.metrics.avgScore}%`, sub: "across all quizzes", color: "#16a34a", trend: 4 },
    { icon: Clock, label: "Hours Studied", value: `${data.metrics.hoursTotal}h`, sub: view === "weekly" ? "this week" : "this month", color: "#0891b2", trend: view === "weekly" ? -3 : 11 },
    { icon: Award, label: "Quizzes Taken", value: data.metrics.quizzesTaken, sub: view === "weekly" ? "this week" : "this month", color: "#db2777", trend: 0 },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Page header + toggle */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-gray-900">Progress Analytics</h1>
          <p className="text-sm text-gray-400 mt-0.5">Track your study performance over time</p>
        </div>

        {/* View toggle */}
        <div className="flex items-center p-1 bg-white border border-[rgba(0,0,0,0.08)] rounded-2xl shadow-sm">
          {(["weekly", "monthly"] as View[]).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-5 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                view === v
                  ? "bg-gray-900 text-white shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {v === "weekly" ? "Weekly View" : "Monthly View"}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {weeklyMetrics.map((m) => (
          <MetricCard key={m.label} {...m} />
        ))}
      </div>

      {/* Charts row — bar + line + donut */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <StudyHoursChart data={data.studyHours} view={view} />
        <ProgressChart data={data.progress} view={view} />
        <MasteryChart data={data.mastery} />
      </div>

      {/* Bottom row — subject bars + summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <SubjectBreakdown data={data.mastery} />
        </div>

        {/* Insight card */}
        <div className="bg-gradient-to-br from-[#f0fdf4] via-white to-[#eff6ff] rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-5 flex flex-col gap-4">
          <div>
            <h3 className="text-gray-900">AI Insight</h3>
            <p className="text-xs text-gray-400 mt-0.5">Based on your {view} data</p>
          </div>
          <div className="flex flex-col gap-3">
            {[
              {
                icon: "🏆",
                title: "Top subject",
                body: `Mathematics at ${data.mastery.find(m => m.name === "Maths")?.value}% — keep the momentum!`,
              },
              {
                icon: "⚡",
                title: "Needs attention",
                body: `History at ${data.mastery.find(m => m.name === "History")?.value}% — try 2 extra flashcard sessions.`,
              },
              {
                icon: "📈",
                title: "Score trend",
                body: `Your quiz scores improved by ${data.progress[data.progress.length - 1].score - data.progress[0].score}% over this ${view === "weekly" ? "7-week" : "6-month"} period.`,
              },
            ].map(({ icon, title, body }) => (
              <div key={title} className="flex gap-3 items-start bg-white/70 rounded-xl p-3 border border-[rgba(0,0,0,0.05)]">
                <span className="text-lg shrink-0">{icon}</span>
                <div>
                  <p className="text-xs font-semibold text-gray-700">{title}</p>
                  <p className="text-xs text-gray-500 mt-0.5 leading-snug">{body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
