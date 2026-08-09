import { useState } from "react";
import {
  Sparkles, Clock, RotateCcw, Brain, Target, BookOpen,
  TrendingUp, AlertCircle, ChevronDown, ChevronUp,
  Calendar, Check, ArrowRight, Zap, Star, Flame,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

type Tag = "Weak Subject" | "High Priority" | "Recommended" | "On Track" | "New Technique";

interface ScheduleDay {
  day: string;
  subject: string;
  duration: string;
  type: string;
}

interface Recommendation {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  icon: React.ElementType;
  iconColor: string;
  tags: Tag[];
  subjects: string[];
  benefit: string;
  difficulty: "Easy" | "Moderate" | "Advanced";
  schedule: ScheduleDay[];
  tip: string;
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const TAG_STYLES: Record<Tag, { bg: string; text: string; border: string }> = {
  "Weak Subject":   { bg: "#fef2f2", text: "#dc2626", border: "#fecaca" },
  "High Priority":  { bg: "#fff7ed", text: "#ea580c", border: "#fed7aa" },
  "Recommended":    { bg: "#f0fdf4", text: "#16a34a", border: "#bbf7d0" },
  "On Track":       { bg: "#eff6ff", text: "#2563eb", border: "#bfdbfe" },
  "New Technique":  { bg: "#fdf4ff", text: "#9333ea", border: "#e9d5ff" },
};

const DIFFICULTY_STYLES = {
  Easy:     { bg: "#f0fdf4", text: "#16a34a" },
  Moderate: { bg: "#fffbeb", text: "#d97706" },
  Advanced: { bg: "#fef2f2", text: "#dc2626" },
};

const CARDS: Recommendation[] = [
  {
    id: "r1",
    title: "Pomodoro Technique",
    subtitle: "Boost focus with structured work intervals",
    description: "Break your study sessions into 25-minute focused sprints followed by a 5-minute break. After four rounds, take a longer 20-minute rest. This technique is especially effective for Chemistry and History where sustained concentration is critical.",
    icon: Clock,
    iconColor: "#2563eb",
    tags: ["High Priority", "New Technique"],
    subjects: ["Chemistry", "History"],
    benefit: "Reduces mental fatigue by up to 40%",
    difficulty: "Easy",
    tip: "Set a physical timer — it creates a stronger commitment than a phone app.",
    schedule: [
      { day: "Mon", subject: "Chemistry", duration: "4 × 25 min", type: "Formula revision" },
      { day: "Tue", subject: "History", duration: "4 × 25 min", type: "Essay planning" },
      { day: "Wed", subject: "Chemistry", duration: "3 × 25 min", type: "Practice problems" },
      { day: "Thu", subject: "History", duration: "4 × 25 min", type: "Timeline review" },
      { day: "Fri", subject: "Both", duration: "2 × 25 min each", type: "Mixed revision" },
    ],
  },
  {
    id: "r2",
    title: "Spaced Repetition",
    subtitle: "Review material at optimally increasing intervals",
    description: "Instead of cramming, revisit concepts at growing intervals — 1 day, 3 days, 7 days, 14 days. Your History and Chemistry scores show clear retention gaps that spaced repetition directly targets, reinforcing memory just before it fades.",
    icon: RotateCcw,
    iconColor: "#dc2626",
    tags: ["Weak Subject", "Recommended"],
    subjects: ["History", "Chemistry"],
    benefit: "Improves long-term retention by 80%",
    difficulty: "Moderate",
    tip: "Use your Flashcards page — it's already set up for spaced review cycles.",
    schedule: [
      { day: "Day 1", subject: "History", duration: "20 min", type: "Initial learning" },
      { day: "Day 2", subject: "History", duration: "10 min", type: "First recall" },
      { day: "Day 4", subject: "History", duration: "10 min", type: "Second recall" },
      { day: "Day 8", subject: "Chemistry", duration: "15 min", type: "Deep recall" },
      { day: "Day 15", subject: "Both", duration: "20 min", type: "Final consolidation" },
    ],
  },
  {
    id: "r3",
    title: "Active Recall Practice",
    subtitle: "Test yourself instead of re-reading notes",
    description: "Close your notes and write down everything you remember on a blank page. This technique forces your brain to retrieve information — the single most powerful learning activity. Ideal for Mathematics where procedure recall matters most.",
    icon: Brain,
    iconColor: "#9333ea",
    tags: ["Recommended", "High Priority"],
    subjects: ["Mathematics", "Physics"],
    benefit: "2× more effective than re-reading",
    difficulty: "Moderate",
    tip: "After each lecture, write a 5-minute brain dump without looking at your notes.",
    schedule: [
      { day: "Mon", subject: "Mathematics", duration: "30 min", type: "Blank-page recall" },
      { day: "Wed", subject: "Physics", duration: "30 min", type: "Formula recall" },
      { day: "Fri", subject: "Mathematics", duration: "20 min", type: "Problem-solving sprint" },
      { day: "Sun", subject: "Physics", duration: "25 min", type: "Concept mapping" },
    ],
  },
  {
    id: "r4",
    title: "Interleaved Practice",
    subtitle: "Mix subjects within a single study session",
    description: "Instead of studying one subject for hours, alternate between Biology, Physics, and Maths in the same session. Interleaving feels harder but dramatically improves your ability to distinguish and apply different concepts under exam pressure.",
    icon: Zap,
    iconColor: "#ea580c",
    tags: ["New Technique", "On Track"],
    subjects: ["Biology", "Physics", "Mathematics"],
    benefit: "43% better exam performance",
    difficulty: "Advanced",
    tip: "Start with 20-min blocks per subject, then reduce to 10 min as you improve.",
    schedule: [
      { day: "Mon", subject: "Bio → Phys → Maths", duration: "20 min each", type: "Interleaved block" },
      { day: "Wed", subject: "Bio → Phys → Maths", duration: "20 min each", type: "Problem rotation" },
      { day: "Sat", subject: "All three", duration: "15 min each", type: "Mixed exam drill" },
    ],
  },
  {
    id: "r5",
    title: "Elaborative Interrogation",
    subtitle: "Ask 'why' and 'how' to build deep understanding",
    description: "For every fact you study, ask yourself 'Why is this true?' and 'How does this connect to what I already know?' This deepens comprehension beyond surface memorisation — particularly powerful for Biology where systems interconnect.",
    icon: Target,
    iconColor: "#0891b2",
    tags: ["Recommended", "On Track"],
    subjects: ["Biology", "Chemistry"],
    benefit: "Builds conceptual frameworks, not just facts",
    difficulty: "Easy",
    tip: "Keep a 'Why?' notebook. Write one deep question per topic before each session.",
    schedule: [
      { day: "Daily", subject: "Biology", duration: "10 min pre-session", type: "Question generation" },
      { day: "Daily", subject: "Chemistry", duration: "10 min pre-session", type: "Mechanism tracing" },
      { day: "Weekly", subject: "Both", duration: "30 min", type: "Connection mapping" },
    ],
  },
  {
    id: "r6",
    title: "The Feynman Technique",
    subtitle: "Teach it simply to truly understand it",
    description: "Pick a concept, explain it as if teaching a 12-year-old, identify gaps in your explanation, then go back to your notes and refine. Repeat until your explanation is clear and gapless. Perfect for complex Physics topics.",
    icon: Star,
    iconColor: "#d97706",
    tags: ["New Technique", "Weak Subject"],
    subjects: ["Physics", "Mathematics"],
    benefit: "Exposes hidden knowledge gaps instantly",
    difficulty: "Advanced",
    tip: "Record a 2-minute voice memo explaining a concept — play it back to spot confusion.",
    schedule: [
      { day: "Tue", subject: "Physics", duration: "25 min", type: "Teach-back session" },
      { day: "Thu", subject: "Mathematics", duration: "25 min", type: "Worked-example narration" },
      { day: "Sun", subject: "Physics", duration: "20 min", type: "Gap-fill revision" },
    ],
  },
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function TagBadge({ tag }: { tag: Tag }) {
  const s = TAG_STYLES[tag];
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-semibold tracking-wide border"
      style={{ backgroundColor: s.bg, color: s.text, borderColor: s.border }}
    >
      {tag === "Weak Subject" && <AlertCircle size={9} />}
      {tag === "High Priority" && <Flame size={9} />}
      {tag === "Recommended" && <Sparkles size={9} />}
      {tag === "On Track" && <Check size={9} />}
      {tag === "New Technique" && <Zap size={9} />}
      {tag}
    </span>
  );
}

function SubjectChip({ subject }: { subject: string }) {
  return (
    <span className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-[#EAF3FF] text-[#1d4ed8] border border-[#bfdbfe]">
      {subject}
    </span>
  );
}

function RevisionSchedule({ schedule }: { schedule: ScheduleDay[] }) {
  return (
    <div className="mt-1 rounded-xl border border-[#bfdbfe] bg-[#EAF3FF] overflow-hidden">
      <div className="px-4 py-2.5 border-b border-[#bfdbfe] flex items-center gap-2">
        <Calendar size={13} className="text-[#2563eb]" />
        <span className="text-xs font-semibold text-[#1d4ed8]">Revision Schedule</span>
      </div>
      <div className="divide-y divide-[#bfdbfe]/60">
        {schedule.map((row, i) => (
          <div key={i} className="flex items-center gap-3 px-4 py-2.5">
            <span className="w-14 text-[10px] font-semibold text-[#2563eb] shrink-0">{row.day}</span>
            <span className="flex-1 text-xs text-[#1e3a8a]">{row.subject}</span>
            <span className="text-[10px] text-[#3b82f6] bg-white px-2 py-0.5 rounded-md border border-[#bfdbfe] shrink-0">{row.duration}</span>
            <span className="hidden sm:block text-[10px] text-[#6b7280] shrink-0 w-36 text-right">{row.type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function RecommendationCard({ card }: { card: Recommendation }) {
  const [expanded, setExpanded] = useState(false);
  const Icon = card.icon;
  const diff = DIFFICULTY_STYLES[card.difficulty];

  return (
    <div
      className={`flex flex-col gap-4 bg-white rounded-2xl border shadow-sm transition-all duration-200 overflow-hidden ${
        expanded ? "border-[#93c5fd] shadow-md shadow-[#bfdbfe40]" : "border-[rgba(0,0,0,0.07)] hover:border-[#93c5fd] hover:shadow-md"
      }`}
    >
      {/* Card top accent strip */}
      <div className="h-1 w-full rounded-t-2xl" style={{ backgroundColor: card.iconColor + "60" }} />

      <div className="px-5 pb-1 flex flex-col gap-3 -mt-1">
        {/* Header row */}
        <div className="flex items-start gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 mt-0.5"
            style={{ backgroundColor: card.iconColor + "15" }}
          >
            <Icon size={20} style={{ color: card.iconColor }} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-gray-900 text-base">{card.title}</h3>
              <span
                className="text-[10px] font-semibold px-2 py-0.5 rounded-lg"
                style={{ backgroundColor: diff.bg, color: diff.text }}
              >
                {card.difficulty}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5">{card.subtitle}</p>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5">
          {card.tags.map((t) => <TagBadge key={t} tag={t} />)}
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 leading-relaxed">{card.description}</p>

        {/* Subjects + benefit */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex flex-wrap gap-1.5">
            {card.subjects.map((s) => <SubjectChip key={s} subject={s} />)}
          </div>
          <div className="flex items-center gap-1.5 text-[10px] text-[#16a34a] bg-[#f0fdf4] px-2.5 py-1 rounded-lg border border-[#bbf7d0]">
            <TrendingUp size={10} />
            <span className="font-medium">{card.benefit}</span>
          </div>
        </div>

        {/* Tip */}
        <div className="flex items-start gap-2.5 bg-[#fffbeb] border border-[#fde68a] rounded-xl px-3 py-2.5">
          <span className="text-base shrink-0 mt-0.5">💡</span>
          <p className="text-xs text-[#92400e] leading-snug"><span className="font-semibold">Pro tip: </span>{card.tip}</p>
        </div>

        {/* Expand toggle */}
        <button
          onClick={() => setExpanded((e) => !e)}
          className="flex items-center justify-between w-full px-4 py-2.5 rounded-xl bg-[#EAF3FF] border border-[#bfdbfe] hover:bg-[#dbeafe] transition-colors group"
        >
          <div className="flex items-center gap-2">
            <Calendar size={13} className="text-[#2563eb]" />
            <span className="text-xs font-semibold text-[#1d4ed8]">View Revision Schedule</span>
          </div>
          <div className="flex items-center gap-1 text-[#3b82f6]">
            <span className="text-[10px]">{expanded ? "Hide" : "Show"}</span>
            {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </div>
        </button>

        {/* Expandable schedule */}
        <div
          className={`overflow-hidden transition-all duration-300 ${expanded ? "max-h-96 opacity-100" : "max-h-0 opacity-0"}`}
        >
          <RevisionSchedule schedule={card.schedule} />
        </div>

        {/* CTA */}
        <div className="flex items-center gap-2 pb-1">
          <button className="flex items-center gap-1.5 text-xs font-medium text-white bg-gray-900 hover:bg-gray-700 px-4 py-2 rounded-xl active:scale-95 transition-all shadow-sm">
            <Sparkles size={12} /> Apply Technique
          </button>
          <button className="flex items-center gap-1.5 text-xs font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-100 px-4 py-2 rounded-xl transition-all">
            Learn more <ArrowRight size={12} />
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Filter bar ───────────────────────────────────────────────────────────────

const FILTERS = ["All", "Weak Subject", "High Priority", "Recommended", "New Technique", "On Track"] as const;
type Filter = typeof FILTERS[number];

// ─── Main ─────────────────────────────────────────────────────────────────────

export function Recommendations() {
  const [activeFilter, setActiveFilter] = useState<Filter>("All");
  const [search, setSearch] = useState("");

  const visible = CARDS.filter((c) => {
    const matchFilter = activeFilter === "All" || c.tags.includes(activeFilter as Tag);
    const matchSearch =
      !search ||
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.subjects.some((s) => s.toLowerCase().includes(search.toLowerCase()));
    return matchFilter && matchSearch;
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-gray-900">Study Recommendations</h1>
          <p className="text-sm text-gray-400 mt-0.5">
            Personalised AI techniques based on your performance data
          </p>
        </div>
        <div className="flex items-center gap-2 bg-[#EAF3FF] border border-[#bfdbfe] rounded-xl px-3 py-2">
          <Sparkles size={13} className="text-[#2563eb]" />
          <span className="text-xs font-medium text-[#1d4ed8]">{CARDS.length} insights generated</span>
        </div>
      </div>

      {/* Search + filter row */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-xs">
          <BookOpen size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title or subject…"
            className="w-full bg-white border border-[rgba(0,0,0,0.08)] rounded-xl pl-8 pr-3 py-2 text-xs text-gray-700 placeholder-gray-400 focus:outline-none focus:border-[#93c5fd] focus:ring-2 focus:ring-[#bfdbfe] transition-all"
          />
        </div>
        <div className="flex flex-wrap gap-1.5">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-all duration-150 active:scale-95 ${
                activeFilter === f
                  ? "bg-gray-900 text-white border-gray-900 shadow-sm"
                  : "bg-white text-gray-500 border-[rgba(0,0,0,0.08)] hover:border-gray-300 hover:text-gray-700"
              }`}
            >
              {f === "All" ? `All (${CARDS.length})` : f}
            </button>
          ))}
        </div>
      </div>

      {/* Weak-subject callout */}
      {(activeFilter === "All" || activeFilter === "Weak Subject") && (
        <div className="flex items-start gap-3 bg-[#fef2f2] border border-[#fecaca] rounded-2xl px-4 py-3.5">
          <AlertCircle size={16} className="text-[#dc2626] shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-[#dc2626]">Weak subjects detected</p>
            <p className="text-xs text-[#dc2626]/70 mt-0.5">
              Based on your quiz history, <strong>History (58%)</strong> and <strong>Chemistry (67%)</strong> need the most attention. The highlighted cards below are specifically tailored for you.
            </p>
          </div>
        </div>
      )}

      {/* Card grid */}
      {visible.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {visible.map((card) => (
            <RecommendationCard key={card.id} card={card} />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 gap-3 text-gray-400">
          <BookOpen size={32} className="text-gray-200" />
          <p className="text-sm">No recommendations match your filter.</p>
          <button
            onClick={() => { setActiveFilter("All"); setSearch(""); }}
            className="text-xs text-[#2563eb] hover:underline"
          >
            Clear filters
          </button>
        </div>
      )}
    </div>
  );
}
