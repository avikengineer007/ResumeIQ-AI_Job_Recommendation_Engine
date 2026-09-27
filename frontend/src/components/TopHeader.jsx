import React, { useState } from 'react';
import {
  Search,
  Bell,
  Menu,
  ChevronDown,
  Layers,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  ExternalLink,
  Lock,
  User,
  ListOrdered,
  Maximize2
} from 'lucide-react';
import { CandidateAvatar } from './BrandIllustrations';

export default function TopHeader({
  activeTab,
  setActiveTab,
  searchQuery,
  setSearchQuery,
  onSearchSubmit,
  onMenuToggle,
  backendStatus,
  currentUser,
  isSequentialMode = true,
  setIsSequentialMode,
  onScrollToSection
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  const screensList = [
    { id: 'section-hero', tab: 'home', label: '1. Welcome & Recommendations' },
    { id: 'section-auth', tab: 'auth', label: '2. Login / Register (Auth)' },
    { id: 'section-upload', tab: 'upload', label: '3. Resume Upload' },
    { id: 'section-analysis', tab: 'resume_analysis', label: '4. Resume Analysis' },
    { id: 'section-recommendations', tab: 'profile', label: '5. Candidate Profile' },
    { id: 'section-evidence', tab: 'match_explanation', label: '6. Match Explanation' },
    { id: 'section-skillgap', tab: 'skills', label: '7. Skill Gap Analyzer' },
    { id: 'section-applications', tab: 'saved', label: '8. Applications & Saved' },
    { id: 'section-feedback', tab: 'settings', label: '9. Feedback & Settings' },
  ];

  const handleSelectScreen = (screen) => {
    if (isSequentialMode && onScrollToSection) {
      onScrollToSection(screen.id);
    } else {
      setActiveTab(screen.tab);
    }
    setDropdownOpen(false);
  };

  return (
    <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 py-3 transition-all">
      <div className="flex items-center justify-between gap-4 max-w-[1600px] mx-auto">
        {/* Mobile menu button */}
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-2 rounded-xl text-slate-600 hover:bg-slate-100 cursor-pointer"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search Bar */}
        <div className="flex-1 max-w-xl">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (onSearchSubmit) onSearchSubmit(searchQuery);
            }}
            className="relative"
          >
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery || ''}
              onChange={(e) => setSearchQuery && setSearchQuery(e.target.value)}
              placeholder="Search jobs, companies, skills, or job titles..."
              className="w-full pl-10 pr-4 py-2.5 rounded-full bg-slate-50 border border-slate-200 text-xs sm:text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all shadow-inner"
            />
          </form>
        </div>

        {/* Right Section: Notifications & Candidate Profile */}
        <div className="flex items-center space-x-3 sm:space-x-4">
          {/* Notifications Bell */}
          <div className="relative">
            <button
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              className="relative p-2.5 rounded-full hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
              title="Notifications"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white" />
            </button>

            {notificationsOpen && (
              <div className="absolute right-0 mt-2 w-72 bg-white rounded-2xl shadow-xl border border-slate-100 p-4 z-50 animate-fadeIn text-xs">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100 mb-2">
                  <span className="font-bold text-slate-800">Notifications</span>
                  <span className="text-[10px] text-indigo-600 font-semibold cursor-pointer">
                    Mark all read
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="p-2 rounded-xl bg-indigo-50/50 border border-indigo-100 flex items-start space-x-2">
                    <Sparkles className="w-4 h-4 text-indigo-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-slate-800 text-[11px]">
                        Google posted a new match!
                      </p>
                      <p className="text-[10px] text-slate-500">96% fit for your profile</p>
                    </div>
                  </div>
                  <div className="p-2 rounded-xl bg-emerald-50/50 border border-emerald-100 flex items-start space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-slate-800 text-[11px]">
                        Profile 100% completed
                      </p>
                      <p className="text-[10px] text-slate-500">Resume parsed & verified</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Candidate Profile Preview Pill */}
          <div
            onClick={() => setActiveTab('profile')}
            className="flex items-center space-x-2.5 pl-2 sm:pl-3 border-l border-slate-200 cursor-pointer group select-none"
          >
            <CandidateAvatar className="w-9 h-9" />
            <div className="hidden sm:block text-left leading-tight">
              <p className="text-xs font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                {currentUser?.full_name?.trim() || 'Candidate'}
              </p>
              <p className="text-[10px] text-slate-500 font-medium">
                {currentUser?.degree?.trim() || currentUser?.targetRole?.trim() || 'Profile'}
              </p>
              {currentUser?.college?.trim() && (
                <p className="text-[9.5px] text-slate-400 font-light truncate max-w-[140px]">
                  {currentUser.college.trim()}
                </p>
              )}

            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
