import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TopHeader from './components/TopHeader';
import MainDashboard from './components/MainDashboard';
import ThreeBackground from './components/ThreeBackground';

// Phase 11 & Sequential Onboarding Screens
import AuthScreen from './components/screens/AuthScreen';
import BasicDetailsScreen from './components/screens/BasicDetailsScreen';
import ProfileScreen from './components/screens/ProfileScreen';
import UploadScreen from './components/screens/UploadScreen';
import ResumeAnalysisScreen from './components/screens/ResumeAnalysisScreen';
import SearchScreen from './components/screens/SearchScreen';
import FiltersScreen from './components/screens/FiltersScreen';
import RecommendationDashboardScreen from './components/screens/RecommendationDashboardScreen';
import JobDetailsScreen from './components/screens/JobDetailsScreen';
import MatchExplanationScreen from './components/screens/MatchExplanationScreen';
import SkillGapScreen from './components/screens/SkillGapScreen';
import SavedJobsScreen from './components/screens/SavedJobsScreen';
import PreferencesScreen from './components/screens/PreferencesScreen';
import FeedbackScreen from './components/screens/FeedbackScreen';

import { MOCK_RESUMES, checkBackendHealth } from './services/api';
import { Cpu, Shield, Database, Sparkles, CheckCircle2 } from 'lucide-react';

export default function App() {
  // Website Sequence: 'auth' (Step 1: Login) -> 'basic_details' (Step 2: Details) -> 'home' (Step 3: Dashboard)
  const [activeTab, setActiveTab] = useState('auth');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeResume, setActiveResume] = useState(MOCK_RESUMES[0]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Candidate User State (Blank by default so user enters their own details)
  const [currentUser, setCurrentUser] = useState({
    id: 'u-candidate-' + Date.now().toString().slice(-4),
    email: '',
    full_name: '',
    college: '',
    degree: '',
    gradYear: '',
    cgpa: '',
    targetRole: '',
    preferredLocation: '',
    skills: [],
    is_active: true,
  });


  // Track saved and applied job IDs
  const [savedJobIds, setSavedJobIds] = useState(new Set(['job-goog-sde', 'job-amzn-ml']));
  const [appliedJobIds, setAppliedJobIds] = useState(new Set(['job-tcs-ds']));

  const [filterState, setFilterState] = useState({
    targetRole: 'Software Development Engineer',
    selectedModes: ['full-time', 'internship'],
    requireMode: false,
    selectedLocation: 'Bangalore, India',
    requireLocation: false,
    minYears: 0.0,
    topK: 10,
  });

  const [backendStatus, setBackendStatus] = useState({ online: false, data: {} });

  useEffect(() => {
    async function checkHealth() {
      const status = await checkBackendHealth();
      setBackendStatus(status);
    }
    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleSaveJob = (job) => {
    setSavedJobIds((prev) => {
      const next = new Set(prev);
      if (next.has(job.id)) {
        next.delete(job.id);
      } else {
        next.add(job.id);
      }
      return next;
    });
  };

  const handleApplyJob = (job) => {
    setAppliedJobIds((prev) => new Set([...prev, job.id]));
  };

  const handleSearchSubmit = (query) => {
    if (query && query.trim()) {
      setActiveTab('search');
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setActiveTab('auth');
  };

  // If on pure onboarding step (Step 1: Auth or Step 2: Basic Details), display dedicated focused layout
  const isOnboardingFlow = activeTab === 'auth' || activeTab === 'basic_details';

  return (
    <div className="relative min-h-screen bg-[#F4F7FC] text-slate-800 flex font-sans antialiased">
      {/* Three.js Ambient subtle constellations for tech depth */}
      <ThreeBackground />

      {/* Persistent Left Sidebar (Visible when on Dashboard & internal screens) */}
      {!isOnboardingFlow && (
        <Sidebar
          activeTab={activeTab}
          setActiveTab={(screen) => {
            setActiveTab(screen);
            setMobileMenuOpen(false);
          }}
          currentUser={currentUser}
          onLogout={handleLogout}
          isOpen={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Backdrop overlay */}
      {mobileMenuOpen && !isOnboardingFlow && (
        <div
          onClick={() => setMobileMenuOpen(false)}
          className="fixed inset-0 z-30 bg-slate-900/50 backdrop-blur-xs lg:hidden"
        />
      )}

      {/* Main Content Area */}
      <div className={`flex-1 flex flex-col min-w-0 ${!isOnboardingFlow ? 'lg:pl-64' : ''}`}>
        {/* Sticky Top Header (Visible on Dashboard & internal screens) */}
        {!isOnboardingFlow && (
          <TopHeader
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            onSearchSubmit={handleSearchSubmit}
            onMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)}
            backendStatus={backendStatus}
            currentUser={currentUser}
          />
        )}

        {/* Dynamic Main Body Content */}
        <main className={`flex-1 w-full ${!isOnboardingFlow ? 'px-4 sm:px-6 lg:px-8 py-6' : ''}`}>
          {/* STEP 1: Login / Sign In Page */}
          {activeTab === 'auth' && (
            <div className="py-6 px-4">
              <div className="max-w-4xl mx-auto flex items-center justify-between pb-4">
                <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500">
                  <span className="px-3 py-1 rounded-full bg-[#3B49DF] text-white shadow-xs font-bold">
                    Step 1 of 3: Login Portal
                  </span>
                  <span>&rarr;</span>
                  <span className="text-slate-400">Step 2: Basic Details</span>
                  <span>&rarr;</span>
                  <span className="text-slate-400">Step 3: Dashboard</span>
                </div>
                <button
                  onClick={() => setActiveTab('home')}
                  className="text-xs font-bold text-indigo-600 hover:text-indigo-800 cursor-pointer"
                >
                  Skip to Live Dashboard &rarr;
                </button>
              </div>
              <AuthScreen
                currentUser={currentUser}
                setCurrentUser={setCurrentUser}
                onNavigate={(screen) => setActiveTab(screen)}
              />
            </div>
          )}

          {/* STEP 2: Basic Details & Profile Setup */}
          {activeTab === 'basic_details' && (
            <BasicDetailsScreen
              currentUser={currentUser}
              setCurrentUser={setCurrentUser}
              onComplete={(updatedUser) => {
                setCurrentUser(updatedUser);
                setActiveTab('home');
              }}
            />
          )}

          {/* STEP 3: Home Dashboard (The full reference UI) */}
          {activeTab === 'home' && (
            <MainDashboard
              currentUser={currentUser}
              onSelectJob={(job) => {
                setSelectedJob(job);
                setActiveTab('job_details');
              }}
              onNavigate={(screen) => setActiveTab(screen)}
              savedJobIds={savedJobIds}
              onToggleSaveJob={handleToggleSaveJob}
              appliedJobIds={appliedJobIds}
              onApplyJob={handleApplyJob}
            />
          )}

          {/* 4. Candidate Profile Screen */}
          {activeTab === 'profile' && (
            <ProfileScreen
              currentUser={currentUser}
              activeResume={activeResume}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 5. Recommendations Feed / Dashboard */}
          {(activeTab === 'recommendations' || activeTab === 'recommendation_dashboard') && (
            <MainDashboard
              currentUser={currentUser}
              onSelectJob={(job) => {
                setSelectedJob(job);
                setActiveTab('job_details');
              }}
              onNavigate={(screen) => setActiveTab(screen)}
              savedJobIds={savedJobIds}
              onToggleSaveJob={handleToggleSaveJob}
              appliedJobIds={appliedJobIds}
              onApplyJob={handleApplyJob}
            />
          )}


          {/* 6. Saved Jobs Screen */}
          {(activeTab === 'saved' || activeTab === 'saved_jobs') && (
            <SavedJobsScreen
              onSelectJob={(j) => {
                setSelectedJob(j);
                setActiveTab('job_details');
              }}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 7. Applied Jobs Screen */}
          {activeTab === 'applied' && (
            <div className="space-y-6 max-w-5xl mx-auto animate-fadeIn py-4">
              <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold font-display text-slate-900">
                    My Applied Positions ({appliedJobIds.size})
                  </h2>
                  <p className="text-xs text-slate-500">
                    Track your active interview and application statuses
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('home')}
                  className="px-4 py-2 rounded-xl bg-[#3B49DF] text-white text-xs font-bold cursor-pointer"
                >
                  Explore More Jobs
                </button>
              </div>

              <div className="p-6 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-4">
                <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-wider">
                      Under Review
                    </span>
                    <h4 className="text-sm font-bold text-slate-800">
                      Data Science Trainee • Tata Consultancy Services (TCS)
                    </h4>
                    <p className="text-xs text-slate-500">Submitted 2 days ago • Match Fit: 87%</p>
                  </div>
                  <span className="px-3 py-1 rounded-full bg-amber-50 text-amber-700 text-xs font-semibold border border-amber-200">
                    Application Received
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* 8. Resume Builder & Upload */}
          {(activeTab === 'builder' || activeTab === 'upload') && (
            <UploadScreen
              onResumeLoaded={(res) => {
                setActiveResume(res);
                setActiveTab('resume_analysis');
              }}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 9. Resume Analysis Screen */}
          {activeTab === 'resume_analysis' && (
            <ResumeAnalysisScreen
              activeResume={activeResume}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 10. Career Insights & Search */}
          {(activeTab === 'insights' || activeTab === 'search') && (
            <SearchScreen
              activeResume={activeResume}
              onSelectJob={(j) => {
                setSelectedJob(j);
                setActiveTab('job_details');
              }}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 11. Filters Screen */}
          {activeTab === 'filters' && (
            <FiltersScreen
              filterState={filterState}
              setFilterState={setFilterState}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 12. Job Details Screen */}
          {activeTab === 'job_details' && (
            <JobDetailsScreen
              job={selectedJob}
              activeResume={activeResume}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 13. Match Explanation Screen */}
          {activeTab === 'match_explanation' && (
            <MatchExplanationScreen
              job={selectedJob}
              activeResume={activeResume}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 14. Skill Development / Skill Gap */}
          {(activeTab === 'skills' || activeTab === 'skill_gap') && (
            <SkillGapScreen
              job={selectedJob}
              activeResume={activeResume}
              onNavigate={(screen) => setActiveTab(screen)}
            />
          )}

          {/* 15. Preferences & Settings */}
          {(activeTab === 'settings' || activeTab === 'preferences') && (
            <PreferencesScreen onNavigate={(screen) => setActiveTab(screen)} />
          )}

          {/* 16. Feedback */}
          {activeTab === 'feedback' && (
            <FeedbackScreen onNavigate={(screen) => setActiveTab(screen)} />
          )}
        </main>

        {/* Global Footer (Visible on Dashboard & internal screens) */}
        {!isOnboardingFlow && (
          <footer className="mt-auto border-t border-slate-200/80 bg-white/80 backdrop-blur-xs py-4 px-4 sm:px-8">
            <div className="max-w-[1600px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500 font-sans">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-slate-800 font-display">ResumeIQ</span>
                <span>•</span>
                <span>AI Job Recommendation Engine</span>
                <span className="font-medium text-indigo-600">
                  {currentUser?.college || 'Candidate Career Portal'}
                </span>
              </div>

              <div className="flex items-center space-x-4 text-[11px] text-slate-400 font-mono">
                <span className="flex items-center space-x-1">
                  <Cpu className="w-3.5 h-3.5 text-indigo-500" />
                  <span>Hybrid Reranker v2.6</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Shield className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Zero-Hallucination Grounding</span>
                </span>
                <span className="flex items-center space-x-1">
                  <Database className="w-3.5 h-3.5 text-sky-500" />
                  <span>Vector Index Active</span>
                </span>
              </div>
            </div>
          </footer>
        )}
      </div>
    </div>
  );
}
