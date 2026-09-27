import React, { useState } from 'react';
import {
  Sparkles,
  Search,
  FileText,
  ShieldCheck,
  Bookmark,
  Sliders,
  MessageSquare,
  Lock,
  ChevronDown,
  User,
  Home,
  CheckCircle2,
  BarChart3,
  Layers,
  Upload,
} from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  backendStatus,
  activeResume,
  currentUser,
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const screensList = [
    { id: 'landing', label: '1. Landing Hero', icon: Home },
    { id: 'auth', label: '2. Login / Register', icon: Lock },
    { id: 'upload', label: '3. Resume Upload', icon: Upload },
    { id: 'resume_analysis', label: '4. Resume Analysis', icon: FileText },
    { id: 'search', label: '5. Job Search', icon: Search },
    { id: 'filters', label: '6. Filters Control', icon: Sliders },
    { id: 'recommendation_dashboard', label: '7. Recommendations', icon: Sparkles },
    { id: 'job_details', label: '8. Job Details', icon: Layers },
    { id: 'match_explanation', label: '9. Match Explanation', icon: ShieldCheck },
    { id: 'skill_gap', label: '10. Skill Gap Analyzer', icon: BarChart3 },
    { id: 'saved_jobs', label: '11. Saved Jobs', icon: Bookmark },
    { id: 'preferences', label: '12. Preferences', icon: Sliders },
    { id: 'feedback', label: '13. Relevance Feedback', icon: MessageSquare },
  ];

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-darkbg/90 border-b border-surface-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Brand Logo */}
          <div
            className="flex items-center space-x-3 cursor-pointer"
            onClick={() => setActiveTab('landing')}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-gold-600 via-gold-400 to-amber-200 p-[1.5px] shadow-gold-glow flex items-center justify-center">
              <div className="w-full h-full bg-darkbg rounded-[9px] flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-gold-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-display font-extrabold text-xl tracking-tight text-gold-gradient">
                  ResumeIQ
                </span>
                <span className="text-[10px] uppercase font-mono tracking-widest px-2 py-0.5 rounded-full bg-gold-500/10 text-gold-400 border border-gold-500/30">
                  13-Screen
                </span>
              </div>
              <p className="text-[11px] text-gray-400 font-sans">
                Skill-Aware Recommendation Engine
              </p>
            </div>
          </div>

          {/* Primary Nav Links */}
          <nav className="hidden lg:flex items-center space-x-1 p-1 bg-surface-card rounded-2xl border border-surface-border">
            <button
              onClick={() => setActiveTab('landing')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'landing'
                  ? 'bg-gold-500 text-darkbg font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Home
            </button>

            <button
              onClick={() => setActiveTab('recommendation_dashboard')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'recommendation_dashboard'
                  ? 'bg-gold-500 text-darkbg font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Recommendations
            </button>

            <button
              onClick={() => setActiveTab('search')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'search'
                  ? 'bg-gold-500 text-darkbg font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Search
            </button>

            <button
              onClick={() => setActiveTab('upload')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'upload' || activeTab === 'resume_analysis'
                  ? 'bg-gold-500 text-darkbg font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Resume
            </button>

            <button
              onClick={() => setActiveTab('saved_jobs')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'saved_jobs'
                  ? 'bg-gold-500 text-darkbg font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Saved
            </button>

            <button
              onClick={() => setActiveTab('preferences')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'preferences'
                  ? 'bg-gold-500 text-darkbg font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Preferences
            </button>

            <button
              onClick={() => setActiveTab('feedback')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeTab === 'feedback'
                  ? 'bg-gold-500 text-darkbg font-semibold shadow-sm'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Feedback
            </button>
          </nav>

          {/* Right Action: 13-Screen Selector Dropdown & Profile */}
          <div className="flex items-center space-x-3">
            {/* Quick 13-Screen Dropdown Selector */}
            <div className="relative">
              <button
                type="button"
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="px-3 py-1.5 rounded-xl bg-surface-card hover:bg-gold-500/10 border border-gold-500/30 text-gold-300 text-xs font-mono font-medium flex items-center space-x-1.5 cursor-pointer shadow-sm"
              >
                <span>Screens ({screensList.findIndex((s) => s.id === activeTab) + 1}/13)</span>
                <ChevronDown className="w-3.5 h-3.5" />
              </button>

              {dropdownOpen && (
                <div
                  className="absolute right-0 mt-2 w-64 rounded-2xl bg-surface-card border border-surface-border shadow-2xl py-2 z-50 animate-fadeIn"
                  onClick={() => setDropdownOpen(false)}
                >
                  <div className="px-3 py-1 text-[11px] font-mono text-gray-500 uppercase tracking-wider border-b border-surface-border mb-1">
                    Select Phase 11 Screen
                  </div>
                  <div className="max-h-80 overflow-y-auto space-y-0.5 px-1">
                    {screensList.map((screen) => {
                      const Icon = screen.icon;
                      const isCurrent = activeTab === screen.id;
                      return (
                        <button
                          key={screen.id}
                          onClick={() => setActiveTab(screen.id)}
                          className={`w-full px-3 py-1.5 rounded-lg text-left text-xs flex items-center space-x-2 transition-colors cursor-pointer ${
                            isCurrent
                              ? 'bg-gold-500/20 text-gold-300 font-semibold'
                              : 'text-gray-300 hover:bg-darkbg hover:text-white'
                          }`}
                        >
                          <Icon className="w-3.5 h-3.5 text-gold-400 flex-shrink-0" />
                          <span className="truncate">{screen.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Auth / Profile Trigger */}
            <button
              onClick={() => setActiveTab('auth')}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-darkbg border border-surface-border hover:border-gold-500/40 text-xs text-gray-300 hover:text-white transition-colors cursor-pointer"
            >
              <User className="w-3.5 h-3.5 text-gold-400" />
              <span className="hidden sm:inline font-mono">
                {currentUser?.email ? currentUser.email.split('@')[0] : 'Sign In'}
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
