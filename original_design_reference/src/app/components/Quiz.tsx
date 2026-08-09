import { useState, useCallback } from "react";
import {
  ChevronDown,
  Sparkles,
  CheckCircle2,
  XCircle,
  RotateCcw,
  Trophy,
  Target,
  Clock,
  ArrowRight,
  Loader2,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

interface Option { id: string; label: string; text: string }
interface Question {
  id: string;
  number: number;
  text: string;
  options: Option[];
  correctId: string;
  explanation: string;
}

// ─── Question bank ────────────────────────────────────────────────────────────

const QUESTION_BANK: Record<string, Question[]> = {
  Biology: [
    {
      id: "b1", number: 1,
      text: "Which organelle is responsible for producing ATP through cellular respiration?",
      options: [
        { id: "a", label: "A", text: "Nucleus" },
        { id: "b", label: "B", text: "Mitochondria" },
        { id: "c", label: "C", text: "Ribosome" },
        { id: "d", label: "D", text: "Golgi apparatus" },
      ],
      correctId: "b",
      explanation: "Mitochondria are the site of cellular respiration, converting glucose and oxygen into ATP — the cell's primary energy currency.",
    },
    {
      id: "b2", number: 2,
      text: "What is the process by which cells divide to produce two identical daughter cells?",
      options: [
        { id: "a", label: "A", text: "Meiosis" },
        { id: "b", label: "B", text: "Apoptosis" },
        { id: "c", label: "C", text: "Mitosis" },
        { id: "d", label: "D", text: "Cytokinesis only" },
      ],
      correctId: "c",
      explanation: "Mitosis is the process producing two genetically identical diploid daughter cells, used for growth and repair.",
    },
    {
      id: "b3", number: 3,
      text: "Which molecule carries genetic information from the nucleus to the ribosome?",
      options: [
        { id: "a", label: "A", text: "tRNA" },
        { id: "b", label: "B", text: "rRNA" },
        { id: "c", label: "C", text: "DNA" },
        { id: "d", label: "D", text: "mRNA" },
      ],
      correctId: "d",
      explanation: "Messenger RNA (mRNA) carries the genetic code transcribed from DNA out of the nucleus to the ribosome for translation.",
    },
    {
      id: "b4", number: 4,
      text: "What is the primary function of the cell membrane?",
      options: [
        { id: "a", label: "A", text: "Energy production" },
        { id: "b", label: "B", text: "Protein synthesis" },
        { id: "c", label: "C", text: "Selective permeability and cell boundary" },
        { id: "d", label: "D", text: "DNA replication" },
      ],
      correctId: "c",
      explanation: "The cell membrane acts as a selectively permeable barrier, controlling what enters and exits the cell.",
    },
  ],
  Chemistry: [
    {
      id: "c1", number: 1,
      text: "What is the atomic number of Carbon?",
      options: [
        { id: "a", label: "A", text: "6" },
        { id: "b", label: "B", text: "12" },
        { id: "c", label: "C", text: "8" },
        { id: "d", label: "D", text: "14" },
      ],
      correctId: "a",
      explanation: "Carbon has atomic number 6, meaning it has 6 protons. Its atomic mass is approximately 12 amu.",
    },
    {
      id: "c2", number: 2,
      text: "Which type of bond involves the sharing of electron pairs between atoms?",
      options: [
        { id: "a", label: "A", text: "Ionic bond" },
        { id: "b", label: "B", text: "Hydrogen bond" },
        { id: "c", label: "C", text: "Covalent bond" },
        { id: "d", label: "D", text: "Metallic bond" },
      ],
      correctId: "c",
      explanation: "Covalent bonds form when two atoms share one or more pairs of electrons, typically between non-metals.",
    },
    {
      id: "c3", number: 3,
      text: "What is the pH of a neutral solution at 25°C?",
      options: [
        { id: "a", label: "A", text: "0" },
        { id: "b", label: "B", text: "7" },
        { id: "c", label: "C", text: "14" },
        { id: "d", label: "D", text: "5" },
      ],
      correctId: "b",
      explanation: "A neutral solution has a pH of 7 at 25°C, where the concentration of H⁺ and OH⁻ ions are equal.",
    },
    {
      id: "c4", number: 4,
      text: "What does Avogadro's number represent?",
      options: [
        { id: "a", label: "A", text: "The speed of light" },
        { id: "b", label: "B", text: "The number of particles in one mole" },
        { id: "c", label: "C", text: "The universal gas constant" },
        { id: "d", label: "D", text: "The charge of an electron" },
      ],
      correctId: "b",
      explanation: "Avogadro's number (6.022 × 10²³) is the number of atoms, molecules, or particles in one mole of a substance.",
    },
  ],
  Physics: [
    {
      id: "p1", number: 1,
      text: "What is the SI unit of force?",
      options: [
        { id: "a", label: "A", text: "Watt" },
        { id: "b", label: "B", text: "Joule" },
        { id: "c", label: "C", text: "Newton" },
        { id: "d", label: "D", text: "Pascal" },
      ],
      correctId: "c",
      explanation: "The Newton (N) is the SI unit of force. One Newton equals 1 kg·m/s², from Newton's second law F = ma.",
    },
    {
      id: "p2", number: 2,
      text: "What is the approximate speed of light in a vacuum?",
      options: [
        { id: "a", label: "A", text: "3 × 10⁶ m/s" },
        { id: "b", label: "B", text: "3 × 10⁸ m/s" },
        { id: "c", label: "C", text: "3 × 10¹⁰ m/s" },
        { id: "d", label: "D", text: "3 × 10⁴ m/s" },
      ],
      correctId: "b",
      explanation: "Light travels at approximately 3 × 10⁸ m/s (299,792,458 m/s) in a vacuum — denoted as 'c'.",
    },
    {
      id: "p3", number: 3,
      text: "Which law states that energy cannot be created or destroyed?",
      options: [
        { id: "a", label: "A", text: "Newton's First Law" },
        { id: "b", label: "B", text: "Ohm's Law" },
        { id: "c", label: "C", text: "First Law of Thermodynamics" },
        { id: "d", label: "D", text: "Boyle's Law" },
      ],
      correctId: "c",
      explanation: "The First Law of Thermodynamics states that energy is conserved — it can only be converted from one form to another.",
    },
    {
      id: "p4", number: 4,
      text: "What type of wave does not require a medium to travel?",
      options: [
        { id: "a", label: "A", text: "Sound wave" },
        { id: "b", label: "B", text: "Seismic wave" },
        { id: "c", label: "C", text: "Water wave" },
        { id: "d", label: "D", text: "Electromagnetic wave" },
      ],
      correctId: "d",
      explanation: "Electromagnetic waves (light, radio, X-rays, etc.) can travel through a vacuum and need no medium.",
    },
  ],
  Mathematics: [
    {
      id: "m1", number: 1,
      text: "What is the derivative of sin(x)?",
      options: [
        { id: "a", label: "A", text: "−sin(x)" },
        { id: "b", label: "B", text: "cos(x)" },
        { id: "c", label: "C", text: "tan(x)" },
        { id: "d", label: "D", text: "−cos(x)" },
      ],
      correctId: "b",
      explanation: "The derivative of sin(x) with respect to x is cos(x). This is a fundamental result in differential calculus.",
    },
    {
      id: "m2", number: 2,
      text: "What is the value of π to four decimal places?",
      options: [
        { id: "a", label: "A", text: "3.1416" },
        { id: "b", label: "B", text: "3.1214" },
        { id: "c", label: "C", text: "3.1618" },
        { id: "d", label: "D", text: "3.1200" },
      ],
      correctId: "a",
      explanation: "π ≈ 3.14159265…, which rounds to 3.1416 at four decimal places.",
    },
    {
      id: "m3", number: 3,
      text: "If f(x) = x², what is f(−3)?",
      options: [
        { id: "a", label: "A", text: "−9" },
        { id: "b", label: "B", text: "6" },
        { id: "c", label: "C", text: "9" },
        { id: "d", label: "D", text: "−6" },
      ],
      correctId: "c",
      explanation: "f(−3) = (−3)² = 9. Squaring any negative number yields a positive result.",
    },
    {
      id: "m4", number: 4,
      text: "What is the sum of angles in a triangle?",
      options: [
        { id: "a", label: "A", text: "90°" },
        { id: "b", label: "B", text: "360°" },
        { id: "c", label: "C", text: "270°" },
        { id: "d", label: "D", text: "180°" },
      ],
      correctId: "d",
      explanation: "The interior angles of any triangle always sum to 180°. This is one of the foundational theorems of Euclidean geometry.",
    },
  ],
  History: [
    {
      id: "h1", number: 1,
      text: "In which year did the French Revolution begin?",
      options: [
        { id: "a", label: "A", text: "1776" },
        { id: "b", label: "B", text: "1789" },
        { id: "c", label: "C", text: "1804" },
        { id: "d", label: "D", text: "1815" },
      ],
      correctId: "b",
      explanation: "The French Revolution began in 1789 with the storming of the Bastille on July 14th — now celebrated as Bastille Day.",
    },
    {
      id: "h2", number: 2,
      text: "Who was the first President of the United States?",
      options: [
        { id: "a", label: "A", text: "Thomas Jefferson" },
        { id: "b", label: "B", text: "Benjamin Franklin" },
        { id: "c", label: "C", text: "John Adams" },
        { id: "d", label: "D", text: "George Washington" },
      ],
      correctId: "d",
      explanation: "George Washington served as the first U.S. President from 1789 to 1797, setting many precedents for the office.",
    },
    {
      id: "h3", number: 3,
      text: "Which empire was ruled by Julius Caesar?",
      options: [
        { id: "a", label: "A", text: "Greek Empire" },
        { id: "b", label: "B", text: "Ottoman Empire" },
        { id: "c", label: "C", text: "Roman Republic / Empire" },
        { id: "d", label: "D", text: "Byzantine Empire" },
      ],
      correctId: "c",
      explanation: "Julius Caesar was a Roman statesman and general who played a critical role in the transformation of the Roman Republic into the Roman Empire.",
    },
    {
      id: "h4", number: 4,
      text: "What was the name of the first artificial satellite launched into space?",
      options: [
        { id: "a", label: "A", text: "Apollo 11" },
        { id: "b", label: "B", text: "Voyager 1" },
        { id: "c", label: "C", text: "Sputnik 1" },
        { id: "d", label: "D", text: "Explorer 1" },
      ],
      correctId: "c",
      explanation: "Sputnik 1 was launched by the Soviet Union on October 4, 1957, becoming the first artificial Earth satellite.",
    },
  ],
};

const SUBJECTS = Object.keys(QUESTION_BANK);
const TOPICS = ["Multiple Choice", "True / False", "Short Answer", "Mixed"];

// ─── Sub-components ───────────────────────────────────────────────────────────

function SelectBox({
  label, value, options, onChange,
}: { label: string; value: string; options: string[]; onChange: (v: string) => void }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full appearance-none bg-white border border-[rgba(0,0,0,0.1)] rounded-xl px-4 py-2.5 text-sm text-gray-700 pr-9 cursor-pointer hover:border-[#86efac] focus:outline-none focus:border-[#4ade80] focus:ring-2 focus:ring-[#4ade80]/20 transition-all"
        >
          {options.map((o) => (
            <option key={o} value={o}>{o}</option>
          ))}
        </select>
        <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
      </div>
    </div>
  );
}

function OptionCard({
  option, selected, revealed, isCorrect, onSelect,
}: {
  option: Option;
  selected: boolean;
  revealed: boolean;
  isCorrect: boolean;
  onSelect: () => void;
}) {
  let bg = "bg-white border-[rgba(0,0,0,0.1)] text-gray-700 hover:border-[#86efac] hover:bg-[#f0fdf4]/60 hover:shadow-sm";
  let labelBg = "bg-gray-100 text-gray-500";
  let indicator = null;

  if (revealed) {
    if (isCorrect) {
      bg = "bg-[#f0fdf4] border-[#4ade80] text-[#15803d] shadow-sm shadow-[#4ade8020]";
      labelBg = "bg-[#4ade80] text-white";
      indicator = <CheckCircle2 size={16} className="text-[#16a34a] shrink-0" />;
    } else if (selected && !isCorrect) {
      bg = "bg-[#fef2f2] border-[#fca5a5] text-[#dc2626]";
      labelBg = "bg-[#fca5a5] text-white";
      indicator = <XCircle size={16} className="text-[#dc2626] shrink-0" />;
    }
  } else if (selected) {
    bg = "bg-[#f0fdf4] border-[#4ade80] text-[#15803d] shadow-sm";
    labelBg = "bg-[#4ade80] text-white";
  }

  return (
    <button
      onClick={onSelect}
      disabled={revealed}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border-2 text-sm text-left transition-all duration-150 active:scale-[0.99] ${bg}`}
    >
      <span className={`w-6 h-6 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 transition-colors ${labelBg}`}>
        {option.label}
      </span>
      <span className="flex-1 leading-snug">{option.text}</span>
      {indicator}
    </button>
  );
}

// ─── Score summary ────────────────────────────────────────────────────────────

function ScoreSummary({
  questions,
  answers,
  subject,
  topic,
  elapsed,
  onRetake,
  onNewQuiz,
}: {
  questions: Question[];
  answers: Record<string, string>;
  subject: string;
  topic: string;
  elapsed: number;
  onRetake: () => void;
  onNewQuiz: () => void;
}) {
  const correct = questions.filter((q) => answers[q.id] === q.correctId).length;
  const total = questions.length;
  const pct = Math.round((correct / total) * 100);
  const mins = Math.floor(elapsed / 60);
  const secs = elapsed % 60;

  const grade =
    pct >= 90 ? { label: "Excellent", color: "#16a34a", bg: "#f0fdf4" } :
    pct >= 75 ? { label: "Good", color: "#2563eb", bg: "#eff6ff" } :
    pct >= 60 ? { label: "Fair", color: "#d97706", bg: "#fffbeb" } :
                { label: "Needs Work", color: "#dc2626", bg: "#fef2f2" };

  return (
    <div className="flex flex-col gap-6 max-w-2xl mx-auto w-full">
      {/* Score card */}
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm overflow-hidden">
        <div className="bg-gradient-to-br from-[#f0fdf4] to-[#dcfce7] px-8 py-8 flex flex-col items-center gap-3 border-b border-[rgba(0,0,0,0.06)]">
          <div className="w-16 h-16 rounded-2xl bg-white flex items-center justify-center shadow-sm">
            <Trophy size={28} className="text-[#4ade80]" />
          </div>
          <h2 className="text-gray-900">Quiz Complete!</h2>
          <div className="flex items-baseline gap-1.5">
            <span className="text-6xl font-bold text-gray-900">{pct}</span>
            <span className="text-2xl text-gray-400 font-medium">%</span>
          </div>
          <span
            className="px-3 py-1 rounded-lg text-sm font-semibold"
            style={{ backgroundColor: grade.bg, color: grade.color }}
          >
            {grade.label}
          </span>
        </div>

        {/* Metrics row */}
        <div className="grid grid-cols-3 divide-x divide-[rgba(0,0,0,0.06)]">
          {[
            { icon: CheckCircle2, color: "#16a34a", value: `${correct}/${total}`, label: "Correct" },
            { icon: Target, color: "#2563eb", value: `${pct}%`, label: "Accuracy" },
            { icon: Clock, color: "#9333ea", value: `${mins}m ${secs}s`, label: "Time Taken" },
          ].map(({ icon: Icon, color, value, label }) => (
            <div key={label} className="flex flex-col items-center gap-1 py-4">
              <Icon size={16} style={{ color }} />
              <span className="text-base font-semibold text-gray-800">{value}</span>
              <span className="text-xs text-gray-400">{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Progress bar */}
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-5 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">Score Breakdown</span>
          <span className="text-xs text-gray-400">{subject} · {topic}</span>
        </div>
        <div className="flex gap-1 h-3 rounded-full overflow-hidden">
          {questions.map((q) => {
            const ok = answers[q.id] === q.correctId;
            return (
              <div
                key={q.id}
                className="flex-1 rounded-sm transition-colors"
                style={{ backgroundColor: ok ? "#4ade80" : "#fca5a5" }}
                title={`Q${q.number}: ${ok ? "Correct" : "Incorrect"}`}
              />
            );
          })}
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-[#4ade80]" /> Correct</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-sm bg-[#fca5a5]" /> Incorrect</span>
        </div>
      </div>

      {/* Answer key */}
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-[rgba(0,0,0,0.06)]">
          <h3 className="text-gray-900">Answer Key</h3>
          <p className="text-xs text-gray-400 mt-0.5">Review each question with explanations</p>
        </div>
        <div className="divide-y divide-[rgba(0,0,0,0.04)]">
          {questions.map((q) => {
            const chosen = answers[q.id];
            const ok = chosen === q.correctId;
            const correctOption = q.options.find((o) => o.id === q.correctId)!;
            const chosenOption = q.options.find((o) => o.id === chosen);
            return (
              <div key={q.id} className="px-5 py-4 flex flex-col gap-2">
                <div className="flex items-start gap-3">
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${ok ? "bg-[#f0fdf4]" : "bg-[#fef2f2]"}`}>
                    {ok
                      ? <CheckCircle2 size={14} className="text-[#16a34a]" />
                      : <XCircle size={14} className="text-[#dc2626]" />
                    }
                  </div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-700 leading-snug">
                      <span className="font-medium text-gray-900 mr-1">Q{q.number}.</span>
                      {q.text}
                    </p>
                    <div className="mt-2 flex flex-col gap-1 text-xs">
                      {!ok && chosenOption && (
                        <span className="text-[#dc2626]">
                          Your answer: <strong>{chosenOption.label}. {chosenOption.text}</strong>
                        </span>
                      )}
                      <span className="text-[#16a34a]">
                        Correct answer: <strong>{correctOption.label}. {correctOption.text}</strong>
                      </span>
                      <p className="text-gray-400 mt-1 leading-relaxed">{q.explanation}</p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3 pb-4">
        <button
          onClick={onRetake}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium bg-white border border-[rgba(0,0,0,0.1)] text-gray-600 hover:bg-gray-50 hover:border-gray-300 active:scale-95 transition-all shadow-sm"
        >
          <RotateCcw size={15} />
          Retake Quiz
        </button>
        <button
          onClick={onNewQuiz}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium bg-gray-900 text-white hover:bg-gray-700 active:scale-95 transition-all shadow-sm"
        >
          New Quiz
          <ArrowRight size={15} />
        </button>
      </div>
    </div>
  );
}

// ─── Main Quiz component ──────────────────────────────────────────────────────

type Phase = "setup" | "quiz" | "results";

export function Quiz() {
  const [phase, setPhase] = useState<Phase>("setup");
  const [subject, setSubject] = useState("Biology");
  const [topic, setTopic] = useState("Multiple Choice");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [revealed, setRevealed] = useState<Set<string>>(new Set());
  const [generating, setGenerating] = useState(false);
  const [startTime, setStartTime] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  const generate = useCallback(() => {
    setGenerating(true);
    setTimeout(() => {
      const qs = QUESTION_BANK[subject] ?? QUESTION_BANK["Biology"];
      setQuestions(qs);
      setAnswers({});
      setRevealed(new Set());
      setStartTime(Date.now());
      setGenerating(false);
      setPhase("quiz");
    }, 1400);
  }, [subject]);

  const select = (questionId: string, optionId: string) => {
    if (revealed.has(questionId)) return;
    setAnswers((prev) => ({ ...prev, [questionId]: optionId }));
    setRevealed((prev) => new Set(prev).add(questionId));
  };

  const answered = Object.keys(answers).length;
  const allAnswered = answered === questions.length;

  const submit = () => {
    setElapsed(Math.round((Date.now() - startTime) / 1000));
    setPhase("results");
  };

  const retake = () => {
    setAnswers({});
    setRevealed(new Set());
    setStartTime(Date.now());
    setPhase("quiz");
  };

  const newQuiz = () => {
    setPhase("setup");
    setAnswers({});
    setRevealed(new Set());
  };

  // ── Setup screen ─────────────────────────────────────────────────────────────
  if (phase === "setup") {
    return (
      <div className="flex flex-col gap-6 max-w-xl mx-auto w-full pt-4">
        <div className="text-center">
          <h1 className="text-gray-900">Study Quiz</h1>
          <p className="text-sm text-gray-400 mt-1">Select a subject and topic to generate AI-powered questions</p>
        </div>

        <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm p-6 flex flex-col gap-5">
          <div className="grid grid-cols-2 gap-4">
            <SelectBox label="Subject" value={subject} options={SUBJECTS} onChange={setSubject} />
            <SelectBox label="Topic" value={topic} options={TOPICS} onChange={setTopic} />
          </div>

          {/* Subject preview chips */}
          <div className="flex flex-col gap-2">
            <span className="text-xs text-gray-400">Quick select subject</span>
            <div className="flex flex-wrap gap-2">
              {SUBJECTS.map((s) => (
                <button
                  key={s}
                  onClick={() => setSubject(s)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-all ${
                    subject === s
                      ? "bg-gray-900 text-white border-gray-900"
                      : "bg-white text-gray-500 border-[rgba(0,0,0,0.1)] hover:border-gray-300 hover:text-gray-700"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="pt-2 border-t border-[rgba(0,0,0,0.05)] flex items-center justify-between text-xs text-gray-400">
            <span>4 questions · {topic}</span>
            <span>{subject}</span>
          </div>

          <button
            onClick={generate}
            disabled={generating}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-medium bg-gray-900 text-white hover:bg-gray-700 active:scale-[0.99] transition-all shadow-sm disabled:opacity-60"
          >
            {generating ? (
              <><Loader2 size={15} className="animate-spin" /> Generating Questions…</>
            ) : (
              <><Sparkles size={15} /> Generate Quiz</>
            )}
          </button>
        </div>
      </div>
    );
  }

  // ── Results screen ────────────────────────────────────────────────────────────
  if (phase === "results") {
    return (
      <ScoreSummary
        questions={questions}
        answers={answers}
        subject={subject}
        topic={topic}
        elapsed={elapsed}
        onRetake={retake}
        onNewQuiz={newQuiz}
      />
    );
  }

  // ── Quiz screen ───────────────────────────────────────────────────────────────
  return (
    <div className="flex flex-col gap-6 max-w-2xl mx-auto w-full">
      {/* Quiz header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-gray-900">Study Quiz</h1>
          <p className="text-sm text-gray-400 mt-0.5">{subject} · {topic}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs bg-white border border-[rgba(0,0,0,0.07)] text-gray-500 px-3 py-1.5 rounded-xl shadow-sm">
            {answered} / {questions.length} answered
          </span>
          <button
            onClick={newQuiz}
            className="text-xs text-gray-400 hover:text-gray-600 px-3 py-1.5 rounded-xl hover:bg-white transition-all"
          >
            ← Back
          </button>
        </div>
      </div>

      {/* Answered progress strip */}
      <div className="flex gap-1">
        {questions.map((q, i) => (
          <div
            key={q.id}
            className={`flex-1 h-1 rounded-full transition-colors duration-300 ${
              answers[q.id] ? "bg-[#4ade80]" : "bg-gray-200"
            }`}
          />
        ))}
      </div>

      {/* Question cards */}
      <div className="flex flex-col gap-5">
        {questions.map((q) => (
          <div
            key={q.id}
            className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm overflow-hidden"
          >
            {/* Question header */}
            <div className="px-5 py-4 border-b border-[rgba(0,0,0,0.05)] flex items-start gap-3">
              <span className="w-7 h-7 rounded-lg bg-gray-900 text-white text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                {q.number}
              </span>
              <p className="text-sm text-gray-800 leading-relaxed pt-0.5">{q.text}</p>
            </div>

            {/* Options grid */}
            <div className="p-4 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {q.options.map((opt) => (
                <OptionCard
                  key={opt.id}
                  option={opt}
                  selected={answers[q.id] === opt.id}
                  revealed={revealed.has(q.id)}
                  isCorrect={opt.id === q.correctId}
                  onSelect={() => select(q.id, opt.id)}
                />
              ))}
            </div>

            {/* Explanation (after reveal) */}
            {revealed.has(q.id) && (
              <div className="mx-4 mb-4 px-4 py-3 bg-[#f8fafc] rounded-xl border border-[rgba(0,0,0,0.05)] text-xs text-gray-500 leading-relaxed">
                <span className="font-semibold text-gray-700 mr-1">Explanation:</span>
                {q.explanation}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Submit */}
      <div className="pb-4">
        <button
          onClick={submit}
          disabled={!allAnswered}
          className={`w-full flex items-center justify-center gap-2 py-3.5 rounded-xl text-sm font-medium transition-all duration-200 shadow-sm active:scale-[0.99]
            ${allAnswered
              ? "bg-gray-900 text-white hover:bg-gray-700 shadow-md"
              : "bg-gray-100 text-gray-400 cursor-not-allowed"
            }`}
        >
          {allAnswered ? (
            <><Sparkles size={15} /> Submit Answers &amp; Get Analysis</>
          ) : (
            `Answer all questions to submit (${answered}/${questions.length} done)`
          )}
        </button>
      </div>
    </div>
  );
}
