import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Search,
  Filter,
  MapPin,
  Building,
  DollarSign,
  Calendar,
  Sparkles,
  CheckCircle,
  ExternalLink,
  Tag
} from 'lucide-react';
import { fetchJobs } from '../services/api';

export default function JobCatalogView({ activeResume }) {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMode, setSelectedMode] = useState('all');
  const [locationQuery, setLocationQuery] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);

  const loadJobs = async () => {
    setLoading(true);
    const data = await fetchJobs({
      query: searchQuery,
      work_mode: selectedMode,
      location: locationQuery,
    });
    setJobs(data || []);
    if (data?.length > 0 && !selectedJob) {
      setSelectedJob(data[0]);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadJobs();
  }, [selectedMode]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadJobs();
  };

  const candidateSkills = new Set((activeResume?.skills || []).map(s => s.toLowerCase()));

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-surface-border">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-gold-400 text-xs font-mono uppercase tracking-wider mb-1">
              <Briefcase className="w-4 h-4" />
              <span>Catalog Index & Semantic Querying</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-display font-bold text-white tracking-tight">
              Job Postings Catalog
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 mt-1">
              Explore active job postings with taxonomy skill breakdowns, experience requirements, and live candidate compatibility.
            </p>
          </div>

          <div className="text-right font-mono text-xs text-gray-400">
            Total Active Postings: <span className="text-gold-400 font-bold">{jobs.length}</span>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 md:grid-cols-12 gap-3 pt-6">
          <div className="md:col-span-6 relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by title, company, or skill..."
              className="w-full bg-surface-200/90 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-gold-500/50"
            />
          </div>

          <div className="md:col-span-3">
            <select
              value={selectedMode}
              onChange={(e) => setSelectedMode(e.target.value)}
              className="w-full bg-surface-200/90 border border-white/10 rounded-xl px-3.5 py-2.5 text-xs text-gray-200 focus:outline-none focus:border-gold-500/50"
            >
              <option value="all">All Work Modes</option>
              <option value="remote">Remote Only</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">Onsite Only</option>
            </select>
          </div>

          <div className="md:col-span-3">
            <button
              type="submit"
              className="w-full py-2.5 rounded-xl bg-gold-500 text-darkbg font-bold text-xs hover:brightness-110 active:scale-95 transition-all shadow-gold-glow"
            >
              Filter Catalog
            </button>
          </div>
        </form>
      </div>

      {/* Catalog Grid + Detail Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Jobs List (Left) */}
        <div className="lg:col-span-5 space-y-3">
          {jobs.map(job => {
            const isSelected = selectedJob?.id === job.id;
            const jobSkills = job.skills || [];
            const matchedSkills = jobSkills.filter(s => candidateSkills.has(s.toLowerCase()));

            return (
              <div
                key={job.id}
                onClick={() => setSelectedJob(job)}
                className={`glass-panel p-4 rounded-xl cursor-pointer transition-all duration-200 border ${
                  isSelected
                    ? 'border-gold-500 bg-surface-200/80 shadow-gold-glow'
                    : 'border-white/5 hover:border-gold-500/30 bg-surface-100/50'
                }`}
              >
                <div className="flex items-start justify-between">
                  <h3 className="font-display font-semibold text-sm text-white line-clamp-1">
                    {job.title}
                  </h3>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-surface-200 text-gold-400 border border-gold-500/20 shrink-0 ml-2">
                    {job.work_mode}
                  </span>
                </div>

                <div className="flex items-center space-x-3 text-xs text-gray-400 mt-1">
                  <span className="text-gray-300 font-medium">{job.company}</span>
                  <span>•</span>
                  <span>{job.location || 'Remote'}</span>
                </div>

                <div className="flex items-center justify-between text-[11px] text-gray-400 mt-3 pt-2 border-t border-white/5 font-mono">
                  <span>Req. Exp: {job.required_years_experience} yrs</span>
                  <span className="text-emerald-400">
                    {matchedSkills.length}/{jobSkills.length} Skills Matched
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Job Detail Panel (Right) */}
        <div className="lg:col-span-7">
          {selectedJob ? (
            <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 space-y-6 sticky top-28">
              
              {/* Header */}
              <div className="space-y-2 border-b border-white/10 pb-6">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-gold-400 uppercase tracking-widest">
                    ID: {selectedJob.id}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full text-xs font-mono uppercase bg-surface-200 text-gray-300 border border-white/10">
                    {selectedJob.work_mode}
                  </span>
                </div>
                <h2 className="text-2xl font-display font-bold text-white">
                  {selectedJob.title}
                </h2>
                <div className="flex flex-wrap items-center gap-4 text-xs text-gray-400">
                  <span className="flex items-center space-x-1.5 text-gray-200 font-semibold">
                    <Building className="w-4 h-4 text-gold-400" />
                    <span>{selectedJob.company}</span>
                  </span>
                  <span className="flex items-center space-x-1.5">
                    <MapPin className="w-4 h-4 text-gold-400" />
                    <span>{selectedJob.location || 'Remote'}</span>
                  </span>
                  {selectedJob.salary_range && (
                    <span className="flex items-center space-x-1 text-emerald-400 font-mono">
                      <DollarSign className="w-4 h-4" />
                      <span>{selectedJob.salary_range}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <h4 className="font-display font-semibold text-sm text-gray-200">
                  Role Description
                </h4>
                <p className="text-xs text-gray-300 leading-relaxed">
                  {selectedJob.description}
                </p>
              </div>

              {/* Skills Breakdown */}
              <div className="space-y-4">
                <h4 className="font-display font-semibold text-sm text-gray-200">
                  Competency Taxonomy Mapping
                </h4>

                <div className="space-y-2">
                  <span className="text-xs font-mono text-gold-400 uppercase block">
                    All Required & Preferred Skills ({selectedJob.skills?.length || 0})
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {(selectedJob.skills || []).map((skill, idx) => {
                      const isCandidateMatched = candidateSkills.has(skill.toLowerCase());
                      return (
                        <span
                          key={idx}
                          className={`px-2.5 py-1 rounded-lg text-xs font-mono border transition-all ${
                            isCandidateMatched
                              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-sm'
                              : 'bg-surface-200 text-gray-300 border-white/5'
                          }`}
                        >
                          {skill} {isCandidateMatched && '✓'}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Candidate Alignment Meter */}
              <div className="p-4 rounded-xl bg-surface-200/50 border border-gold-500/20 space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono text-gray-300">Candidate Profile Compatibility:</span>
                  <span className="font-mono text-gold-400 font-bold">
                    {Math.round(
                      ((selectedJob.skills || []).filter(s => candidateSkills.has(s.toLowerCase())).length /
                        Math.max(1, (selectedJob.skills || []).length)) * 100
                    )}% Skill Overlap
                  </span>
                </div>
                <p className="text-[11px] text-gray-400">
                  Calculated against active profile <strong className="text-gray-200">{activeResume?.title?.split('(')[0]}</strong>.
                </p>
              </div>

            </div>
          ) : (
            <div className="glass-panel p-12 rounded-2xl text-center text-gray-500">
              Select a position to view complete requirements.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
