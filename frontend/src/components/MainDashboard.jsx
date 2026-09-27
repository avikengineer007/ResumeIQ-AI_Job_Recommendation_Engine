import React, { useState, useEffect } from 'react';
import {
  Filter,
  Bookmark,
  CheckCircle2,
  ChevronRight,
  ChevronDown,
  Flame,
  Lightbulb,
  FileEdit,
  Compass,
  BookOpen,
  ArrowRight,
  Building,
  MapPin,
  Calendar,
  Sparkles,
  RotateCcw,
  Star,
  Send,
  Heart,
  TrendingUp,
  School,
  Check,
  CheckSquare,
  Square,
  Loader2,
  ExternalLink,
  Radio
} from 'lucide-react';
import { CompanyLogo } from './CompanyLogos';
import { CandidateAvatar, HeroRobotIllustration } from './BrandIllustrations';
import { fetchLiveAdzunaJobs } from '../services/api';

export default function MainDashboard({
  currentUser,
  onSelectJob,
  onNavigate,
  savedJobIds = new Set(),
  onToggleSaveJob,
  appliedJobIds = new Set(),
  onApplyJob
}) {
  // Tab State: 'recommended' | 'live_adzuna' | 'saved' | 'applied'
  const [activeListTab, setActiveListTab] = useState('recommended');
  const [sortBy, setSortBy] = useState('Most Relevant');
  const [currentPage, setCurrentPage] = useState(1);
  const [toastMessage, setToastMessage] = useState(null);

  // Live Adzuna API Integration States
  const [liveJobs, setLiveJobs] = useState([]);
  const [liveLoading, setLiveLoading] = useState(false);
  const [liveSearchQuery, setLiveSearchQuery] = useState('Software Engineer');
  const [liveLocation, setLiveLocation] = useState('Bangalore');

  // Filter States
  const [jobTypes, setJobTypes] = useState({
    'Full-time': true,
    'Internship': true,
    'Part-time': false
  });
  const [experienceLevels, setExperienceLevels] = useState({
    'Fresher': true,
    '1–2 Years': false,
    '3+ Years': false
  });
  const [locations, setLocations] = useState({
    'Bangalore': true,
    'Hyderabad': false,
    'Pune': false,
    'Remote': false,
    'Kolkata': false
  });
  const [salaryRange, setSalaryRange] = useState('Any');
  const [showMoreLocations, setShowMoreLocations] = useState(false);

  // Primary Job Dataset precisely matching the reference screenshot
  const initialJobs = [
    {
      id: 'job-goog-sde',
      title: 'Software Development Engineer (SDE)',
      company: 'Google',
      location: 'Bangalore, India',
      jobType: 'Full-time',
      experience: '0–1 yr',
      salary: '₹ 12–18 LPA',
      matchScore: 96,
      tags: ['Java', 'DSA', 'System Design', 'Problem Solving'],
      description: 'Design and build core distributed systems, scalable services, and cloud-native solutions at Google scale.',
      applied: false
    },
    {
      id: 'job-msft-da',
      title: 'Data Analyst Intern',
      company: 'Microsoft',
      location: 'Hyderabad, India',
      jobType: 'Internship',
      experience: '3–6 months',
      salary: '₹ 45k/mo stipend',
      matchScore: 92,
      tags: ['SQL', 'Excel', 'Power BI', 'Data Visualization'],
      description: 'Analyze telemetry and user behavior across Microsoft 365, turning large datasets into actionable product insights.',
      applied: false
    },
    {
      id: 'job-amzn-ml',
      title: 'Machine Learning Intern',
      company: 'Amazon',
      location: 'Bangalore, India',
      jobType: 'Internship',
      experience: '6–9 months',
      salary: '₹ 50k/mo stipend',
      matchScore: 89,
      tags: ['Python', 'ML', 'TensorFlow', 'Data Analysis'],
      description: 'Collaborate with science teams to develop recommendation algorithms, NLP models, and computer vision pipelines.',
      applied: false
    },
    {
      id: 'job-tcs-ds',
      title: 'Data Science Trainee',
      company: 'Tata Consultancy Services (TCS)',
      location: 'Kolkata, India',
      jobType: 'Full-time',
      experience: '0–1 yr',
      salary: '₹ 6–9 LPA',
      matchScore: 87,
      tags: ['Python', 'Machine Learning', 'SQL', 'Statistics'],
      description: 'Work on predictive analytics, enterprise data modeling, and AI transformation initiatives for global clients.',
      applied: false
    },
    {
      id: 'job-acn-ba',
      title: 'Business Analyst',
      company: 'Accenture',
      location: 'Bangalore, India',
      jobType: 'Full-time',
      experience: '1–2 yrs',
      salary: '₹ 8–12 LPA',
      matchScore: 84,
      tags: ['Excel', 'SQL', 'Communication', 'Analytical Thinking'],
      description: 'Bridge business requirements and technology implementations through structured analytics and stakeholder management.',
      applied: false
    }
  ];

  const [jobs, setJobs] = useState(initialJobs);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const loadLiveJobs = async (query = liveSearchQuery, loc = liveLocation) => {
    setLiveLoading(true);
    try {
      const results = await fetchLiveAdzunaJobs(query, loc, 15);
      if (results && results.length > 0) {
        setLiveJobs(results);
        showToast(`Loaded ${results.length} live jobs from Adzuna for "${query}" in ${loc}`);
      } else {
        showToast(`No live jobs returned for "${query}". Try another query.`);
      }
    } catch (err) {
      console.error('Error fetching Adzuna jobs:', err);
      showToast('Could not reach live Adzuna feed, check connection.');
    } finally {
      setLiveLoading(false);
    }
  };

  // Pre-load live jobs from Adzuna on mount
  useEffect(() => {
    loadLiveJobs('Software Engineer', 'Bangalore');
  }, []);

  const handleResetFilters = () => {
    setJobTypes({ 'Full-time': true, 'Internship': true, 'Part-time': false });
    setExperienceLevels({ 'Fresher': true, '1–2 Years': false, '3+ Years': false });
    setLocations({ 'Bangalore': true, 'Hyderabad': false, 'Pune': false, 'Remote': false, 'Kolkata': false });
    setSalaryRange('Any');
    showToast('Filters reset to default');
  };

  const handleToggleSave = (e, job) => {
    e.stopPropagation();
    if (onToggleSaveJob) {
      onToggleSaveJob(job);
    }
    const isCurrentlySaved = savedJobIds.has(job.id);
    showToast(isCurrentlySaved ? `Removed ${job.title} from Saved` : `Saved ${job.title} to your collection!`);
  };

  const handleApply = (e, job) => {
    e.stopPropagation();
    if (job.redirect_url) {
      window.open(job.redirect_url, '_blank');
    }
    if (onApplyJob) {
      onApplyJob(job);
    }
    showToast(`Application initiated for ${job.title} at ${job.company}! 🚀`);
  };

  // Filtered jobs according to tabs
  let displayedJobs = jobs;
  if (activeListTab === 'live_adzuna') {
    displayedJobs = liveJobs;
  } else if (activeListTab === 'saved') {
    displayedJobs = jobs.filter((j) => savedJobIds.has(j.id));
  } else if (activeListTab === 'applied') {
    displayedJobs = jobs.filter((j) => appliedJobIds.has(j.id));
  }


  return (
    <div className="space-y-6 pb-12 animate-fadeIn max-w-[1600px] mx-auto">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-2xl bg-slate-900 text-white shadow-2xl flex items-center space-x-2 text-xs border border-indigo-500/40 animate-slideUp">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 1. Hero Welcome Banner */}
      <section className="relative overflow-hidden rounded-3xl bg-hero-pattern p-6 sm:p-8 border border-indigo-100/70 shadow-sm flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-3 z-10 flex-1">
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-800 font-display flex items-center gap-2">
            <span>Hello, {currentUser?.full_name ? currentUser.full_name.trim().split(' ')[0] : 'Candidate'}!</span>
            <span className="inline-block animate-wave origin-bottom-right">👋</span>
          </h2>
          <h3 className="text-sm sm:text-base font-bold text-slate-700">
            Your AI-powered career companion is here!
          </h3>
          <p className="text-xs sm:text-sm text-slate-600 max-w-xl leading-relaxed">
            Get personalized job recommendations based on your skills, interests and career goals. Build the future you want!
          </p>

          {/* Quick Skill Tags in Banner */}
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-white/90 text-indigo-700 text-xs font-semibold shadow-xs border border-indigo-100 hover:bg-white cursor-pointer transition-colors">
              <Sparkles className="w-3.5 h-3.5 text-indigo-500" />
              <span>AI/ML</span>
            </span>
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-white/90 text-indigo-700 text-xs font-semibold shadow-xs border border-indigo-100 hover:bg-white cursor-pointer transition-colors">
              <span className="text-amber-500">⚡</span>
              <span>Python</span>
            </span>
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-white/90 text-indigo-700 text-xs font-semibold shadow-xs border border-indigo-100 hover:bg-white cursor-pointer transition-colors">
              <span className="text-sky-500">🌐</span>
              <span>Web Development</span>
            </span>
            <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-white/90 text-indigo-700 text-xs font-semibold shadow-xs border border-indigo-100 hover:bg-white cursor-pointer transition-colors">
              <span className="text-purple-500">📊</span>
              <span>Data Analytics</span>
            </span>
          </div>
        </div>

        {/* Hero Banner Cute Robot & Laptop Illustration */}
        <div className="flex-shrink-0 z-10 w-full sm:w-auto flex justify-center">
          <HeroRobotIllustration className="w-64 sm:w-80 h-44 sm:h-48" />
        </div>
      </section>

      {/* 2. Main 3-Column Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ================= COLUMN 1: FILTER JOBS (2.5 of 12 cols) ================= */}
        <aside className="lg:col-span-3 space-y-6 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center space-x-2 text-slate-800 font-bold text-sm">
              <Filter className="w-4 h-4 text-indigo-600" />
              <span>Filter Jobs</span>
            </div>
            <button
              type="button"
              onClick={handleResetFilters}
              className="text-[11px] font-semibold text-slate-400 hover:text-indigo-600 transition-colors cursor-pointer"
            >
              Reset All
            </button>
          </div>

          {/* Job Type Section */}
          <div className="space-y-2.5">
            <h4 className="text-xs font-bold text-slate-700">Job Type</h4>
            <div className="space-y-2 text-xs">
              {[
                { label: 'Full-time', count: 642 },
                { label: 'Internship', count: 298 },
                { label: 'Part-time', count: 63 }
              ].map((item) => (
                <label
                  key={item.label}
                  className="flex items-center justify-between text-slate-600 hover:text-slate-900 cursor-pointer select-none group"
                >
                  <div className="flex items-center space-x-2.5">
                    <input
                      type="checkbox"
                      checked={!!jobTypes[item.label]}
                      onChange={(e) =>
                        setJobTypes({ ...jobTypes, [item.label]: e.target.checked })
                      }
                      className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 rounded cursor-pointer"
                    />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">{item.count}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Experience Level */}
          <div className="space-y-2.5 pt-2 border-t border-slate-100">
            <h4 className="text-xs font-bold text-slate-700">Experience Level</h4>
            <div className="space-y-2 text-xs">
              {[
                { label: 'Fresher', count: 512 },
                { label: '1–2 Years', count: 321 },
                { label: '3+ Years', count: 174 }
              ].map((item) => (
                <label
                  key={item.label}
                  className="flex items-center justify-between text-slate-600 hover:text-slate-900 cursor-pointer select-none group"
                >
                  <div className="flex items-center space-x-2.5">
                    <input
                      type="checkbox"
                      checked={!!experienceLevels[item.label]}
                      onChange={(e) =>
                        setExperienceLevels({ ...experienceLevels, [item.label]: e.target.checked })
                      }
                      className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 rounded cursor-pointer"
                    />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">{item.count}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Location Section */}
          <div className="space-y-2.5 pt-2 border-t border-slate-100">
            <h4 className="text-xs font-bold text-slate-700">Location</h4>
            <div className="space-y-2 text-xs">
              {[
                { label: 'Bangalore', count: 412 },
                { label: 'Hyderabad', count: 289 },
                { label: 'Pune', count: 156 },
                { label: 'Remote', count: 97 }
              ].map((item) => (
                <label
                  key={item.label}
                  className="flex items-center justify-between text-slate-600 hover:text-slate-900 cursor-pointer select-none group"
                >
                  <div className="flex items-center space-x-2.5">
                    <input
                      type="checkbox"
                      checked={!!locations[item.label]}
                      onChange={(e) =>
                        setLocations({ ...locations, [item.label]: e.target.checked })
                      }
                      className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 rounded cursor-pointer"
                    />
                    <span className="font-medium">{item.label}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">{item.count}</span>
                </label>
              ))}

              {showMoreLocations && (
                <label className="flex items-center justify-between text-slate-600 hover:text-slate-900 cursor-pointer select-none">
                  <div className="flex items-center space-x-2.5">
                    <input
                      type="checkbox"
                      checked={!!locations['Kolkata']}
                      onChange={(e) =>
                        setLocations({ ...locations, Kolkata: e.target.checked })
                      }
                      className="w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 border-slate-300 rounded cursor-pointer"
                    />
                    <span className="font-medium">Kolkata</span>
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">82</span>
                </label>
              )}

              <button
                type="button"
                onClick={() => setShowMoreLocations(!showMoreLocations)}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-800 transition-colors pt-1 block cursor-pointer"
              >
                {showMoreLocations ? '- Less' : '+ More'}
              </button>
            </div>
          </div>

          {/* Salary Range */}
          <div className="space-y-2 pt-2 border-t border-slate-100">
            <h4 className="text-xs font-bold text-slate-700">Salary Range</h4>
            <div className="relative">
              <select
                value={salaryRange}
                onChange={(e) => setSalaryRange(e.target.value)}
                className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 cursor-pointer appearance-none"
              >
                <option value="Any">Any</option>
                <option value="3-6">₹ 3–6 LPA</option>
                <option value="6-10">₹ 6–10 LPA</option>
                <option value="10-15">₹ 10–15 LPA</option>
                <option value="15+">₹ 15+ LPA</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          {/* Apply Filters Button */}
          <button
            type="button"
            onClick={() => showToast('Filters applied! Refreshing recommendations...')}
            className="w-full py-2.5 rounded-xl bg-[#3B49DF] hover:bg-[#323ec2] text-white font-semibold text-xs flex items-center justify-center space-x-2 shadow-md shadow-indigo-600/20 cursor-pointer transition-all"
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Apply Filters</span>
          </button>
        </aside>

        {/* ================= COLUMN 2: JOB RECOMMENDATIONS (6 of 12 cols) ================= */}
        <main className="lg:col-span-6 space-y-4">
          {/* Tabs bar: Recommended / Live Adzuna / Saved / Applied & Sort By */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-1">
            {/* Tab Pills */}
            <div className="flex flex-wrap items-center gap-1.5 p-1 bg-white rounded-2xl sm:rounded-full border border-slate-200/80 shadow-xs">
              <button
                type="button"
                onClick={() => setActiveListTab('recommended')}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                  activeListTab === 'recommended'
                    ? 'bg-[#3B49DF] text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Recommended <span className="text-[10px] ml-1 opacity-90">122</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setActiveListTab('live_adzuna');
                  if (liveJobs.length === 0) loadLiveJobs();
                }}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer flex items-center space-x-1.5 ${
                  activeListTab === 'live_adzuna'
                    ? 'bg-[#3B49DF] text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Live Adzuna Feed</span>
                <span className="text-[10px] ml-1 px-1.5 py-0.2 rounded-full bg-emerald-100 text-emerald-800 font-mono">
                  {liveJobs.length > 0 ? liveJobs.length : 'Live'}
                </span>
              </button>

              <button
                type="button"
                onClick={() => setActiveListTab('saved')}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                  activeListTab === 'saved'
                    ? 'bg-[#3B49DF] text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Saved <span className="text-[10px] ml-1 opacity-90">{savedJobIds.size || 8}</span>
              </button>

              <button
                type="button"
                onClick={() => setActiveListTab('applied')}
                className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                  activeListTab === 'applied'
                    ? 'bg-[#3B49DF] text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Applied <span className="text-[10px] ml-1 opacity-90">{appliedJobIds.size || 6}</span>
              </button>
            </div>

            {/* Sort by Dropdown */}
            <div className="flex items-center space-x-2 text-xs text-slate-500 self-end sm:self-auto">
              <span>Sort by:</span>
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-transparent font-semibold text-slate-700 pr-5 focus:outline-none cursor-pointer appearance-none"
                >
                  <option value="Most Relevant">Most Relevant</option>
                  <option value="Highest Match">Highest Match</option>
                  <option value="Newest">Newest</option>
                </select>
                <ChevronDown className="w-3 h-3 text-slate-500 absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>
          </div>

          {/* Adzuna Live Feed Search Bar & Status */}
          {activeListTab === 'live_adzuna' && (
            <div className="p-4 bg-gradient-to-r from-blue-50/90 to-indigo-50/90 border border-blue-200/80 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-3 shadow-xs animate-fadeIn">
              <div className="flex items-center space-x-2.5 text-xs text-indigo-950 font-medium">
                <span className="flex h-2.5 w-2.5 relative flex-shrink-0">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
                <span>
                  <strong>Adzuna Live Feed:</strong> Real-time verified postings from Adzuna API India
                </span>
              </div>
              <div className="flex items-center space-x-2 w-full md:w-auto">
                <input
                  type="text"
                  value={liveSearchQuery}
                  onChange={(e) => setLiveSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && loadLiveJobs(liveSearchQuery, liveLocation)}
                  placeholder="Role: e.g. Python, AI, React"
                  className="px-3 py-1.5 text-xs bg-white border border-indigo-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/30 w-full md:w-40 text-slate-800"
                />
                <input
                  type="text"
                  value={liveLocation}
                  onChange={(e) => setLiveLocation(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && loadLiveJobs(liveSearchQuery, liveLocation)}
                  placeholder="Location: Bangalore..."
                  className="px-3 py-1.5 text-xs bg-white border border-indigo-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/30 w-full md:w-32 text-slate-800"
                />
                <button
                  type="button"
                  onClick={() => loadLiveJobs(liveSearchQuery, liveLocation)}
                  disabled={liveLoading}
                  className="px-3.5 py-1.5 bg-[#3B49DF] text-white rounded-xl text-xs font-bold hover:bg-[#313ec0] flex items-center space-x-1.5 flex-shrink-0 cursor-pointer shadow-xs disabled:opacity-60 transition-all"
                >
                  {liveLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <span>Search</span>}
                </button>
              </div>
            </div>
          )}

          {/* Job Recommendation Cards List */}
          <div className="space-y-3.5">

            {displayedJobs.length === 0 ? (
              <div className="p-10 text-center bg-white rounded-2xl border border-slate-200 space-y-3">
                <Bookmark className="w-8 h-8 text-slate-300 mx-auto" />
                <p className="text-sm font-semibold text-slate-700">No jobs in this section</p>
                <p className="text-xs text-slate-500">
                  Switch back to Recommended to view all high-matching career opportunities.
                </p>
                <button
                  onClick={() => setActiveListTab('recommended')}
                  className="px-4 py-2 rounded-xl bg-[#3B49DF] text-white text-xs font-bold cursor-pointer"
                >
                  View Recommended Jobs
                </button>
              </div>
            ) : (
              displayedJobs.map((job) => {
                const isSaved = savedJobIds.has(job.id);
                const isApplied = appliedJobIds.has(job.id);

                return (
                  <div
                    key={job.id}
                    onClick={() => onSelectJob && onSelectJob(job)}
                    className="p-5 rounded-2xl bg-white border border-slate-200/80 hover:border-indigo-200 shadow-sm hover:shadow-md transition-all duration-200 space-y-3 cursor-pointer group"
                  >
                    {/* Top Row: Logo, Title, Match Badge, Bookmark */}
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start space-x-3.5">
                        <CompanyLogo company={job.company} className="w-11 h-11 flex-shrink-0" />
                        <div>
                          <h3 className="text-sm sm:text-base font-bold text-slate-900 group-hover:text-indigo-600 transition-colors leading-snug font-display">
                            {job.title}
                          </h3>
                          <p className="text-xs font-medium text-slate-600">
                            {job.company}
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        {/* Mint Green Match Pill */}
                        <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-600 font-extrabold text-[11px] tracking-tight">
                          {job.matchScore}% Match
                        </span>

                        {/* Bookmark Button */}
                        <button
                          type="button"
                          onClick={(e) => handleToggleSave(e, job)}
                          className={`p-1.5 rounded-lg transition-colors cursor-pointer ${
                            isSaved
                              ? 'text-indigo-600 bg-indigo-50'
                              : 'text-slate-400 hover:text-slate-700 hover:bg-slate-100'
                          }`}
                          title={isSaved ? 'Remove from Saved' : 'Save Job'}
                        >
                          <Bookmark
                            className={`w-4 h-4 ${isSaved ? 'fill-indigo-600' : ''}`}
                          />
                        </button>
                      </div>
                    </div>

                    {/* Metadata line: Location, Job Type, Experience, Salary */}
                    <div className="flex flex-wrap items-center gap-y-1 gap-x-2.5 text-xs text-slate-500 font-sans">
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        <span>{job.location}</span>
                      </span>
                      <span>•</span>
                      <span>{job.jobType}</span>
                      <span>•</span>
                      <span>{job.experience}</span>
                      {job.salary && (
                        <>
                          <span>•</span>
                          <span className="font-semibold text-slate-700">{job.salary}</span>
                        </>
                      )}
                    </div>

                      {/* Bottom Row: Skill Tags & Apply Now */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-slate-100/80">
                      <div className="flex flex-wrap items-center gap-1.5">
                        {job.tags && job.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2.5 py-0.5 rounded-md bg-sky-50 text-sky-800 text-[11px] font-medium border border-sky-100"
                          >
                            {tag}
                          </span>
                        ))}
                        {job.source && (
                          <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 text-[10px] font-semibold border border-indigo-100 flex items-center space-x-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                            <span>{job.source}</span>
                          </span>
                        )}
                      </div>

                      <button
                        type="button"
                        onClick={(e) => handleApply(e, job)}
                        disabled={isApplied}
                        className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center space-x-1.5 transition-all cursor-pointer ${
                          isApplied
                            ? 'bg-emerald-600 text-white cursor-default'
                            : 'bg-[#3B49DF] hover:bg-[#313ec0] text-white shadow-sm shadow-indigo-600/20 group-hover:shadow-md'
                        }`}
                      >
                        {isApplied ? (
                          <>
                            <Check className="w-3.5 h-3.5" />
                            <span>Applied</span>
                          </>
                        ) : (
                          <>
                            <span>{job.redirect_url ? 'Apply via Adzuna' : 'Apply Now'}</span>
                            {job.redirect_url ? (
                              <ExternalLink className="w-3.5 h-3.5" />
                            ) : (
                              <ArrowRight className="w-3.5 h-3.5" />
                            )}
                          </>
                        )}
                      </button>
                    </div>

                  </div>
                );
              })
            )}
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-center space-x-1.5 pt-4">
            <button
              type="button"
              onClick={() => setCurrentPage(1)}
              className="w-8 h-8 rounded-lg bg-[#3B49DF] text-white text-xs font-bold flex items-center justify-center shadow-xs cursor-pointer"
            >
              1
            </button>
            <button
              type="button"
              onClick={() => setCurrentPage(2)}
              className="w-8 h-8 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium flex items-center justify-center cursor-pointer"
            >
              2
            </button>
            <button
              type="button"
              onClick={() => setCurrentPage(3)}
              className="w-8 h-8 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium flex items-center justify-center cursor-pointer"
            >
              3
            </button>
            <button
              type="button"
              onClick={() => setCurrentPage(4)}
              className="w-8 h-8 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium flex items-center justify-center cursor-pointer"
            >
              4
            </button>
            <button
              type="button"
              onClick={() => setCurrentPage(5)}
              className="w-8 h-8 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium flex items-center justify-center cursor-pointer"
            >
              5
            </button>
            <button
              type="button"
              className="w-8 h-8 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-medium flex items-center justify-center cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </main>

        {/* ================= COLUMN 3: CANDIDATE PROFILE & ACTIONS (3.5 of 12 cols) ================= */}
        <aside className="lg:col-span-3 space-y-5">
          {/* Candidate Profile Summary Card */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm text-center space-y-4">
            <div className="flex flex-col items-center">
              <CandidateAvatar className="w-16 h-16" />
              <h3 className="text-base font-bold text-slate-900 mt-2 font-display">
                {currentUser?.full_name?.trim() || 'Candidate Profile'}
              </h3>
              <p className="text-xs text-slate-500 font-medium">
                {currentUser?.degree?.trim() || currentUser?.targetRole?.trim() || 'Specialization'}
              </p>
              {currentUser?.college?.trim() && (
                <div className="flex items-center space-x-1 text-slate-600 text-[11px] mt-0.5">
                  <School className="w-3.5 h-3.5 text-indigo-500 flex-shrink-0" />
                  <span className="truncate max-w-[200px]">{currentUser.college.trim()}</span>
                </div>
              )}
              <p className="text-[11px] text-emerald-600 font-semibold tracking-wide mt-1">
                Learn • Build • Grow
              </p>
            </div>


            {/* 4 Stats Grid */}
            <div className="grid grid-cols-2 gap-2.5 pt-2 border-t border-slate-100 text-left">
              {/* Stat 1 */}
              <div className="p-2.5 rounded-xl bg-slate-50/70 border border-slate-100 space-y-1">
                <div className="flex items-center space-x-1.5 text-[10px] text-slate-500 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Completed Profile</span>
                </div>
                <p className="text-sm font-extrabold text-slate-800">100%</p>
              </div>

              {/* Stat 2 */}
              <div className="p-2.5 rounded-xl bg-slate-50/70 border border-slate-100 space-y-1">
                <div className="flex items-center space-x-1.5 text-[10px] text-slate-500 font-medium">
                  <Star className="w-3.5 h-3.5 text-purple-500" />
                  <span>Skills Matched</span>
                </div>
                <p className="text-sm font-extrabold text-slate-800">8/10</p>
              </div>

              {/* Stat 3 */}
              <div className="p-2.5 rounded-xl bg-slate-50/70 border border-slate-100 space-y-1">
                <div className="flex items-center space-x-1.5 text-[10px] text-slate-500 font-medium">
                  <Send className="w-3.5 h-3.5 text-sky-500" />
                  <span>Applications</span>
                </div>
                <p className="text-sm font-extrabold text-slate-800">7</p>
              </div>

              {/* Stat 4 */}
              <div className="p-2.5 rounded-xl bg-slate-50/70 border border-slate-100 space-y-1">
                <div className="flex items-center space-x-1.5 text-[10px] text-slate-500 font-medium">
                  <Heart className="w-3.5 h-3.5 text-rose-500" />
                  <span>Saved Jobs</span>
                </div>
                <p className="text-sm font-extrabold text-slate-800">12</p>
              </div>
            </div>
          </div>

          {/* Top Skills in Demand Card */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-3.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1.5 text-slate-800 font-bold text-xs">
                <Flame className="w-4 h-4 text-orange-500 fill-orange-500" />
                <span>Top Skills in Demand</span>
              </div>
              <button
                type="button"
                onClick={() => onNavigate && onNavigate('skills')}
                className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800 flex items-center cursor-pointer"
              >
                <span>View All</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Skill list with progress bars */}
            <div className="space-y-3 text-xs">
              {[
                { rank: 1, name: 'Python', pct: 92 },
                { rank: 2, name: 'Data Analysis', pct: 88 },
                { rank: 3, name: 'Machine Learning', pct: 82 },
                { rank: 4, name: 'Java', pct: 76 },
                { rank: 5, name: 'SQL', pct: 70 }
              ].map((skill) => (
                <div key={skill.name} className="space-y-1">
                  <div className="flex items-center justify-between text-slate-700">
                    <div className="flex items-center space-x-2">
                      <span className="w-4 h-4 rounded-full bg-indigo-50 text-indigo-600 text-[10px] font-bold flex items-center justify-center">
                        {skill.rank}
                      </span>
                      <span className="font-semibold text-[11.5px]">{skill.name}</span>
                    </div>
                    <span className="text-[11px] font-mono text-slate-500">{skill.pct}%</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-slate-100 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-500"
                      style={{ width: `${skill.pct}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Pro Tip Card */}
          <div className="p-4 rounded-2xl bg-gradient-to-br from-[#E6FAF2] via-[#EAFBF7] to-[#EDF6FF] border border-teal-100/90 shadow-sm flex items-start space-x-3 group cursor-pointer">
            <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5">
              <Lightbulb className="w-4 h-4" />
            </div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-900">Pro Tip</h4>
                <ArrowRight className="w-3.5 h-3.5 text-teal-600 group-hover:translate-x-1 transition-transform" />
              </div>
              <p className="text-[11px] text-slate-600 leading-snug">
                Keep your resume updated and add real projects to improve your chances of getting hired!
              </p>
            </div>
          </div>

          {/* Quick Actions 2x2 Grid */}
          <div className="p-5 rounded-2xl bg-white border border-slate-200/80 shadow-sm space-y-3">
            <div className="flex items-center space-x-1.5 text-slate-800 font-bold text-xs">
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              <span>Quick Actions</span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-left">
              {/* Action 1 */}
              <button
                type="button"
                onClick={() => onNavigate && onNavigate('builder')}
                className="p-3 rounded-xl border border-slate-200/80 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all flex flex-col space-y-1.5 group cursor-pointer text-left"
              >
                <FileEdit className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
                <span className="text-[11px] font-bold text-slate-700 leading-tight">
                  Build / Update Resume
                </span>
              </button>

              {/* Action 2 */}
              <button
                type="button"
                onClick={() => onNavigate && onNavigate('insights')}
                className="p-3 rounded-xl border border-slate-200/80 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all flex flex-col space-y-1.5 group cursor-pointer text-left"
              >
                <Compass className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
                <span className="text-[11px] font-bold text-slate-700 leading-tight">
                  Explore Career Paths
                </span>
              </button>

              {/* Action 3 */}
              <button
                type="button"
                onClick={() => onNavigate && onNavigate('skills')}
                className="p-3 rounded-xl border border-slate-200/80 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all flex flex-col space-y-1.5 group cursor-pointer text-left"
              >
                <BookOpen className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
                <span className="text-[11px] font-bold text-slate-700 leading-tight">
                  View Learning Resources
                </span>
              </button>

              {/* Action 4 */}
              <button
                type="button"
                onClick={() => onNavigate && onNavigate('recommendations')}
                className="p-3 rounded-xl border border-slate-200/80 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all flex flex-col space-y-1.5 group cursor-pointer text-left"
              >
                <Lightbulb className="w-4 h-4 text-indigo-600 group-hover:scale-110 transition-transform" />
                <span className="text-[11px] font-bold text-slate-700 leading-tight">
                  Get AI Career Tips
                </span>
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
