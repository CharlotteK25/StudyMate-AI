import { useState, useCallback } from "react";
import {
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Flag,
  Sparkles,
  RotateCcw,
  BookOpen,
  Star,
} from "lucide-react";

interface Flashcard {
  id: string;
  subject: string;
  question: string;
  answer: string;
  learned: boolean;
  flagged: boolean;
}

const INITIAL_CARDS: Flashcard[] = [
  {
    id: "1",
    subject: "Biology",
    question: "What is the powerhouse of the cell?",
    answer: "The mitochondria. It generates most of the cell's supply of ATP through a process called cellular respiration, converting oxygen and nutrients into usable energy.",
    learned: false,
    flagged: false,
  },
  {
    id: "2",
    subject: "Chemistry",
    question: "What is the chemical formula for water?",
    answer: "H₂O — two hydrogen atoms covalently bonded to one oxygen atom. Its bent molecular geometry gives it a dipole moment, making it a polar molecule.",
    learned: false,
    flagged: false,
  },
  {
    id: "3",
    subject: "Physics",
    question: "State Newton's Second Law of Motion.",
    answer: "F = ma. The net force acting on an object equals the product of its mass and its acceleration. Force is measured in Newtons (N).",
    learned: true,
    flagged: false,
  },
  {
    id: "4",
    subject: "Mathematics",
    question: "What is the quadratic formula?",
    answer: "x = (−b ± √(b²−4ac)) / 2a. It solves for x in any quadratic equation of the form ax² + bx + c = 0, where a ≠ 0.",
    learned: false,
    flagged: true,
  },
  {
    id: "5",
    subject: "History",
    question: "When did World War II end?",
    answer: "World War II ended in 1945 — V-E Day (Victory in Europe) was May 8, 1945, and V-J Day (Victory over Japan) was September 2, 1945.",
    learned: true,
    flagged: false,
  },
  {
    id: "6",
    subject: "Literature",
    question: "Who wrote 'Romeo and Juliet'?",
    answer: "William Shakespeare, written around 1594–1596. It is a tragedy about two young star-crossed lovers whose deaths ultimately reconcile their feuding families.",
    learned: false,
    flagged: false,
  },
];

const SUBJECT_COLORS: Record<string, { bg: string; text: string; dot: string }> = {
  Biology:     { bg: "#f0fdf4", text: "#16a34a", dot: "#4ade80" },
  Chemistry:   { bg: "#fdf4ff", text: "#9333ea", dot: "#c084fc" },
  Physics:     { bg: "#eff6ff", text: "#2563eb", dot: "#60a5fa" },
  Mathematics: { bg: "#fff7ed", text: "#ea580c", dot: "#fb923c" },
  History:     { bg: "#fef2f2", text: "#dc2626", dot: "#f87171" },
  Literature:  { bg: "#f0fdfa", text: "#0d9488", dot: "#2dd4bf" },
};

function SubjectBadge({ subject }: { subject: string }) {
  const s = SUBJECT_COLORS[subject] ?? { bg: "#f3f4f6", text: "#374151", dot: "#9ca3af" };
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium"
      style={{ backgroundColor: s.bg, color: s.text }}
    >
      <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: s.dot }} />
      {subject}
    </span>
  );
}

export function Flashcards() {
  const [cards, setCards] = useState<Flashcard[]>(INITIAL_CARDS);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [animating, setAnimating] = useState(false);
  const [generating, setGenerating] = useState(false);

  const current = cards[index];

  const navigate = useCallback(
    (dir: -1 | 1) => {
      if (animating) return;
      setAnimating(true);
      setFlipped(false);
      setTimeout(() => {
        setIndex((i) => (i + dir + cards.length) % cards.length);
        setAnimating(false);
      }, 180);
    },
    [animating, cards.length]
  );

  const flip = () => {
    if (animating) return;
    setFlipped((f) => !f);
  };

  const toggleLearned = () => {
    setCards((prev) =>
      prev.map((c) => (c.id === current.id ? { ...c, learned: !c.learned } : c))
    );
  };

  const toggleFlagged = () => {
    setCards((prev) =>
      prev.map((c) => (c.id === current.id ? { ...c, flagged: !c.flagged } : c))
    );
  };

  const generateMore = () => {
    setGenerating(true);
    setTimeout(() => {
      const newCards: Flashcard[] = [
        {
          id: crypto.randomUUID(),
          subject: "Biology",
          question: "What is the process by which plants make food using sunlight?",
          answer: "Photosynthesis. Plants use chlorophyll in their chloroplasts to convert CO₂ and water into glucose and oxygen using light energy: 6CO₂ + 6H₂O + light → C₆H₁₂O₆ + 6O₂.",
          learned: false,
          flagged: false,
        },
        {
          id: crypto.randomUUID(),
          subject: "Chemistry",
          question: "What is Avogadro's number?",
          answer: "6.022 × 10²³ — the number of atoms, molecules, or particles in one mole of a substance. Named after Italian scientist Amedeo Avogadro.",
          learned: false,
          flagged: false,
        },
      ];
      setCards((prev) => [...prev, ...newCards]);
      setGenerating(false);
    }, 1800);
  };

  const learnedCount = cards.filter((c) => c.learned).length;
  const progress = Math.round((learnedCount / cards.length) * 100);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-gray-900">Flashcards</h1>
          <p className="text-sm text-gray-400 mt-0.5">
            {learnedCount} of {cards.length} cards learned
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 bg-white border border-[rgba(0,0,0,0.07)] rounded-xl px-4 py-2 shadow-sm">
            <BookOpen size={13} className="text-[#4ade80]" />
            <span className="text-xs text-gray-500">{progress}% complete</span>
          </div>
          <button
            onClick={generateMore}
            disabled={generating}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-gray-900 text-white hover:bg-gray-700 active:scale-95 transition-all shadow-sm disabled:opacity-60"
          >
            {generating ? (
              <RotateCcw size={13} className="animate-spin" />
            ) : (
              <Sparkles size={13} />
            )}
            {generating ? "Generating…" : "Generate More"}
          </button>
        </div>
      </div>

      {/* Progress bar */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-[#4ade80] rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="text-xs text-gray-400 shrink-0">{index + 1} / {cards.length}</span>
      </div>

      {/* Main layout */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_220px] gap-6 items-start">

        {/* Card + controls */}
        <div className="flex flex-col items-center gap-5">

          {/* Flip card */}
          <div
            className="w-full cursor-pointer"
            style={{ perspective: "1200px" }}
            onClick={flip}
          >
            <div
              className="relative w-full transition-transform duration-500"
              style={{
                transformStyle: "preserve-3d",
                transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
                opacity: animating ? 0 : 1,
                transition: animating
                  ? "opacity 0.18s ease"
                  : "transform 0.5s cubic-bezier(0.4,0.2,0.2,1), opacity 0.18s ease",
              }}
            >
              {/* Front */}
              <div
                className="w-full min-h-64 rounded-[12px] bg-white border border-[rgba(0,0,0,0.08)] shadow-[0_4px_24px_rgba(0,0,0,0.08)] p-8 flex flex-col justify-between"
                style={{ backfaceVisibility: "hidden" }}
              >
                <div className="flex items-center justify-between">
                  <SubjectBadge subject={current.subject} />
                  <span className="text-xs text-gray-300 select-none">Click to flip</span>
                </div>
                <div className="flex flex-col items-center justify-center flex-1 py-8 gap-3">
                  <span className="text-[10px] font-semibold tracking-widest uppercase text-gray-300">
                    Question
                  </span>
                  <p className="text-2xl text-gray-800 text-center leading-snug max-w-lg">
                    {current.question}
                  </p>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-300">Card {index + 1}</span>
                  <div className="flex items-center gap-1.5">
                    {current.learned && (
                      <span className="flex items-center gap-1 text-xs text-[#16a34a] bg-[#f0fdf4] px-2 py-0.5 rounded-lg">
                        <CheckCircle2 size={11} /> Learned
                      </span>
                    )}
                    {current.flagged && (
                      <span className="flex items-center gap-1 text-xs text-[#ea580c] bg-[#fff7ed] px-2 py-0.5 rounded-lg">
                        <Flag size={11} /> Flagged
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Back */}
              <div
                className="absolute inset-0 w-full min-h-64 rounded-[12px] bg-gradient-to-br from-[#f0fdf4] to-[#dcfce7] border border-[#86efac] shadow-[0_4px_24px_rgba(74,222,128,0.15)] p-8 flex flex-col justify-between"
                style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}
              >
                <div className="flex items-center justify-between">
                  <SubjectBadge subject={current.subject} />
                  <span className="text-xs text-[#16a34a]/50 select-none">Click to flip back</span>
                </div>
                <div className="flex flex-col items-center justify-center flex-1 py-8 gap-3">
                  <span className="text-[10px] font-semibold tracking-widest uppercase text-[#16a34a]/40">
                    Answer
                  </span>
                  <p className="text-lg text-gray-700 text-center leading-relaxed max-w-lg">
                    {current.answer}
                  </p>
                </div>
                <div className="flex items-center justify-center">
                  <span className="text-xs text-[#16a34a]/50">Card {index + 1}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action row */}
          <div className="flex items-center gap-2 flex-wrap justify-center">
            <button
              onClick={toggleLearned}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-medium transition-all duration-150 active:scale-95 ${
                current.learned
                  ? "bg-[#4ade80] text-white shadow-sm hover:bg-[#22c55e]"
                  : "bg-[#f0fdf4] text-[#16a34a] border border-[#86efac] hover:bg-[#dcfce7]"
              }`}
            >
              <CheckCircle2 size={13} />
              {current.learned ? "Learned ✓" : "Mark as Learned"}
            </button>
            <button
              onClick={toggleFlagged}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-medium transition-all duration-150 active:scale-95 ${
                current.flagged
                  ? "bg-[#ea580c] text-white shadow-sm hover:bg-[#c2410c]"
                  : "bg-[#fff7ed] text-[#ea580c] border border-[#fdba74] hover:bg-[#ffedd5]"
              }`}
            >
              <Flag size={13} />
              {current.flagged ? "Flagged" : "Flag for Review"}
            </button>
          </div>

          {/* Nav buttons */}
          <div className="flex items-center gap-3 w-full justify-center">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium bg-white border border-[rgba(0,0,0,0.1)] text-gray-600 hover:bg-gray-50 hover:border-gray-300 active:scale-95 transition-all shadow-sm"
            >
              <ChevronLeft size={16} />
              Previous Card
            </button>
            <button
              onClick={flip}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium bg-white border border-[rgba(0,0,0,0.1)] text-gray-600 hover:bg-gray-50 active:scale-95 transition-all shadow-sm"
            >
              <RotateCcw size={15} />
              Flip Card
            </button>
            <button
              onClick={() => navigate(1)}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium bg-gray-900 text-white hover:bg-gray-700 active:scale-95 transition-all shadow-sm"
            >
              Next Card
              <ChevronRight size={16} />
            </button>
          </div>
        </div>

        {/* Card deck sidebar */}
        <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-4 flex flex-col gap-3">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide px-1">All Cards</p>
          <div className="grid grid-cols-2 gap-2">
            {cards.map((c, i) => (
              <button
                key={c.id}
                onClick={() => {
                  if (animating) return;
                  setAnimating(true);
                  setFlipped(false);
                  setTimeout(() => { setIndex(i); setAnimating(false); }, 180);
                }}
                className={`relative flex flex-col items-center justify-center h-16 rounded-xl border text-xs font-medium transition-all duration-150 active:scale-95 ${
                  i === index
                    ? "border-[#4ade80] bg-[#f0fdf4] text-[#16a34a] shadow-sm"
                    : "border-[rgba(0,0,0,0.07)] bg-[#fafafa] text-gray-500 hover:border-gray-300 hover:bg-gray-50"
                }`}
              >
                <span>Card {i + 1}</span>
                {c.learned && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#4ade80]" />
                )}
                {c.flagged && (
                  <span className="absolute top-1.5 left-1.5 w-2 h-2 rounded-full bg-[#fb923c]" />
                )}
              </button>
            ))}
          </div>
          <div className="pt-2 border-t border-[rgba(0,0,0,0.05)] flex items-center justify-between px-1">
            <span className="text-xs text-gray-400">{learnedCount} learned</span>
            <div className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-[#4ade80]" />
              <span className="text-[10px] text-gray-400">done</span>
              <span className="w-2 h-2 rounded-full bg-[#fb923c] ml-2" />
              <span className="text-[10px] text-gray-400">flagged</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
