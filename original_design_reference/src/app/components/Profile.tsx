import { useState, useRef } from "react";
import {
  User,
  Target,
  Bell,
  Camera,
  Check,
  X,
  LogOut,
  ChevronRight,
  Mail,
  BookOpen,
  Shield,
  Trash2,
  Eye,
  EyeOff,
  AlertTriangle,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

type Section = "account" | "goals" | "notifications";

interface ToggleProps {
  checked: boolean;
  onChange: (v: boolean) => void;
  label: string;
  description?: string;
}

interface TextFieldProps {
  label: string;
  value: string;
  type?: string;
  placeholder?: string;
  onChange: (v: string) => void;
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function Toggle({ checked, onChange, label, description }: ToggleProps) {
  return (
    <div className="flex items-center justify-between gap-4 py-3.5 border-b border-[rgba(0,0,0,0.05)] last:border-0">
      <div className="flex flex-col gap-0.5">
        <span className="text-sm text-gray-700">{label}</span>
        {description && <span className="text-xs text-gray-400 leading-snug">{description}</span>}
      </div>
      <button
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
          checked
            ? "bg-[#4ade80] border-[#4ade80] focus:ring-[#4ade80]/30"
            : "bg-gray-200 border-gray-200 focus:ring-gray-300"
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform duration-200 ${
            checked ? "translate-x-5" : "translate-x-0.5"
          }`}
        />
      </button>
    </div>
  );
}

function TextField({ label, value, type = "text", placeholder, onChange }: TextFieldProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const [showPw, setShowPw] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const commit = () => { onChange(draft); setEditing(false); };
  const cancel = () => { setDraft(value); setEditing(false); };

  const inputType = type === "password" ? (showPw ? "text" : "password") : type;

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</label>
      {editing ? (
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <input
              ref={inputRef}
              autoFocus
              type={inputType}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") commit(); if (e.key === "Escape") cancel(); }}
              className="w-full bg-white border-2 border-[#4ade80] rounded-xl px-4 py-2.5 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-[#4ade80]/20 transition-all pr-10"
            />
            {type === "password" && (
              <button
                type="button"
                onClick={() => setShowPw((s) => !s)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
              </button>
            )}
          </div>
          <button onClick={commit} className="w-8 h-8 rounded-xl bg-[#4ade80] text-white flex items-center justify-center hover:bg-[#22c55e] active:scale-95 transition-all shadow-sm">
            <Check size={14} />
          </button>
          <button onClick={cancel} className="w-8 h-8 rounded-xl bg-gray-100 text-gray-500 flex items-center justify-center hover:bg-gray-200 active:scale-95 transition-all">
            <X size={14} />
          </button>
        </div>
      ) : (
        <button
          onClick={() => { setDraft(value); setEditing(true); }}
          className="w-full flex items-center justify-between bg-[#f8fafc] border border-[rgba(0,0,0,0.08)] rounded-xl px-4 py-2.5 text-sm text-gray-700 hover:border-[#86efac] hover:bg-[#f0fdf4]/50 transition-all group text-left"
        >
          <span className={type === "password" ? "tracking-widest text-gray-400" : ""}>
            {type === "password" ? "••••••••" : value || placeholder}
          </span>
          <span className="text-xs text-gray-400 group-hover:text-[#16a34a] transition-colors">Edit</span>
        </button>
      )}
    </div>
  );
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-[rgba(0,0,0,0.05)]">
        <h3 className="text-gray-900">{title}</h3>
      </div>
      <div className="px-6 py-5">{children}</div>
    </div>
  );
}

// ─── Avatar uploader ──────────────────────────────────────────────────────────

function AvatarUpload({ name }: { name: string }) {
  const [preview, setPreview] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const initials = name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target?.result as string);
    reader.readAsDataURL(file);
  };

  return (
    <div className="flex items-center gap-5">
      <div className="relative group">
        <div
          className={`w-20 h-20 rounded-2xl flex items-center justify-center overflow-hidden transition-all duration-200 cursor-pointer border-2 ${
            dragging ? "border-[#4ade80] scale-105" : "border-transparent"
          }`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) handleFile(f); }}
          onClick={() => fileRef.current?.click()}
        >
          {preview ? (
            <img src={preview} alt="Avatar" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-[#bbf7d0] to-[#4ade80] flex items-center justify-center">
              <span className="text-white font-bold text-xl">{initials}</span>
            </div>
          )}
          <div className="absolute inset-0 bg-black/30 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <Camera size={18} className="text-white" />
          </div>
        </div>
        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[#4ade80] rounded-lg flex items-center justify-center shadow-sm border-2 border-white cursor-pointer" onClick={() => fileRef.current?.click()}>
          <Camera size={11} className="text-white" />
        </div>
        <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
      </div>
      <div>
        <p className="text-sm font-medium text-gray-700">{name}</p>
        <p className="text-xs text-gray-400 mt-0.5">Click or drag to update photo</p>
        {preview && (
          <button onClick={() => setPreview(null)} className="text-xs text-[#dc2626] hover:underline mt-1 flex items-center gap-1">
            <X size={10} /> Remove photo
          </button>
        )}
      </div>
    </div>
  );
}

// ─── Section renderers ────────────────────────────────────────────────────────

function AccountSection() {
  const [name, setName] = useState("Carmen Koh");
  const [email, setEmail] = useState("carmen@university.edu.my");
  const [password, setPassword] = useState("password123");

  return (
    <div className="flex flex-col gap-5">
      <SectionCard title="Profile">
        <div className="flex flex-col gap-5">
          <AvatarUpload name={name} />
          <div className="border-t border-[rgba(0,0,0,0.05)] pt-5 flex flex-col gap-4">
            <TextField label="Full Name" value={name} onChange={setName} placeholder="Enter your name" />
            <TextField label="Email Address" value={email} type="email" onChange={setEmail} placeholder="Enter your email" />
            <TextField label="Password" value={password} type="password" onChange={setPassword} />
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Danger Zone">
        <div className="flex flex-col gap-3">
          <p className="text-xs text-gray-400 leading-relaxed">
            Permanent actions that cannot be undone. Please proceed with caution.
          </p>
          <div className="flex items-center justify-between py-3 px-4 bg-[#fef2f2] rounded-xl border border-[#fecaca]">
            <div className="flex items-center gap-2.5">
              <AlertTriangle size={15} className="text-[#dc2626] shrink-0" />
              <div>
                <p className="text-sm font-medium text-[#dc2626]">Delete Account</p>
                <p className="text-xs text-[#dc2626]/60">All data will be permanently removed</p>
              </div>
            </div>
            <button className="text-xs font-medium text-[#dc2626] border border-[#fca5a5] px-3 py-1.5 rounded-lg hover:bg-[#fef2f2] active:scale-95 transition-all flex items-center gap-1.5">
              <Trash2 size={12} /> Delete
            </button>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}

function GoalsSection() {
  const [dailyHours, setDailyHours] = useState(4);
  const [weeklyTarget, setWeeklyTarget] = useState(20);
  const [subjects, setSubjects] = useState(["Biology", "Chemistry", "Physics"]);
  const [newSubject, setNewSubject] = useState("");

  const addSubject = () => {
    const s = newSubject.trim();
    if (s && !subjects.includes(s)) { setSubjects((p) => [...p, s]); setNewSubject(""); }
  };

  return (
    <div className="flex flex-col gap-5">
      <SectionCard title="Daily Study Goal">
        <div className="flex flex-col gap-5">
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Daily Target</label>
              <span className="text-sm font-semibold text-gray-800">{dailyHours}h / day</span>
            </div>
            <input
              type="range" min={1} max={12} step={0.5} value={dailyHours}
              onChange={(e) => setDailyHours(Number(e.target.value))}
              className="w-full h-2 rounded-full appearance-none cursor-pointer accent-[#4ade80] bg-gray-200"
            />
            <div className="flex justify-between text-[10px] text-gray-400">
              <span>1h</span><span>6h</span><span>12h</span>
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Weekly Target</label>
              <span className="text-sm font-semibold text-gray-800">{weeklyTarget}h / week</span>
            </div>
            <input
              type="range" min={5} max={60} step={1} value={weeklyTarget}
              onChange={(e) => setWeeklyTarget(Number(e.target.value))}
              className="w-full h-2 rounded-full appearance-none cursor-pointer accent-[#4ade80] bg-gray-200"
            />
          </div>

          <div className="pt-1 border-t border-[rgba(0,0,0,0.05)] flex gap-4 text-center">
            {[{ label: "Daily", val: `${dailyHours}h` }, { label: "Weekly", val: `${weeklyTarget}h` }, { label: "Monthly est.", val: `${Math.round(weeklyTarget * 4.3)}h` }].map(({ label, val }) => (
              <div key={label} className="flex-1 bg-[#f0fdf4] rounded-xl py-3">
                <p className="text-base font-semibold text-[#15803d]">{val}</p>
                <p className="text-[10px] text-gray-400 mt-0.5">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </SectionCard>

      <SectionCard title="Focus Subjects">
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap gap-2">
            {subjects.map((s) => (
              <span key={s} className="flex items-center gap-1.5 text-xs bg-[#f0fdf4] text-[#15803d] border border-[#bbf7d0] px-3 py-1.5 rounded-full">
                {s}
                <button onClick={() => setSubjects((p) => p.filter((x) => x !== s))} className="text-[#86efac] hover:text-[#dc2626] transition-colors">
                  <X size={11} />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              value={newSubject}
              onChange={(e) => setNewSubject(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addSubject()}
              placeholder="Add a subject…"
              className="flex-1 bg-[#f8fafc] border border-[rgba(0,0,0,0.08)] rounded-xl px-4 py-2 text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:border-[#4ade80] focus:ring-2 focus:ring-[#4ade80]/20 transition-all"
            />
            <button onClick={addSubject} className="px-4 py-2 rounded-xl bg-[#f0fdf4] text-[#16a34a] text-sm font-medium border border-[#86efac] hover:bg-[#dcfce7] active:scale-95 transition-all">
              Add
            </button>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}

function NotificationsSection() {
  const [prefs, setPrefs] = useState({
    studyReminders: true,
    quizResults: true,
    weeklyReport: true,
    streakAlerts: true,
    aiSuggestions: false,
    emailDigest: false,
    pushNotifications: true,
    soundEffects: false,
  });

  const set = (key: keyof typeof prefs) => (v: boolean) =>
    setPrefs((p) => ({ ...p, [key]: v }));

  return (
    <div className="flex flex-col gap-5">
      <SectionCard title="Study Reminders">
        <div>
          <Toggle checked={prefs.studyReminders} onChange={set("studyReminders")} label="Daily study reminders" description="Get notified when it's time to study based on your goal schedule" />
          <Toggle checked={prefs.streakAlerts} onChange={set("streakAlerts")} label="Streak alerts" description="Be reminded to keep your learning streak alive" />
          <Toggle checked={prefs.aiSuggestions} onChange={set("aiSuggestions")} label="AI study suggestions" description="Receive personalised tips and recommended topics" />
        </div>
      </SectionCard>

      <SectionCard title="Results & Reports">
        <div>
          <Toggle checked={prefs.quizResults} onChange={set("quizResults")} label="Quiz result notifications" description="Instant notification after completing a quiz" />
          <Toggle checked={prefs.weeklyReport} onChange={set("weeklyReport")} label="Weekly progress report" description="A summary of your study activity every Sunday" />
          <Toggle checked={prefs.emailDigest} onChange={set("emailDigest")} label="Email digest" description="Receive a weekly digest to your registered email" />
        </div>
      </SectionCard>

      <SectionCard title="App Preferences">
        <div>
          <Toggle checked={prefs.pushNotifications} onChange={set("pushNotifications")} label="Push notifications" description="Allow browser push notifications from StudyMate" />
          <Toggle checked={prefs.soundEffects} onChange={set("soundEffects")} label="Sound effects" description="Play sounds for streaks, achievements, and quiz results" />
        </div>
      </SectionCard>
    </div>
  );
}

// ─── Logout modal ─────────────────────────────────────────────────────────────

function LogoutModal({ onCancel, onConfirm }: { onCancel: () => void; onConfirm: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
      <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.08)] shadow-xl p-6 w-80 flex flex-col gap-4">
        <div className="flex flex-col items-center gap-3 text-center">
          <div className="w-12 h-12 rounded-2xl bg-[#fef2f2] flex items-center justify-center">
            <LogOut size={22} className="text-[#dc2626]" />
          </div>
          <div>
            <h3 className="text-gray-900">Log out?</h3>
            <p className="text-sm text-gray-400 mt-1">You'll need to sign back in to access your study dashboard.</p>
          </div>
        </div>
        <div className="flex gap-2 pt-1">
          <button onClick={onCancel} className="flex-1 py-2.5 rounded-xl text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 active:scale-95 transition-all">
            Cancel
          </button>
          <button onClick={onConfirm} className="flex-1 py-2.5 rounded-xl text-sm font-medium text-white bg-[#dc2626] hover:bg-[#b91c1c] active:scale-95 transition-all shadow-sm flex items-center justify-center gap-1.5">
            <LogOut size={14} /> Log Out
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

const NAV_ITEMS: { id: Section; label: string; icon: React.ElementType; description: string }[] = [
  { id: "account", label: "Account", icon: User, description: "Profile & security" },
  { id: "goals", label: "Goals", icon: Target, description: "Study targets" },
  { id: "notifications", label: "Notifications", icon: Bell, description: "Alerts & reminders" },
];

export function Profile({ onLogout }: { onLogout?: () => void }) {
  const [section, setSection] = useState<Section>("account");
  const [showLogout, setShowLogout] = useState(false);

  const current = NAV_ITEMS.find((n) => n.id === section)!;

  return (
    <>
      {showLogout && <LogoutModal onCancel={() => setShowLogout(false)} onConfirm={() => { setShowLogout(false); onLogout?.(); }} />}

      <div className="flex gap-6 items-start">
        {/* ── Left sidebar ──────────────────────────────────────────────── */}
        <aside className="w-56 shrink-0 flex flex-col gap-2 sticky top-24">
          <div className="bg-white rounded-2xl border border-[rgba(0,0,0,0.07)] shadow-sm overflow-hidden">
            {/* Profile mini */}
            <div className="px-4 pt-5 pb-4 border-b border-[rgba(0,0,0,0.05)] flex flex-col items-center gap-2 text-center">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#bbf7d0] to-[#4ade80] flex items-center justify-center">
                <span className="text-white font-bold text-lg">CK</span>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-800">Carmen Koh</p>
                <p className="text-xs text-gray-400">carmen@university.edu.my</p>
              </div>
              <span className="text-[10px] bg-[#f0fdf4] text-[#16a34a] px-2 py-0.5 rounded-lg font-medium border border-[#bbf7d0]">
                Student
              </span>
            </div>

            {/* Nav links */}
            <nav className="p-2 flex flex-col gap-0.5">
              {NAV_ITEMS.map(({ id, label, icon: Icon, description }) => {
                const active = section === id;
                return (
                  <button
                    key={id}
                    onClick={() => setSection(id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-150 group ${
                      active
                        ? "bg-[#f0fdf4] border border-[#86efac]"
                        : "border border-transparent hover:bg-gray-50"
                    }`}
                  >
                    <Icon size={15} className={active ? "text-[#16a34a]" : "text-gray-400"} />
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm ${active ? "font-medium text-[#15803d]" : "text-gray-600"}`}>{label}</p>
                      <p className="text-[10px] text-gray-400 truncate">{description}</p>
                    </div>
                    <ChevronRight size={12} className={`shrink-0 transition-opacity ${active ? "opacity-100 text-[#4ade80]" : "opacity-0 group-hover:opacity-50"}`} />
                  </button>
                );
              })}
            </nav>

            {/* Logout */}
            <div className="p-2 pt-0">
              <button
                onClick={() => setShowLogout(true)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl border border-[#fecaca] bg-[#fef2f2] text-[#dc2626] hover:bg-[#fee2e2] hover:border-[#fca5a5] active:scale-[0.98] transition-all group"
              >
                <LogOut size={15} />
                <span className="text-sm font-medium">Log Out</span>
              </button>
            </div>
          </div>
        </aside>

        {/* ── Right pane ────────────────────────────────────────────────── */}
        <div className="flex-1 min-w-0 flex flex-col gap-2">
          {/* Section header */}
          <div className="flex items-center justify-between mb-1">
            <div>
              <h1 className="text-gray-900">{current.label}</h1>
              <p className="text-sm text-gray-400 mt-0.5">{current.description}</p>
            </div>
          </div>

          {section === "account" && <AccountSection />}
          {section === "goals" && <GoalsSection />}
          {section === "notifications" && <NotificationsSection />}
        </div>
      </div>
    </>
  );
}
