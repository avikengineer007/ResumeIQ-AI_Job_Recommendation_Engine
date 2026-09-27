import React from 'react';
import {
  Home,
  User,
  Sparkles,
  Bookmark,
  Briefcase,
  FileText,
  TrendingUp,
  GraduationCap,
  Settings,
  LogOut,
  LogIn,
  X
} from 'lucide-react';
import { ResumeIQLogo } from './CompanyLogos';
import { SidebarCareerCard } from './BrandIllustrations';

export default function Sidebar({
  activeTab,
  setActiveTab,
  currentUser,
  onLogout,
  isOpen = true,
  onClose,
  isSequentialMode = true,
  onScrollToSection
}) {
  const navItems = [
    { id: 'home', sectionId: 'section-hero', label: 'Home', icon: Home },
    { id: 'profile', sectionId: 'section-recommendations', label: 'My Profile', icon: User },
    { id: 'recommendations', sectionId: 'section-hero', label: 'Job Recommendations', icon: Sparkles },
    { id: 'saved', sectionId: 'section-applications', label: 'Saved Jobs', icon: Bookmark },
    { id: 'applied', sectionId: 'section-applications', label: 'Applied Jobs', icon: Briefcase },
    { id: 'builder', sectionId: 'section-upload', label: 'Resume Builder', icon: FileText },
    { id: 'insights', sectionId: 'section-evidence', label: 'Career Insights', icon: TrendingUp },
    { id: 'skills', sectionId: 'section-skillgap', label: 'Skill Development', icon: GraduationCap },
    { id: 'settings', sectionId: 'section-feedback', label: 'Settings', icon: Settings },
  ];

  const handleItemClick = (item) => {
    setActiveTab(item.id);
    if (onClose) onClose();
  };

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 w-64 bg-[#0B112C] text-slate-300 flex flex-col border-r border-[#192248] transition-transform duration-300 ease-in-out lg:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      {/* Top Header Logo */}
      <div className="p-5 flex items-center justify-between border-b border-[#151D3F]">
        <div
          className="flex items-center space-x-3 cursor-pointer group"
          onClick={() => setActiveTab('home')}
        >
          <ResumeIQLogo className="w-9 h-9 flex-shrink-0" />
          <div className="leading-tight">
            <h1 className="text-xl font-bold tracking-tight text-white group-hover:text-cyan-300 transition-colors font-display">
              ResumeIQ
            </h1>
            <p className="text-[10.5px] text-slate-400 font-sans tracking-tight">
              AI Job Recommendation Engine
            </p>
          </div>
        </div>

        {/* Mobile close button */}
        {onClose && (
          <button
            onClick={onClose}
            className="lg:hidden p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Nav List */}
      <div className="flex-1 overflow-y-auto sidebar-scroll px-3 py-4 space-y-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            activeTab === item.id ||
            (item.id === 'home' && (activeTab === 'home' || activeTab === 'landing')) ||
            (item.id === 'recommendations' && (activeTab === 'recommendation_dashboard' || activeTab === 'recommendations')) ||
            (item.id === 'saved' && activeTab === 'saved_jobs') ||
            (item.id === 'builder' && (activeTab === 'upload' || activeTab === 'resume_analysis')) ||
            (item.id === 'skills' && activeTab === 'skill_gap') ||
            (item.id === 'settings' && activeTab === 'preferences');

          return (
            <button
              key={item.id}
              onClick={() => handleItemClick(item)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                isActive
                  ? 'bg-[#3B49DF] text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-[#131B3B]'
              }`}
            >
              <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span className="truncate">{item.label}</span>
            </button>
          );
        })}

        {/* Sidebar Career Banner Card */}
        <div className="pt-4">
          <SidebarCareerCard onNavigate={(s) => setActiveTab(s || 'recommendations')} />
        </div>

        {/* Motivational Quote */}
        <div className="pt-3 px-2 text-center select-none">
          <span className="text-xl text-purple-400/80 font-serif leading-none block">“</span>
          <p className="text-[11px] italic text-slate-400 leading-snug">
            Small steps every day lead to big dreams.
          </p>
          <span className="inline-block text-xs mt-1 text-purple-400">💜</span>
        </div>
      </div>

      {/* Footer User / Auth Section */}
      <div className="p-3 border-t border-[#151D3F] bg-[#080D21]/70">
        {currentUser ? (
          <div className="flex items-center justify-between px-2 py-1.5">
            <div
              className="flex items-center space-x-2 cursor-pointer flex-1 min-w-0"
              onClick={() => setActiveTab('profile')}
            >
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-xs font-bold text-indigo-300">
                {currentUser.full_name ? currentUser.full_name[0] : 'C'}
              </div>
              <div className="truncate">
                <p className="text-xs font-semibold text-white truncate">
                  {currentUser.full_name || 'Candidate'}
                </p>
                <p className="text-[10px] text-slate-400 truncate">
                  {currentUser.email || 'candidate@sunrise.edu.in'}
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                if (onLogout) onLogout();
                setActiveTab('auth');
              }}
              title="Sign Out / Switch"
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-rose-400 cursor-pointer transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <button
            onClick={() => setActiveTab('auth')}
            className="w-full py-2 px-3 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-300 text-xs font-semibold flex items-center justify-center space-x-2 cursor-pointer"
          >
            <LogIn className="w-4 h-4" />
            <span>Sign In / Register</span>
          </button>
        )}
      </div>
    </aside>
  );
}
