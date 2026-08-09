import { useState } from "react";
import { Eye, EyeOff, Mail, Lock, User, ArrowRight, Check, AlertCircle, Loader2 } from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

type Mode = "signin" | "signup" | "forgot";

interface InputProps {
  label: string;
  type?: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  icon: React.ElementType;
  error?: string;
  autoComplete?: string;
}

// ─── Password strength ────────────────────────────────────────────────────────

function passwordStrength(pw: string): { score: number; label: string; color: string } {
  if (!pw) return { score: 0, label: "", color: "" };
  let score = 0;
  if (pw.length >= 8) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;
  const map = [
    { score: 1, label: "Weak", color: "#ef4444" },
    { score: 2, label: "Fair", color: "#f97316" },
    { score: 3, label: "Good", color: "#eab308" },
    { score: 4, label: "Strong", color: "#22c55e" },
  ];
  return map[score - 1] ?? { score: 0, label: "", color: "" };
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function FormInput({ label, type = "text", value, onChange, placeholder, icon: Icon, error, autoComplete }: InputProps) {
  const [show, setShow] = useState(false);
  const [focused, setFocused] = useState(false);
  const isPassword = type === "password";
  const resolvedType = isPassword ? (show ? "text" : "password") : type;

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">{label}</label>
      <div className={`relative flex items-center rounded-[12px] border-2 transition-all duration-200 bg-white ${
        error
          ? "border-red-400 ring-2 ring-red-100"
          : focused
          ? "border-[#4ade80] ring-2 ring-[#4ade80]/15 shadow-sm"
          : "border-gray-200 hover:border-gray-300"
      }`}>
        <Icon size={15} className={`absolute left-3.5 transition-colors ${focused ? "text-[#16a34a]" : "text-gray-400"}`} />
        <input
          type={resolvedType}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          className="w-full bg-transparent pl-9 pr-10 py-3 text-sm text-gray-800 placeholder-gray-400 focus:outline-none rounded-[12px]"
        />
        {isPassword && (
          <button
            type="button"
            tabIndex={-1}
            onClick={() => setShow((s) => !s)}
            className="absolute right-3 text-gray-400 hover:text-gray-600 transition-colors"
          >
            {show ? <EyeOff size={15} /> : <Eye size={15} />}
          </button>
        )}
        {!isPassword && value && !error && (
          <Check size={14} className="absolute right-3.5 text-[#22c55e]" />
        )}
      </div>
      {error && (
        <p className="flex items-center gap-1.5 text-xs text-red-500">
          <AlertCircle size={11} /> {error}
        </p>
      )}
    </div>
  );
}

function GoogleButton({ onClick, loading }: { onClick: () => void; loading: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="w-full flex items-center justify-center gap-3 py-3 rounded-[12px] border-2 border-gray-200 bg-white text-sm font-medium text-gray-700 hover:border-gray-300 hover:bg-gray-50 active:scale-[0.99] transition-all duration-150 shadow-sm disabled:opacity-60"
    >
      {loading ? <Loader2 size={16} className="animate-spin text-gray-400" /> : (
        <svg width="18" height="18" viewBox="0 0 18 18">
          <path fill="#4285F4" d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z"/>
          <path fill="#34A853" d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z"/>
          <path fill="#FBBC05" d="M3.964 10.706A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.706V4.962H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.038l3.007-2.332z"/>
          <path fill="#EA4335" d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.962L3.964 7.294C4.672 5.163 6.656 3.58 9 3.58z"/>
        </svg>
      )}
      Continue with Google
    </button>
  );
}

// ─── Owl illustration ─────────────────────────────────────────────────────────

function OwlIllustration({ mode }: { mode: Mode }) {
  const messages: Record<Mode, { headline: string; body: string }> = {
    signin:  { headline: "Welcome back!", body: "Pick up where you left off. Your notes, flashcards, and progress are all waiting." },
    signup:  { headline: "Start learning smarter.", body: "Join thousands of students using AI to study faster and score higher." },
    forgot:  { headline: "No worries!", body: "It happens to the best of us. We'll send a reset link to your inbox in seconds." },
  };
  const msg = messages[mode];

  return (
    <div className="hidden lg:flex flex-col items-center justify-center h-full gap-8 px-10 bg-gradient-to-br from-[#f0fdf4] to-[#eff6ff] rounded-r-[24px] relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-8 right-8 w-32 h-32 rounded-full bg-[#4ade80]/10" />
      <div className="absolute bottom-12 left-6 w-20 h-20 rounded-full bg-[#60a5fa]/10" />
      <div className="absolute top-1/3 right-4 w-8 h-8 rounded-full bg-[#f472b6]/10" />

      {/* Owl SVG */}
      <div className="relative">
        <div className="w-44 h-44 rounded-3xl bg-white shadow-xl shadow-[#4ade80]/20 flex items-center justify-center border border-[rgba(0,0,0,0.06)]">
          <svg width="100" height="100" viewBox="0 0 100 100" fill="none">
            {/* Body */}
            <ellipse cx="50" cy="62" rx="28" ry="30" fill="#4ade80" />
            {/* Belly */}
            <ellipse cx="50" cy="68" rx="16" ry="18" fill="#f0fdf4" />
            {/* Head */}
            <circle cx="50" cy="38" r="24" fill="#4ade80" />
            {/* Ears */}
            <polygon points="32,20 26,6 38,14" fill="#22c55e" />
            <polygon points="68,20 74,6 62,14" fill="#22c55e" />
            {/* Left eye white */}
            <circle cx="40" cy="36" r="9" fill="white" />
            {/* Right eye white */}
            <circle cx="60" cy="36" r="9" fill="white" />
            {/* Left iris */}
            <circle cx="41" cy="37" r="5.5" fill="#1e293b" />
            {/* Right iris */}
            <circle cx="61" cy="37" r="5.5" fill="#1e293b" />
            {/* Left shine */}
            <circle cx="43" cy="34.5" r="2" fill="white" />
            {/* Right shine */}
            <circle cx="63" cy="34.5" r="2" fill="white" />
            {/* Beak */}
            <polygon points="50,44 45,49 55,49" fill="#fb923c" />
            {/* Wings */}
            <ellipse cx="24" cy="62" rx="10" ry="16" fill="#22c55e" transform="rotate(-15 24 62)" />
            <ellipse cx="76" cy="62" rx="10" ry="16" fill="#22c55e" transform="rotate(15 76 62)" />
            {/* Feet */}
            <ellipse cx="40" cy="91" rx="8" ry="3.5" fill="#22c55e" />
            <ellipse cx="60" cy="91" rx="8" ry="3.5" fill="#22c55e" />
            {/* Graduation cap */}
            <rect x="32" y="16" width="36" height="5" rx="2" fill="#1e293b" />
            <polygon points="50,8 68,18 32,18" fill="#1e293b" />
            <line x1="68" y1="18" x2="72" y2="28" stroke="#1e293b" strokeWidth="2" />
            <circle cx="72" cy="30" r="3" fill="#fb923c" />
          </svg>
        </div>
        {/* Floating badges */}
        <div className="absolute -top-3 -right-3 bg-white rounded-xl px-2.5 py-1.5 shadow-lg border border-[rgba(0,0,0,0.06)] flex items-center gap-1.5">
          <span className="text-xs">🏆</span>
          <span className="text-[10px] font-semibold text-gray-700">44-day streak</span>
        </div>
        <div className="absolute -bottom-3 -left-3 bg-white rounded-xl px-2.5 py-1.5 shadow-lg border border-[rgba(0,0,0,0.06)] flex items-center gap-1.5">
          <span className="text-xs">📚</span>
          <span className="text-[10px] font-semibold text-gray-700">1,031 sessions</span>
        </div>
      </div>

      {/* Copy */}
      <div className="text-center max-w-xs relative z-10">
        <h2 className="text-gray-800 text-xl font-semibold leading-snug">{msg.headline}</h2>
        <p className="text-sm text-gray-500 mt-2 leading-relaxed">{msg.body}</p>
      </div>

      {/* Social proof */}
      <div className="flex flex-col items-center gap-2 relative z-10">
        <div className="flex -space-x-2">
          {["#4ade80", "#60a5fa", "#f472b6", "#fb923c", "#a78bfa"].map((c, i) => (
            <div key={i} className="w-7 h-7 rounded-full border-2 border-white flex items-center justify-center text-[9px] font-bold text-white" style={{ backgroundColor: c }}>
              {["JA","KM","PL","RS","TW"][i]}
            </div>
          ))}
        </div>
        <p className="text-[10px] text-gray-400">Joined by <strong className="text-gray-600">12,000+</strong> students</p>
      </div>
    </div>
  );
}

// ─── Main auth form ───────────────────────────────────────────────────────────

interface AuthPageProps {
  onLogin: () => void;
}

export function AuthPage({ onLogin }: AuthPageProps) {
  const [mode, setMode] = useState<Mode>("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [success, setSuccess] = useState(false);

  const strength = passwordStrength(password);

  const validate = () => {
    const e: Record<string, string> = {};
    if (!email) e.email = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(email)) e.email = "Enter a valid email address";
    if (mode !== "forgot") {
      if (!password) e.password = "Password is required";
      else if (mode === "signup" && password.length < 8) e.password = "Must be at least 8 characters";
    }
    if (mode === "signup" && !name) e.name = "Full name is required";
    return e;
  };

  const handleSubmit = () => {
    const e = validate();
    if (Object.keys(e).length) { setErrors(e); return; }
    setErrors({});
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      if (mode === "forgot") { setSuccess(true); return; }
      onLogin();
    }, 1400);
  };

  const handleGoogle = () => {
    setGoogleLoading(true);
    setTimeout(() => { setGoogleLoading(false); onLogin(); }, 1200);
  };

  const switchMode = (m: Mode) => {
    setMode(m);
    setErrors({});
    setSuccess(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0fdf4] via-white to-[#eff6ff] flex items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-white rounded-[24px] shadow-2xl shadow-gray-200/60 border border-[rgba(0,0,0,0.06)] overflow-hidden flex min-h-[560px]">

        {/* ── Left: Form pane ─────────────────────────────────────────────── */}
        <div className="flex-1 flex flex-col justify-center px-8 py-10 lg:px-12">
          {/* Logo */}
          <div className="flex items-center gap-2.5 mb-8">
            <div className="w-9 h-9 rounded-xl bg-[#4ade80] flex items-center justify-center shadow-sm">
              <span className="text-white text-lg">🦉</span>
            </div>
            <span className="font-bold text-gray-900 text-base tracking-tight">StudyMate AI</span>
          </div>

          {/* Heading */}
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-900">
              {mode === "signin" && "Sign in to your account"}
              {mode === "signup" && "Create your account"}
              {mode === "forgot" && "Reset your password"}
            </h1>
            <p className="text-sm text-gray-400 mt-1.5">
              {mode === "signin" && "Welcome back — your dashboard is waiting."}
              {mode === "signup" && "Free forever. No credit card required."}
              {mode === "forgot" && "Enter your email and we'll send you a reset link."}
            </p>
          </div>

          {/* Success state for forgot */}
          {success ? (
            <div className="flex flex-col items-center gap-4 py-8 text-center">
              <div className="w-14 h-14 rounded-2xl bg-[#f0fdf4] border border-[#bbf7d0] flex items-center justify-center">
                <Check size={24} className="text-[#16a34a]" />
              </div>
              <div>
                <p className="font-semibold text-gray-800">Check your inbox</p>
                <p className="text-sm text-gray-400 mt-1">We've sent a reset link to <strong className="text-gray-600">{email}</strong></p>
              </div>
              <button onClick={() => switchMode("signin")} className="text-sm text-[#16a34a] hover:underline font-medium mt-2">
                ← Back to sign in
              </button>
            </div>
          ) : (
            <>
              {/* Google button */}
              {mode !== "forgot" && (
                <>
                  <GoogleButton onClick={handleGoogle} loading={googleLoading} />
                  <div className="flex items-center gap-3 my-5">
                    <div className="flex-1 h-px bg-gray-200" />
                    <span className="text-xs text-gray-400 font-medium">or continue with email</span>
                    <div className="flex-1 h-px bg-gray-200" />
                  </div>
                </>
              )}

              {/* Form fields */}
              <div className="flex flex-col gap-4">
                {mode === "signup" && (
                  <FormInput
                    label="Full Name"
                    value={name}
                    onChange={setName}
                    placeholder="Jamie Anderson"
                    icon={User}
                    error={errors.name}
                    autoComplete="name"
                  />
                )}

                <FormInput
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={setEmail}
                  placeholder="you@university.edu"
                  icon={Mail}
                  error={errors.email}
                  autoComplete="email"
                />

                {mode !== "forgot" && (
                  <div className="flex flex-col gap-1.5">
                    <FormInput
                      label="Password"
                      type="password"
                      value={password}
                      onChange={setPassword}
                      placeholder={mode === "signup" ? "Min. 8 characters" : "Enter your password"}
                      icon={Lock}
                      error={errors.password}
                      autoComplete={mode === "signup" ? "new-password" : "current-password"}
                    />
                    {/* Password strength */}
                    {mode === "signup" && password && (
                      <div className="flex items-center gap-2 mt-0.5">
                        <div className="flex gap-1 flex-1">
                          {[1, 2, 3, 4].map((n) => (
                            <div
                              key={n}
                              className="flex-1 h-1 rounded-full transition-all duration-300"
                              style={{ backgroundColor: n <= strength.score ? strength.color : "#e5e7eb" }}
                            />
                          ))}
                        </div>
                        {strength.label && (
                          <span className="text-[10px] font-semibold" style={{ color: strength.color }}>
                            {strength.label}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Forgot password link */}
              {mode === "signin" && (
                <div className="flex justify-end mt-2">
                  <button
                    onClick={() => switchMode("forgot")}
                    className="text-xs text-gray-400 hover:text-[#16a34a] transition-colors"
                  >
                    Forgot password?
                  </button>
                </div>
              )}

              {/* Submit */}
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="mt-5 w-full flex items-center justify-center gap-2 py-3.5 rounded-[12px] bg-gray-900 text-white text-sm font-semibold hover:bg-gray-700 active:scale-[0.99] transition-all duration-150 shadow-sm hover:shadow-md disabled:opacity-60"
              >
                {loading ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <>
                    {mode === "signin" && "Sign In"}
                    {mode === "signup" && "Create Account"}
                    {mode === "forgot" && "Send Reset Link"}
                    <ArrowRight size={15} />
                  </>
                )}
              </button>

              {/* Mode switcher */}
              <p className="text-xs text-gray-400 text-center mt-5">
                {mode === "signin" ? (
                  <>Don't have an account?{" "}
                    <button onClick={() => switchMode("signup")} className="text-[#16a34a] font-semibold hover:underline">Sign Up</button>
                  </>
                ) : mode === "signup" ? (
                  <>Already have an account?{" "}
                    <button onClick={() => switchMode("signin")} className="text-[#16a34a] font-semibold hover:underline">Sign In</button>
                  </>
                ) : (
                  <>Remember it?{" "}
                    <button onClick={() => switchMode("signin")} className="text-[#16a34a] font-semibold hover:underline">Back to Sign In</button>
                  </>
                )}
              </p>

              {mode === "signup" && (
                <p className="text-[10px] text-gray-300 text-center mt-3 leading-snug">
                  By signing up, you agree to our <span className="underline cursor-pointer">Terms of Service</span> and <span className="underline cursor-pointer">Privacy Policy</span>.
                </p>
              )}
            </>
          )}
        </div>

        {/* ── Right: Illustration pane ─────────────────────────────────────── */}
        <div className="hidden lg:block w-96 shrink-0">
          <OwlIllustration mode={mode} />
        </div>
      </div>
    </div>
  );
}
