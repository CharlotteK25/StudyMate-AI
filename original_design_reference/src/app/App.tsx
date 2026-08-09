import { useState } from "react";
import { NavBar } from "./components/NavBar";
import { StatsCards } from "./components/StatsCards";
import { StudyProgressCard } from "./components/ProgressCard";
import { PerformanceChart } from "./components/PerformanceChart";
import { QuickActions } from "./components/QuickActions";
import { Sidebar } from "./components/Sidebar";
import { AIRecommendation } from "./components/AIRecommendation";
import { UploadNotes } from "./components/UploadNotes";
import { Flashcards } from "./components/Flashcards";
import { Quiz } from "./components/Quiz";
import { AIChat } from "./components/AIChat";
import { Profile } from "./components/Profile";
import { Analytics } from "./components/Analytics";
import { Recommendations } from "./components/Recommendations";
import { AuthPage } from "./components/AuthPage";

export default function App() {
  const [authed, setAuthed] = useState(false);
  const [activeLink, setActiveLink] = useState("Dashboard");

  if (!authed) return <AuthPage onLogin={() => setAuthed(true)} />;

  const isFullBleed = activeLink === "AI Chat";

  return (
    <div className="min-h-screen bg-[#f8fafc]">
      <NavBar activeLink={activeLink} onLinkClick={setActiveLink} />

      <main
        className={
          isFullBleed
            ? "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
            : "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col gap-6"
        }
      >
        {activeLink === "Notes" ? (
          <UploadNotes />
        ) : activeLink === "Flashcards" ? (
          <Flashcards />
        ) : activeLink === "Quiz" ? (
          <Quiz />
        ) : activeLink === "AI Chat" ? (
          <AIChat />
        ) : activeLink === "Profile" ? (
          <Profile onLogout={() => setAuthed(false)} />
        ) : activeLink === "Analytics" ? (
          <Analytics />
        ) : activeLink === "Recommendations" ? (
          <Recommendations />
        ) : (
          /* Dashboard */
          <>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-gray-900">Good morning, Carmen 👋</h1>
                <p className="text-sm text-gray-400 mt-0.5">Here's your study summary for today</p>
              </div>
              <div className="hidden sm:flex items-center gap-2 bg-white border border-[rgba(0,0,0,0.07)] rounded-xl px-4 py-2 shadow-sm">
                <div className="w-2 h-2 rounded-full bg-[#4ade80] animate-pulse" />
                <span className="text-xs text-gray-500">Friday, June 5, 2026</span>
              </div>
            </div>
            <StatsCards />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 flex flex-col gap-6">
                <StudyProgressCard />
                <PerformanceChart />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <QuickActions />
                  <AIRecommendation />
                </div>
              </div>
              <div className="lg:col-span-1">
                <Sidebar />
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
