import React from 'react';
import {
  Compass,
  Briefcase,
  FileText,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  User,
  Sliders
} from 'lucide-react';

export default function Navbar({
  activeTab,
  setActiveTab,
  backendStatus,
  activeResume,
  setActiveResume,
  allResumes
}) {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-darkbg/80 border-b border-surface-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          
          {/* Brand Logo */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('recommendations')}>
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-gold-600 via-gold-400 to-amber-200 p-[1.5px] shadow-gold-glow flex items-center justify-center">
              <div className="w-full h-full bg-darkbg rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-gold-400 animate-pulse-slow" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-display font-extrabold text-2xl tracking-tight text-gold-gradient">
                  ResumeIQ
                </span>
                <span className="text-[10px] uppercase font-mono tracking-widest px-2 py-0.5 rounded-full bg-gold-500/10 text-gold-400 border border-gold-500/30">
                  v0.1.0 Neural
                </span>
              </div>
              <p className="text-xs text-gray-400 font-sans tracking-wide">
                Skill-Aware Recommendation & Explainability Engine
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1 p-1 bg-surface-100/70 rounded-2xl border border-white/5">
            <button
              onClick={() => setActiveTab('recommendations')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'recommendations'
                  ? 'bg-gradient-to-r from-gold-600/30 to-gold-400/20 text-gold-300 border border-gold-400/30 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              <Sparkles className="w-4 h-4 text-gold-400" />
              <span>Recommendations</span>
            </button>

            <button
              onClick={() => setActiveTab('jobs')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'jobs'
                  ? 'bg-gradient-to-r from-gold-600/30 to-gold-400/20 text-gold-300 border border-gold-400/30 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              <Briefcase className="w-4 h-4 text-gold-400" />
              <span>Job Catalog</span>
            </button>

            <button
              onClick={() => setActiveTab('resume')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'resume'
                  ? 'bg-gradient-to-r from-gold-600/30 to-gold-400/20 text-gold-300 border border-gold-400/30 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              <FileText className="w-4 h-4 text-gold-400" />
              <span>Resume Studio</span>
            </button>

            <button
              onClick={() => setActiveTab('explainability')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeTab === 'explainability'
                  ? 'bg-gradient-to-r from-gold-600/30 to-gold-400/20 text-gold-300 border border-gold-400/30 shadow-sm'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              <ShieldCheck className="w-4 h-4 text-gold-400" />
              <span>Faithfulness Audit</span>
            </button>
          </nav>

          {/* Right Controls: Backend Status & Candidate Selector */}
          <div className="flex items-center space-x-3">
            {/* System Status Pill */}
            <div className="hidden sm:flex items-center space-x-2 px-3 py-1.5 rounded-full bg-surface-200/80 border border-white/10 text-xs">
              {backendStatus.online ? (
                <>
                  <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-emerald-glow"></div>
                  <span className="text-emerald-300 font-mono text-[11px]">FastAPI Live (8000)</span>
                </>
              ) : (
                <>
                  <div className="w-2 h-2 rounded-full bg-amber-400 shadow-[0_0_8px_#f59e0b]"></div>
                  <span className="text-amber-300 font-mono text-[11px]">Autonomous Sandbox</span>
                </>
              )}
            </div>

            {/* Active Candidate Selector */}
            <div className="relative">
              <div className="flex items-center space-x-2 bg-surface-100 hover:bg-surface-200 border border-gold-500/20 rounded-xl px-3 py-1.5 transition-colors">
                <div className="w-7 h-7 rounded-lg bg-gold-500/10 flex items-center justify-center text-gold-400">
                  <User className="w-4 h-4" />
                </div>
                <div className="text-left">
                  <p className="text-xs font-semibold text-gray-200 leading-tight">
                    {activeResume?.title?.split('(')[0] || 'Active Profile'}
                  </p>
                  <p className="text-[10px] text-gold-400 font-mono">
                    {activeResume?.total_years_experience || 5} yrs exp • {(activeResume?.skills || []).length} skills
                  </p>
                </div>
              </div>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
}
