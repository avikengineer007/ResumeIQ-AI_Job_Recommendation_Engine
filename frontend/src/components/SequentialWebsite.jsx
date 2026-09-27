import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  ArrowRight,
  ArrowDown,
  CheckCircle2,
  Lock,
  Upload,
  FileText,
  Sliders,
  ShieldCheck,
  TrendingUp,
  Bookmark,
  Briefcase,
  ChevronRight,
  Compass,
  Layers,
  BarChart3,
  MessageSquare,
  Zap,
  Target
} from 'lucide-react';

import MainDashboard from './MainDashboard';
import AuthScreen from './screens/AuthScreen';
import UploadScreen from './screens/UploadScreen';
import ResumeAnalysisScreen from './screens/ResumeAnalysisScreen';
import MatchExplanationScreen from './screens/MatchExplanationScreen';
import SkillGapScreen from './screens/SkillGapScreen';
import ProfileScreen from './screens/ProfileScreen';
import SavedJobsScreen from './screens/SavedJobsScreen';
import PreferencesScreen from './screens/PreferencesScreen';
import FeedbackScreen from './screens/FeedbackScreen';

export default function SequentialWebsite({
  currentUser,
  setCurrentUser,
  activeResume,
  setActiveResume,
  selectedJob,
  setSelectedJob,
  savedJobIds,
  onToggleSaveJob,
  appliedJobIds,
  onApplyJob,
  onNavigate
}) {
  const [activeSection, setActiveSection] = useState('hero');

  const sections = [
    { id: 'section-hero', title: '1. Welcome & Engine', short: 'Hero', icon: Sparkles },
    { id: 'section-auth', title: '2. Candidate Portal', short: 'Auth', icon: Lock },
    { id: 'section-upload', title: '3. Resume Studio', short: 'Upload', icon: Upload },
    { id: 'section-analysis', title: '4. Skill Extraction', short: 'Analysis', icon: FileText },
    { id: 'section-recommendations', title: '5. Calibrated Matches', short: 'Matches', icon: Target },
    { id: 'section-evidence', title: '6. Match Evidence', short: 'Evidence', icon: ShieldCheck },
    { id: 'section-skillgap', title: '7. Skill Gap & Courses', short: 'Skill Gap', icon: TrendingUp },
    { id: 'section-applications', title: '8. Application Tracker', short: 'Applications', icon: Briefcase },
    { id: 'section-feedback', title: '9. Feedback & Settings', short: 'Feedback', icon: Sliders },
  ];

  const scrollToSection = (id) => {
    setActiveSection(id);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + 200;
      for (const section of sections) {
        const el = document.getElementById(section.id);
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            setActiveSection(section.id);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="space-y-12 pb-20">
      {/* Sticky Sequential Navigation Pill Stepper */}
      <div className="sticky top-[69px] z-20 bg-white/90 backdrop-blur-md py-2.5 px-4 rounded-2xl border border-slate-200/80 shadow-sm flex items-center justify-between gap-2 overflow-x-auto select-none">
        <div className="flex items-center space-x-1.5 flex-nowrap">
          {sections.map((sec, idx) => {
            const Icon = sec.icon;
            const isCurrent = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                onClick={() => scrollToSection(sec.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                  isCurrent
                    ? 'bg-[#3B49DF] text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isCurrent ? 'text-white' : 'text-slate-400'}`} />
                <span>{sec.title}</span>
              </button>
            );
          })}
        </div>

        <div className="hidden xl:flex items-center text-xs text-indigo-600 font-semibold px-2">
          <span>Continuous Website Journey</span>
        </div>
      </div>

      {/* ================= SECTION 1: HOME & HERO ================= */}
      <section id="section-hero" className="scroll-mt-32 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 01 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              Welcome & AI Career Companion
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Overview & Live Recommendations</span>
        </div>

        {/* Primary Dashboard with live filters & recommendations */}
        <MainDashboard
          onSelectJob={(job) => {
            setSelectedJob(job);
            scrollToSection('section-evidence');
          }}
          onNavigate={(screen) => {
            if (screen === 'upload' || screen === 'builder') scrollToSection('section-upload');
            else if (screen === 'auth') scrollToSection('section-auth');
            else if (screen === 'skills') scrollToSection('section-skillgap');
            else if (screen === 'saved' || screen === 'applied') scrollToSection('section-applications');
            else scrollToSection('section-recommendations');
          }}
          savedJobIds={savedJobIds}
          onToggleSaveJob={onToggleSaveJob}
          appliedJobIds={appliedJobIds}
          onApplyJob={onApplyJob}
        />

        {/* Next Section Flow Card */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex items-center justify-between mt-4">
          <div className="space-y-0.5">
            <p className="text-xs font-bold text-slate-800">Ready to save your candidate profile?</p>
            <p className="text-[11px] text-slate-500">Sign in to sync your verified resume and bookmarks</p>
          </div>
          <button
            onClick={() => scrollToSection('section-auth')}
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 text-xs font-bold flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            <span>Step 2: Candidate Portal</span>
            <ArrowDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ================= SECTION 2: CANDIDATE AUTH ================= */}
      <section id="section-auth" className="scroll-mt-32 space-y-4 pt-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 02 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              Candidate Portal &amp; Authentication
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Argon2id + JWT Session</span>
        </div>

        <AuthScreen
          currentUser={currentUser}
          setCurrentUser={setCurrentUser}
          onNavigate={(screen) => scrollToSection('section-upload')}
        />

        {/* Next Section Flow Card */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div className="space-y-0.5">
            <p className="text-xs font-bold text-slate-800">Account verified!</p>
            <p className="text-[11px] text-slate-500">Next, ingest your resume for zero-hallucination skill extraction</p>
          </div>
          <button
            onClick={() => scrollToSection('section-upload')}
            className="px-4 py-2 rounded-xl bg-[#3B49DF] text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm shadow-indigo-600/20 cursor-pointer"
          >
            <span>Step 3: Resume Studio</span>
            <ArrowDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ================= SECTION 3: RESUME UPLOAD ================= */}
      <section id="section-upload" className="scroll-mt-32 space-y-4 pt-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 03 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              Resume Studio &amp; Document Ingestion
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">PDF / DOCX Parsing</span>
        </div>

        <UploadScreen
          onResumeLoaded={(res) => {
            setActiveResume(res);
            scrollToSection('section-analysis');
          }}
          onNavigate={(screen) => scrollToSection('section-analysis')}
        />

        {/* Next Section Flow Card */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div className="space-y-0.5">
            <p className="text-xs font-bold text-slate-800">Document ready!</p>
            <p className="text-[11px] text-slate-500">Review the normalized skill taxonomy and PII scrubbing audit</p>
          </div>
          <button
            onClick={() => scrollToSection('section-analysis')}
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 text-xs font-bold flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            <span>Step 4: View Skill Analysis</span>
            <ArrowDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ================= SECTION 4: RESUME ANALYSIS ================= */}
      <section id="section-analysis" className="scroll-mt-32 space-y-4 pt-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 04 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              AI Resume Analysis &amp; Taxonomy Normalization
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Verified Skills &amp; Spans</span>
        </div>

        <ResumeAnalysisScreen
          activeResume={activeResume}
          onNavigate={(screen) => scrollToSection('section-recommendations')}
        />

        {/* Next Section Flow Card */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div className="space-y-0.5">
            <p className="text-xs font-bold text-slate-800">Skills extracted &amp; normalized!</p>
            <p className="text-[11px] text-slate-500">Examine how candidate skills match top tech openings with mathematical evidence</p>
          </div>
          <button
            onClick={() => scrollToSection('section-evidence')}
            className="px-4 py-2 rounded-xl bg-[#3B49DF] text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm shadow-indigo-600/20 cursor-pointer"
          >
            <span>Step 6: Match Evidence &amp; Explanation</span>
            <ArrowDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ================= SECTION 5: RECOMMENDATIONS FOCUS ================= */}
      <section id="section-recommendations" className="scroll-mt-32 space-y-4 pt-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 05 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              Candidate Profile &amp; Academic Background
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Sunrise College of Technology</span>
        </div>

        <ProfileScreen
          currentUser={currentUser}
          activeResume={activeResume}
          onNavigate={(screen) => {
            if (screen === 'builder') scrollToSection('section-upload');
            else if (screen === 'skills') scrollToSection('section-skillgap');
            else scrollToSection('section-hero');
          }}
        />
      </section>

      {/* ================= SECTION 6: MATCH EVIDENCE ================= */}
      <section id="section-evidence" className="scroll-mt-32 space-y-4 pt-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 06 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              Evidence-Grounded Match Explanation
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Zero Hallucinations Guarantee</span>
        </div>

        <MatchExplanationScreen
          job={selectedJob}
          activeResume={activeResume}
          onNavigate={(screen) => scrollToSection('section-hero')}
        />

        {/* Next Section Flow Card */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div className="space-y-0.5">
            <p className="text-xs font-bold text-slate-800">Want to bridge missing skill gaps?</p>
            <p className="text-[11px] text-slate-500">Discover personalized course recommendations to reach 100% fit</p>
          </div>
          <button
            onClick={() => scrollToSection('section-skillgap')}
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 text-xs font-bold flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            <span>Step 7: Skill Gap Analyzer</span>
            <ArrowDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ================= SECTION 7: SKILL GAP & COURSES ================= */}
      <section id="section-skillgap" className="scroll-mt-32 space-y-4 pt-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 07 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              Skill Gap Analyzer &amp; Learning Roadmap
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Targeted Upskilling</span>
        </div>

        <SkillGapScreen
          job={selectedJob}
          activeResume={activeResume}
          onNavigate={(screen) => scrollToSection('section-applications')}
        />

        {/* Next Section Flow Card */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div className="space-y-0.5">
            <p className="text-xs font-bold text-slate-800">Check active applications?</p>
            <p className="text-[11px] text-slate-500">View interview timelines and saved bookmarked positions</p>
          </div>
          <button
            onClick={() => scrollToSection('section-applications')}
            className="px-4 py-2 rounded-xl bg-[#3B49DF] text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm shadow-indigo-600/20 cursor-pointer"
          >
            <span>Step 8: Application Tracker</span>
            <ArrowDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ================= SECTION 8: APPLICATION TRACKER & SAVED JOBS ================= */}
      <section id="section-applications" className="scroll-mt-32 space-y-4 pt-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 08 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              Saved Jobs &amp; Application Status Tracker
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Pipeline Status</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Saved Jobs Card */}
          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Bookmark className="w-4 h-4 text-indigo-600" />
                <h4 className="text-sm font-bold text-slate-800">Saved Opportunities ({savedJobIds.size})</h4>
              </div>
              <span className="text-[11px] text-indigo-600 font-semibold cursor-pointer" onClick={() => scrollToSection('section-hero')}>
                Explore More &rarr;
              </span>
            </div>

            <div className="space-y-2.5">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between text-xs">
                <div>
                  <p className="font-bold text-slate-800">Software Development Engineer (SDE)</p>
                  <p className="text-[11px] text-slate-500">Google • Bangalore • 96% Match</p>
                </div>
                <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 font-bold text-[10px]">
                  Top Match
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between text-xs">
                <div>
                  <p className="font-bold text-slate-800">Machine Learning Intern</p>
                  <p className="text-[11px] text-slate-500">Amazon • Bangalore • 89% Match</p>
                </div>
                <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-bold text-[10px]">
                  Internship
                </span>
              </div>
            </div>
          </div>

          {/* Active Applications Card */}
          <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Briefcase className="w-4 h-4 text-indigo-600" />
                <h4 className="text-sm font-bold text-slate-800">Active Applications ({appliedJobIds.size})</h4>
              </div>
              <span className="text-[11px] text-emerald-600 font-semibold">1 In Review</span>
            </div>

            <div className="space-y-2.5">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 flex items-center justify-between text-xs">
                <div>
                  <p className="font-bold text-slate-800">Data Science Trainee</p>
                  <p className="text-[11px] text-slate-500">Tata Consultancy Services • Kolkata</p>
                </div>
                <span className="px-2 py-1 rounded-md bg-amber-50 text-amber-800 font-bold text-[10px] border border-amber-200">
                  Application Under Review
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Next Section Flow Card */}
        <div className="p-4 rounded-2xl bg-white border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div className="space-y-0.5">
            <p className="text-xs font-bold text-slate-800">Tune recommendation weights &amp; provide feedback?</p>
            <p className="text-[11px] text-slate-500">Adjust work modes, locations, and submit ranking feedback</p>
          </div>
          <button
            onClick={() => scrollToSection('section-feedback')}
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 text-xs font-bold flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            <span>Step 9: Feedback &amp; Calibration</span>
            <ArrowDown className="w-3.5 h-3.5" />
          </button>
        </div>
      </section>

      {/* ================= SECTION 9: PREFERENCES & FEEDBACK ================= */}
      <section id="section-feedback" className="scroll-mt-32 space-y-4 pt-6">
        <div className="flex items-center justify-between pb-2 border-b border-slate-200/70">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-md bg-indigo-50 border border-indigo-200 text-indigo-700 text-[11px] font-mono font-bold">
              STAGE 09 / 09
            </span>
            <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider font-display">
              Candidate Feedback &amp; System Calibration
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">RLHF / Re-calibration</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <PreferencesScreen onNavigate={(screen) => scrollToSection('section-hero')} />
          <FeedbackScreen onNavigate={(screen) => scrollToSection('section-hero')} />
        </div>

        {/* Back to top card */}
        <div className="p-6 rounded-2xl bg-gradient-to-r from-indigo-50 via-sky-50 to-purple-50 border border-indigo-100 text-center space-y-3">
          <h4 className="text-base font-bold text-slate-900 font-display">
            You've completed the ResumeIQ Candidate Journey! 🎉
          </h4>
          <p className="text-xs text-slate-600 max-w-lg mx-auto">
            All 9 screens operate seamlessly in continuous sequence. You can return to the top recommendations or jump between any section anytime.
          </p>
          <button
            onClick={() => scrollToSection('section-hero')}
            className="px-5 py-2.5 rounded-xl bg-[#3B49DF] text-white font-bold text-xs shadow-md shadow-indigo-600/20 cursor-pointer"
          >
            Return to Top Recommendations &uarr;
          </button>
        </div>
      </section>
    </div>
  );
}
