import React, { useState, useEffect } from 'react';
import {
  Search,
  Sparkles,
  MapPin,
  Building,
  Briefcase,
  Bookmark,
  ArrowRight,
  Filter,
  CheckCircle2,
} from 'lucide-react';
import { fetchJobs, saveJob } from '../../services/api';

export default function SearchScreen({ activeResume, onSelectJob, onNavigate }) {
  const [query, setQuery] = useState('');
  const [workMode, setWorkMode] = useState('all');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [savedIds, setSavedIds] = useState(new Set());
  const [toast, setToast] = useState(null);

  const performSearch = async (searchTerm = query, mode = workMode) => {
    setLoading(true);
    try {
      const results = await fetchJobs({
        query: searchTerm,
        work_mode: mode === 'all' ? null : mode,
        limit: 30,
      });
      setJobs(results);
    } catch (err) {
      // handled
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    performSearch();
  }, []);

  const handleSave = async (e, jobId) => {
    e.stopPropagation();
    await saveJob(jobId);
    setSavedIds((prev) => new Set([...prev, jobId]));
    setToast('Job bookmarked to saved jobs collection!');
    setTimeout(() => setToast(null), 2500);
  };

  const quickPills = [
    'PyTorch',
    'FastAPI',
    'Computer Vision',
    'MLOps',
    'PostgreSQL',
    'Transformers',
  ];

  return (
    <div className="space-y-6 py-6 max-w-5xl mx-auto animate-fadeIn">
      {/* Search Header Bar */}
      <div className="p-6 rounded-2xl bg-surface-card border border-surface-border space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-display font-bold text-white flex items-center space-x-2">
              <Search className="w-6 h-6 text-gold-400" />
              <span>Job Search & Retrieval</span>
            </h2>
            <p className="text-xs text-gray-400">
              Hybrid BM25 keyword search fused with FAISS dense vector similarity
            </p>
          </div>
          <button
            onClick={() => onNavigate('filters')}
            className="px-3.5 py-2 rounded-xl bg-darkbg hover:bg-darkbg/80 border border-surface-border text-gray-300 text-xs font-medium flex items-center space-x-2 cursor-pointer"
          >
            <Filter className="w-3.5 h-3.5 text-gold-400" />
            <span>Advanced Filters</span>
          </button>
        </div>

        {/* Input & Mode selector */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && performSearch(query, workMode)}
              placeholder="Search by job title, skill (e.g. PyTorch), or company..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-darkbg border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500 transition-colors"
            />
          </div>

          <select
            value={workMode}
            onChange={(e) => {
              setWorkMode(e.target.value);
              performSearch(query, e.target.value);
            }}
            className="px-3 py-2.5 rounded-xl bg-darkbg border border-surface-border text-gray-300 text-xs focus:outline-none focus:border-gold-500 cursor-pointer"
          >
            <option value="all">All Work Modes</option>
            <option value="remote">Remote Only</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">Onsite</option>
          </select>

          <button
            onClick={() => performSearch(query, workMode)}
            className="px-6 py-2.5 rounded-xl bg-gold-500 hover:bg-gold-400 text-darkbg font-semibold text-xs transition-all shadow-md shadow-gold-500/20 cursor-pointer flex items-center justify-center space-x-1.5"
          >
            <span>Search</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Quick Suggestion Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] text-gray-400 font-mono">Suggested:</span>
          {quickPills.map((pill) => (
            <button
              key={pill}
              onClick={() => {
                setQuery(pill);
                performSearch(pill, workMode);
              }}
              className="px-2.5 py-1 rounded-lg bg-darkbg hover:bg-gold-500/10 border border-surface-border hover:border-gold-500/40 text-[11px] text-gray-300 hover:text-gold-300 transition-colors cursor-pointer"
            >
              {pill}
            </button>
          ))}
        </div>
      </div>

      {toast && (
        <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-emerald-400 text-xs">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-gray-400 font-mono px-1">
        <span>Found {jobs.length} postings matching search criteria</span>
        {loading && <span className="text-gold-400 animate-pulse">Querying indexes...</span>}
      </div>

      {/* Job Results List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {jobs.map((job) => {
          const isSaved = savedIds.has(job.id);
          return (
            <div
              key={job.id}
              onClick={() => {
                if (onSelectJob) onSelectJob(job);
                if (onNavigate) onNavigate('job_details');
              }}
              className="p-5 rounded-2xl bg-surface-card border border-surface-border hover:border-gold-500/40 transition-all duration-200 cursor-pointer flex flex-col justify-between space-y-4 group"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="text-base font-bold text-white group-hover:text-gold-300 transition-colors leading-snug">
                    {job.title}
                  </h3>
                  <button
                    type="button"
                    onClick={(e) => handleSave(e, job.id)}
                    className={`p-2 rounded-lg border transition-colors cursor-pointer ${
                      isSaved
                        ? 'bg-gold-500/20 border-gold-500/40 text-gold-400'
                        : 'bg-darkbg border-surface-border text-gray-400 hover:text-white'
                    }`}
                  >
                    <Bookmark className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-xs text-gray-400">
                  <span className="flex items-center space-x-1">
                    <Building className="w-3.5 h-3.5 text-gray-500" />
                    <span>{job.company}</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <MapPin className="w-3.5 h-3.5 text-gray-500" />
                    <span>{job.location}</span>
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-darkbg border border-surface-border text-[11px] font-mono capitalize">
                    {job.work_mode}
                  </span>
                </div>

                <p className="text-xs text-gray-300 line-clamp-2 leading-relaxed">
                  {job.description}
                </p>
              </div>

              {/* Skills and details trigger */}
              <div className="pt-3 border-t border-surface-border flex items-center justify-between">
                <div className="flex flex-wrap gap-1">
                  {(job.skills || []).slice(0, 3).map((s, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded bg-darkbg text-[11px] text-gray-300 font-mono"
                    >
                      {s}
                    </span>
                  ))}
                  {(job.skills || []).length > 3 && (
                    <span className="text-[11px] text-gray-500 font-mono">
                      +{job.skills.length - 3}
                    </span>
                  )}
                </div>

                <span className="text-xs text-gold-400 font-medium flex items-center space-x-1 group-hover:translate-x-0.5 transition-transform">
                  <span>View Details</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
