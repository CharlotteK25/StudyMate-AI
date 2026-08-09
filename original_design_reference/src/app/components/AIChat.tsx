import { useState, useRef, useEffect, useCallback } from "react";
import {
  Send,
  Plus,
  Search,
  Settings,
  MessageSquare,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  X,
  Menu,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface Thread {
  id: string;
  title: string;
  preview: string;
  date: string;
  messages: Message[];
}

// ─── Seed data ────────────────────────────────────────────────────────────────

const SEED_THREADS: Thread[] = [
  {
    id: "t1",
    title: "Chapter 3 Summary",
    preview: "Can you summarise Chapter 3 of…",
    date: "Today",
    messages: [
      { id: "m1", role: "user", content: "Can you summarise Chapter 3 of my Biology notes?", timestamp: new Date() },
      { id: "m2", role: "assistant", content: "Sure! Chapter 3 covers **Cell Structure and Function**. Key topics include:\n\n- The cell membrane and its selective permeability\n- Organelles: nucleus, mitochondria, ribosomes, endoplasmic reticulum, and Golgi apparatus\n- Differences between prokaryotic and eukaryotic cells\n- Cell transport mechanisms: diffusion, osmosis, and active transport\n\nWould you like me to go deeper on any specific section?", timestamp: new Date() },
    ],
  },
  {
    id: "t2",
    title: "Explain Concept X",
    preview: "What is cellular respiration?",
    date: "Today",
    messages: [
      { id: "m3", role: "user", content: "What is cellular respiration?", timestamp: new Date() },
      { id: "m4", role: "assistant", content: "Cellular respiration is the process by which cells break down glucose to produce ATP (energy). It occurs in three main stages:\n\n1. **Glycolysis** — in the cytoplasm, glucose splits into pyruvate\n2. **Krebs Cycle** — in the mitochondrial matrix, pyruvate is oxidised\n3. **Electron Transport Chain** — on the inner mitochondrial membrane, producing most ATP\n\nThe overall equation: C₆H₁₂O₆ + 6O₂ → 6CO₂ + 6H₂O + ATP", timestamp: new Date() },
    ],
  },
  {
    id: "t3",
    title: "Explain Concept Y",
    preview: "How does photosynthesis work?",
    date: "Yesterday",
    messages: [],
  },
  {
    id: "t4",
    title: "Chapter 3 Summary",
    preview: "Summarise the key equations…",
    date: "Yesterday",
    messages: [],
  },
  {
    id: "t5",
    title: "Explain 3 Summary",
    preview: "Newton's laws explained simply…",
    date: "This week",
    messages: [],
  },
  {
    id: "t6",
    title: "Chapter 3 Summary",
    preview: "What are the main themes in…",
    date: "This week",
    messages: [],
  },
];

const SUGGESTED_PROMPTS = [
  "Summarise Chapter 3",
  "Explain this concept",
  "Quiz me on Biology",
  "Create flashcards",
  "What are key formulas?",
  "Help me study tonight",
];

const AI_RESPONSES: Record<string, string> = {
  default: "That's a great question! Let me break it down for you.\n\nBased on your study materials, here's what you need to know:\n\n- The core concept revolves around fundamental principles\n- There are several key relationships worth remembering\n- Practice problems will help reinforce your understanding\n\nWould you like me to generate some practice questions on this topic?",
  summarise: "Here's a concise summary:\n\n**Key Points:**\n1. The main argument centres on the relationship between cause and effect\n2. Supporting evidence is drawn from empirical observations\n3. Conclusions align with established theoretical frameworks\n\nShall I create flashcards from this summary?",
  quiz: "Let's test your knowledge! Here's a quick question:\n\n**Q: What is the primary function of mitochondria?**\n\na) Protein synthesis\nb) Energy production (ATP)\nc) DNA replication\nd) Cell division\n\nTake your time — reply with your answer and I'll give you feedback!",
  flashcard: "I've generated 5 flashcards from your notes:\n\n1. **Q:** What is osmosis? **A:** Movement of water across a semipermeable membrane from low to high solute concentration.\n\n2. **Q:** Define ATP. **A:** Adenosine triphosphate — the primary energy currency of the cell.\n\nHead to your Flashcards page to review the full set!",
  formula: "Here are the key formulas you should know:\n\n**Physics:**\n- F = ma (Newton's 2nd Law)\n- E = mc² (Mass-energy equivalence)\n- v = u + at (Kinematic equation)\n\n**Chemistry:**\n- PV = nRT (Ideal gas law)\n- pH = −log[H⁺]\n\nWant me to explain any of these in detail?",
};

function getAIResponse(input: string): string {
  const lower = input.toLowerCase();
  if (lower.includes("summar")) return AI_RESPONSES.summarise;
  if (lower.includes("quiz") || lower.includes("test")) return AI_RESPONSES.quiz;
  if (lower.includes("flashcard")) return AI_RESPONSES.flashcard;
  if (lower.includes("formula") || lower.includes("equation")) return AI_RESPONSES.formula;
  return AI_RESPONSES.default;
}

// ─── Owl avatar ───────────────────────────────────────────────────────────────

function OwlAvatar({ size = 28 }: { size?: number }) {
  return (
    <div
      className="rounded-xl bg-[#f0fdf4] border border-[#bbf7d0] flex items-center justify-center shrink-0"
      style={{ width: size, height: size }}
    >
      <span style={{ fontSize: size * 0.55 }}>🦉</span>
    </div>
  );
}

// ─── Message bubble ───────────────────────────────────────────────────────────

function renderMarkdown(text: string) {
  const lines = text.split("\n");
  const elements: React.ReactNode[] = [];
  let key = 0;

  for (const line of lines) {
    if (line.trim() === "") { elements.push(<div key={key++} className="h-2" />); continue; }

    // Bold inline
    const parts = line.split(/(\*\*[^*]+\*\*)/g).map((p, i) =>
      p.startsWith("**") && p.endsWith("**")
        ? <strong key={i} className="font-semibold text-gray-800">{p.slice(2, -2)}</strong>
        : p
    );

    if (/^\d+\.\s/.test(line)) {
      elements.push(<p key={key++} className="text-sm leading-relaxed pl-1">{parts}</p>);
    } else if (line.startsWith("- ") || line.startsWith("• ")) {
      elements.push(
        <div key={key++} className="flex items-start gap-2 text-sm leading-relaxed">
          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#4ade80] shrink-0" />
          <span>{parts}</span>
        </div>
      );
    } else {
      elements.push(<p key={key++} className="text-sm leading-relaxed">{parts}</p>);
    }
  }
  return elements;
}

function MessageBubble({ message, isLast }: { message: Message; isLast: boolean }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const copy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="flex items-end gap-2 max-w-[72%]">
          <div className="bg-gray-900 text-white rounded-2xl rounded-br-md px-4 py-3 shadow-sm">
            <p className="text-sm leading-relaxed">{message.content}</p>
          </div>
          <div className="w-7 h-7 rounded-full bg-[#bbf7d0] flex items-center justify-center text-[#15803d] text-xs font-semibold shrink-0 mb-0.5">
            JA
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3 max-w-[85%]">
      <OwlAvatar size={30} />
      <div className="flex flex-col gap-1.5 min-w-0">
        <div className="bg-white border border-[rgba(0,0,0,0.07)] rounded-2xl rounded-tl-md px-4 py-3 shadow-sm">
          <div className="flex flex-col gap-1 text-gray-700">
            {renderMarkdown(message.content)}
          </div>
        </div>
        {isLast && (
          <div className="flex items-center gap-1 pl-1">
            <button
              onClick={copy}
              className="flex items-center gap-1 text-[10px] text-gray-400 hover:text-gray-600 px-2 py-1 rounded-lg hover:bg-gray-100 transition-all"
            >
              <Copy size={11} />{copied ? "Copied!" : "Copy"}
            </button>
            <button className="p-1 rounded-lg text-gray-400 hover:text-[#16a34a] hover:bg-gray-100 transition-all">
              <ThumbsUp size={11} />
            </button>
            <button className="p-1 rounded-lg text-gray-400 hover:text-[#dc2626] hover:bg-gray-100 transition-all">
              <ThumbsDown size={11} />
            </button>
            <button className="p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-all">
              <RotateCcw size={11} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Typing indicator ─────────────────────────────────────────────────────────

function TypingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <OwlAvatar size={30} />
      <div className="bg-white border border-[rgba(0,0,0,0.07)] rounded-2xl rounded-tl-md px-4 py-3.5 shadow-sm">
        <div className="flex items-center gap-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-[#86efac] animate-bounce"
              style={{ animationDelay: `${i * 0.15}s`, animationDuration: "0.9s" }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Thread group ─────────────────────────────────────────────────────────────

function ThreadGroup({
  date,
  threads,
  activeId,
  onSelect,
}: {
  date: string;
  threads: Thread[];
  activeId: string;
  onSelect: (id: string) => void;
}) {
  const [open, setOpen] = useState(true);
  return (
    <div>
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-widest text-gray-400 hover:text-gray-600 transition-colors"
      >
        {open ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
        {date}
      </button>
      {open && (
        <div className="flex flex-col gap-0.5">
          {threads.map((t) => (
            <button
              key={t.id}
              onClick={() => onSelect(t.id)}
              className={`w-full text-left px-3 py-2.5 rounded-xl mx-1 transition-all duration-150 group ${
                t.id === activeId
                  ? "bg-[#f0fdf4] border border-[#86efac]"
                  : "hover:bg-gray-100 border border-transparent"
              }`}
              style={{ width: "calc(100% - 8px)" }}
            >
              <div className="flex items-center gap-2">
                <MessageSquare
                  size={13}
                  className={t.id === activeId ? "text-[#16a34a]" : "text-gray-400"}
                />
                <span className={`text-xs truncate ${t.id === activeId ? "text-[#15803d] font-medium" : "text-gray-600"}`}>
                  {t.title}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export function AIChat() {
  const [threads, setThreads] = useState<Thread[]>(SEED_THREADS);
  const [activeThreadId, setActiveThreadId] = useState("t1");
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const activeThread = threads.find((t) => t.id === activeThreadId)!;
  const messages = activeThread?.messages ?? [];

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const send = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isTyping) return;

      const userMsg: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed,
        timestamp: new Date(),
      };

      setThreads((prev) =>
        prev.map((t) =>
          t.id === activeThreadId
            ? { ...t, messages: [...t.messages, userMsg], preview: trimmed.slice(0, 50) }
            : t
        )
      );
      setInput("");
      setIsTyping(true);

      setTimeout(() => {
        const aiMsg: Message = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: getAIResponse(trimmed),
          timestamp: new Date(),
        };
        setThreads((prev) =>
          prev.map((t) =>
            t.id === activeThreadId ? { ...t, messages: [...t.messages, aiMsg] } : t
          )
        );
        setIsTyping(false);
      }, 1200 + Math.random() * 600);
    },
    [activeThreadId, isTyping]
  );

  const newThread = () => {
    const id = crypto.randomUUID();
    const thread: Thread = {
      id,
      title: "New Chat",
      preview: "Start a new conversation…",
      date: "Today",
      messages: [],
    };
    setThreads((prev) => [thread, ...prev]);
    setActiveThreadId(id);
    setTimeout(() => inputRef.current?.focus(), 50);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  const filteredThreads = threads.filter((t) =>
    t.title.toLowerCase().includes(searchQuery.toLowerCase())
  );
  const grouped = ["Today", "Yesterday", "This week"].map((date) => ({
    date,
    items: filteredThreads.filter((t) => t.date === date),
  })).filter((g) => g.items.length > 0);

  const isEmpty = messages.length === 0;

  return (
    <div className="flex h-[calc(100vh-4rem)] -mt-6 -mx-4 sm:-mx-6 lg:-mx-8 overflow-hidden">

      {/* ── Sidebar ─────────────────────────────────────────────────────────── */}
      <aside
        className={`flex flex-col bg-[#fafafa] border-r border-[rgba(0,0,0,0.07)] transition-all duration-300 shrink-0 overflow-hidden ${
          sidebarOpen ? "w-64" : "w-0"
        }`}
      >
        <div className="flex items-center justify-between px-4 pt-4 pb-3 shrink-0">
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Chats</span>
          <button
            onClick={newThread}
            className="w-7 h-7 rounded-lg bg-gray-900 text-white flex items-center justify-center hover:bg-gray-700 active:scale-95 transition-all"
            title="New chat"
          >
            <Plus size={14} />
          </button>
        </div>

        {/* Search */}
        <div className="px-3 pb-3 shrink-0">
          <div className="relative">
            <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search chats…"
              className="w-full bg-white border border-[rgba(0,0,0,0.08)] rounded-xl pl-7 pr-3 py-2 text-xs text-gray-600 placeholder-gray-400 focus:outline-none focus:border-[#86efac] focus:ring-2 focus:ring-[#4ade80]/20 transition-all"
            />
          </div>
        </div>

        {/* Thread list */}
        <div className="flex-1 overflow-y-auto py-1 px-1 flex flex-col gap-1">
          {grouped.map((g) => (
            <ThreadGroup
              key={g.date}
              date={g.date}
              threads={g.items}
              activeId={activeThreadId}
              onSelect={setActiveThreadId}
            />
          ))}
        </div>

        {/* Sidebar footer */}
        <div className="px-4 py-3 border-t border-[rgba(0,0,0,0.06)] shrink-0 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#bbf7d0] flex items-center justify-center text-[#15803d] text-[10px] font-semibold">JA</div>
            <span className="text-xs text-gray-500">Jamie</span>
          </div>
          <button className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-200 transition-all">
            <Settings size={13} />
          </button>
        </div>
      </aside>

      {/* ── Main pane ───────────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#f8fafc]">

        {/* Chat header */}
        <div className="bg-white border-b border-[rgba(0,0,0,0.07)] px-5 h-14 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen((o) => !o)}
              className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-all"
            >
              <Menu size={16} />
            </button>
            <div className="flex items-center gap-2">
              <OwlAvatar size={26} />
              <div>
                <span className="text-sm font-medium text-gray-800">{activeThread?.title ?? "Chat"}</span>
                <div className="flex items-center gap-1 -mt-0.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#4ade80]" />
                  <span className="text-[10px] text-gray-400">StudyMate AI · Online</span>
                </div>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={newThread}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs text-gray-500 hover:bg-gray-100 transition-all"
            >
              <Plus size={13} /> New chat
            </button>
          </div>
        </div>

        {/* Message log */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-6 flex flex-col gap-5">
          {isEmpty ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-6 py-16">
              <div className="flex flex-col items-center gap-3">
                <OwlAvatar size={56} />
                <div className="text-center">
                  <h2 className="text-gray-800">Friendly AI assistant experience</h2>
                  <p className="text-sm text-gray-400 mt-1">Ask anything about your study materials</p>
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-w-md w-full">
                {["Summarise my notes", "Explain a concept", "Quiz me", "Create flashcards", "Help me revise", "Key formulas"].map((p) => (
                  <button
                    key={p}
                    onClick={() => send(p)}
                    className="text-xs text-gray-600 bg-white border border-[rgba(0,0,0,0.08)] px-3 py-2.5 rounded-xl hover:border-[#86efac] hover:bg-[#f0fdf4] hover:text-[#15803d] transition-all text-left leading-snug shadow-sm"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <MessageBubble key={msg.id} message={msg} isLast={i === messages.length - 1 && msg.role === "assistant"} />
              ))}
              {isTyping && <TypingIndicator />}
            </>
          )}
          <div ref={bottomRef} />
        </div>

        {/* ── Sticky input area ──────────────────────────────────────────────── */}
        <div className="bg-white border-t border-[rgba(0,0,0,0.07)] px-4 sm:px-8 pt-3 pb-4 shrink-0">
          {/* Suggested prompts */}
          <div className="flex items-center gap-2 mb-3 overflow-x-auto pb-1 scrollbar-hide">
            <span className="text-[10px] text-gray-400 shrink-0 font-medium">Suggested:</span>
            {SUGGESTED_PROMPTS.map((p) => (
              <button
                key={p}
                onClick={() => send(p)}
                className="shrink-0 text-xs text-gray-600 bg-[#f3f4f6] hover:bg-[#f0fdf4] hover:text-[#15803d] hover:border-[#86efac] border border-transparent px-3 py-1.5 rounded-full transition-all duration-150 whitespace-nowrap active:scale-95"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Input row */}
          <div className="flex items-end gap-2 bg-white border border-[rgba(0,0,0,0.1)] rounded-2xl px-4 py-3 focus-within:border-[#4ade80] focus-within:ring-2 focus-within:ring-[#4ade80]/20 transition-all shadow-sm">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
              }}
              onKeyDown={handleKeyDown}
              placeholder="Ask StudyMate anything…"
              rows={1}
              className="flex-1 resize-none bg-transparent text-sm text-gray-800 placeholder-gray-400 focus:outline-none leading-relaxed"
              style={{ minHeight: "24px", maxHeight: "120px" }}
            />
            <button
              onClick={() => send(input)}
              disabled={!input.trim() || isTyping}
              className={`w-8 h-8 rounded-xl flex items-center justify-center transition-all duration-150 active:scale-95 shrink-0 mb-0.5 ${
                input.trim() && !isTyping
                  ? "bg-gray-900 text-white hover:bg-gray-700 shadow-sm"
                  : "bg-gray-100 text-gray-300 cursor-not-allowed"
              }`}
              aria-label="Send message"
            >
              <Send size={14} />
            </button>
          </div>
          <p className="text-center text-[10px] text-gray-300 mt-2">
            StudyMate AI · Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
