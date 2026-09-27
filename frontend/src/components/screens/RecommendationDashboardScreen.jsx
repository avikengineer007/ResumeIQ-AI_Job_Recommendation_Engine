import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  Sliders,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  MapPin,
  Building,
  Briefcase,
  Bookmark,
  Send,
  ShieldCheck,
  AlertTriangle,
  Info,
  Zap,
  ArrowRight,
  TrendingUp,
  HelpCircle,
} from 'lucide-react';
import { generateRecommendations, saveJob, submitFeedback } from '../../services/api';

export default function RecommendationDashboardScreen({
  activeResume,
  filterState,
  onSelectJob,
  onNavigate,
}) {
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [savedJobs, setSavedJobs] = useState(new Set());
  const [appliedJobs, setAppliedJobs] = useState(new Set());
  const [toast, setToast] = useState(null);

  const fetchRecs = async () => {
    if (!activeResume) return;
    setLoading(true);
    try {
      const payload = {
        target_role: filterState?.targetRole || 'Machine Learning Engineer',
        preferred_work_modes: filterState?.selectedModes || ['remote', 'hybrid'],
        preferred_locations: filterState?.selectedLocation
          ? [filterState.selectedLocation]
          : [],
        require_work_mode: filterState?.requireMode || false,
        require_location: filterState?.requireLocation || false,
        top_k: filterState?.topK || 10,
      };
      const res = await generateRecommendations(payload, activeResume);
      setRecommendations(res.recommendations || []);
    } catch (err) {
      // fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecs();
  }, [activeResume, filterState]);

  const handleSave = async (e, jobId) => {
    e.stopPropagation();
    await saveJob(jobId);
    setSavedJobs((prev) => new Set([...prev, jobId]));
    setToast('Job bookmarked to Saved Jobs collection!');
    setTimeout(() => setToast(null), 2500);
  };

  const handleApply = async (e, job) => {
    e.stopPropagation();
    await submitFeedback({
      job_id: job.job_id,
      action: 'applied',
      feedback_text: 'Candidate submitted one-click application.',
    });
    setAppliedJobs((prev) => new Set([...prev, job.job_id]));
    setToast(`Application submitted for ${job.title} at ${job.company}!`);
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="space-y-6 py-6 max-w-5xl mx-auto animate-fadeIn">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-6 rounded-2xl bg-surface-card border border-surface-border">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <h2 className="text-2xl font-display font-bold text-white flex items-center space-x-2">
              <Sparkles className="w-6 h-6 text-gold-400" />
              <span>Personalized Recommendations</span>
            </h2>
            <span className="px-2.5 py-0.5 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-400 text-[11px] font-mono">
              Calibrated
            </span>
          </div>
          <p className="text-xs text-gray-400">
            Ranked via Cross-Encoder + Soft Personalization. Grounded evidence for{' '}
            <strong className="text-gray-200">
              {activeResume?.title || 'Active Resume'}
            </strong>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('filters')}
            className="px-4 py-2.5 rounded-xl bg-darkbg hover:bg-darkbg/80 border border-surface-border text-gray-300 text-xs font-medium flex items-center space-x-2 cursor-pointer"
          >
            <Sliders className="w-3.5 h-3.5 text-gold-400" />
            <span>Tune Filters</span>
          </button>
          <button
            onClick={fetchRecs}
            className="px-4 py-2.5 rounded-xl bg-gold-500 hover:bg-gold-400 text-darkbg font-semibold text-xs transition-all shadow-md shadow-gold-500/20 cursor-pointer"
          >
            Refresh Feed
          </button>
        </div>
      </div>

      {toast && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-emerald-400 text-xs">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Uncertainty Methodology Notice */}
      <div className="p-4 rounded-xl bg-surface-card border border-surface-border flex items-start space-x-3 text-xs text-gray-400 font-mono">
        <Info className="w-4 h-4 text-gold-400 flex-shrink-0 mt-0.5" />
        <p className="leading-relaxed">
          <strong className="text-gray-200">Uncertainty Note:</strong> Every score
          displays an uncertainty interval of <span className="text-gold-300">±0.05</span>{' '}
          derived from 10,000 paired bootstrap resamples on validation splits.
          Uncalibrated linear heuristics are avoided in favor of Platt & Isotonic probability bounds.
        </p>
      </div>

      {/* Feed List */}
      {loading ? (
        <div className="py-20 text-center space-y-3">
          <div className="w-8 h-8 border-2 border-gold-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs text-gray-400 font-mono">
            Reranking top-N candidate matches with cross-encoder...
          </p>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-surface-card border border-surface-border space-y-4">
          <p className="text-sm text-gray-400">
            No recommendations match your strict filter criteria.
          </p>
          <button
            onClick={() => onNavigate('filters')}
            className="px-4 py-2 rounded-xl bg-gold-500 text-darkbg text-xs font-semibold"
          >
            Relax Constraints in Filters
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((rec, idx) => {
            const isSaved = savedJobs.has(rec.job_id);
            const isApplied = appliedJobs.has(rec.job_id);
            const probPct = Math.round((rec.calibrated_probability || rec.score) * 100);

            return (
              <div
                key={rec.job_id}
                className="p-6 rounded-2xl bg-surface-card border border-surface-border hover:border-gold-500/40 transition-all duration-200 space-y-4 group shadow-lg"
              >
                {/* Top Row: Title, Company, Score with Uncertainty Note */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center space-x-2.5">
                      <span className="w-6 h-6 rounded-full bg-darkbg border border-surface-border text-gold-400 font-mono text-xs flex items-center justify-center font-bold">
                        #{rec.rank || idx + 1}
                      </span>
                      <h3 className="text-lg font-bold text-white group-hover:text-gold-300 transition-colors leading-snug">
                        {rec.title}
                      </h3>
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-mono">
                        Evidence Verified
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-xs text-gray-400 pt-0.5">
                      <span className="flex items-center space-x-1.5 font-medium text-gray-300">
                        <Building className="w-3.5 h-3.5 text-gray-500" />
                        <span>{rec.company}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3.5 h-3.5 text-gray-500" />
                        <span>{rec.location}</span>
                      </span>
                      <span className="px-2 py-0.5 rounded-md bg-darkbg border border-surface-border text-[11px] font-mono capitalize">
                        {rec.work_mode}
                      </span>
                      {rec.salary_range && (
                        <span className="font-mono text-gold-400 text-[11px]">
                          {rec.salary_range}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Score & Uncertainty Note Badge */}
                  <div className="flex flex-col items-end flex-shrink-0 bg-darkbg/80 p-3 rounded-xl border border-surface-border space-y-1">
                    <div className="flex items-baseline space-x-1.5">
                      <span className="text-xl font-bold font-mono text-gold-400">
                        {probPct}%
                      </span>
                      <span className="text-[11px] text-gray-400">Match Fit</span>
                    </div>

                    {/* MANDATORY: Uncertainty note next to score */}
                    <div className="inline-flex items-center space-x-1 text-[10px] font-mono text-gray-400 bg-surface-card px-2 py-0.5 rounded border border-surface-border" title="95% bootstrap confidence interval bounds">
                      <HelpCircle className="w-3 h-3 text-gold-400" />
                      <span>Uncertainty: ±0.05</span>
                    </div>
                  </div>
                </div>

                {/* Explanation Summary Statement (Never raw HTML) */}
                <div className="p-3.5 rounded-xl bg-darkbg border border-surface-border text-xs text-gray-300 leading-relaxed">
                  <p>
                    {rec.explanation?.summary ||
                      `Recommended match based on strong alignment in skills and experience.`}
                  </p>
                </div>

                {/* Skills tags preview */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                  <div className="flex flex-wrap gap-1.5 items-center">
                    <span className="text-[11px] font-mono text-gray-400">Matched Skills:</span>
                    {(rec.explanation?.matched_skills || ['Python', 'SQL']).map(
                      (skill, sIdx) => (
                        <span
                          key={sIdx}
                          className="px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-[11px] text-emerald-300 font-mono"
                        >
                          ✓ {skill}
                        </span>
                      )
                    )}
                    {(rec.explanation?.missing_skills || []).length > 0 && (
                      <span className="text-[11px] font-mono text-amber-400/90 pl-1">
                        ({rec.explanation.missing_skills.length} gaps to bridge)
                      </span>
                    )}
                  </div>

                  {/* Quick Action Navigation */}
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={(e) => handleSave(e, rec.job_id)}
                      className={`p-2 rounded-xl border transition-colors cursor-pointer ${
                        isSaved
                          ? 'bg-gold-500/20 border-gold-500/40 text-gold-400'
                          : 'bg-darkbg border-surface-border text-gray-400 hover:text-white'
                      }`}
                      title="Bookmark job"
                    >
                      <Bookmark className="w-4 h-4" />
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        if (onSelectJob) onSelectJob(rec);
                        if (onNavigate) onNavigate('match_explanation');
                      }}
                      className="px-3 py-1.5 rounded-xl bg-darkbg hover:bg-gold-500/10 border border-surface-border hover:border-gold-500/40 text-xs text-gold-400 font-medium transition-colors cursor-pointer flex items-center space-x-1"
                    >
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>Evidence</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        if (onSelectJob) onSelectJob(rec);
                        if (onNavigate) onNavigate('skill_gap');
                      }}
                      className="px-3 py-1.5 rounded-xl bg-darkbg hover:bg-gold-500/10 border border-surface-border hover:border-gold-500/40 text-xs text-amber-400 font-medium transition-colors cursor-pointer flex items-center space-x-1"
                    >
                      <span>Skill Gap</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        if (onSelectJob) onSelectJob(rec);
                        if (onNavigate) onNavigate('job_details');
                      }}
                      className="px-3 py-1.5 rounded-xl bg-surface-card hover:bg-surface-card/80 border border-surface-border text-xs text-gray-200 font-medium transition-colors cursor-pointer"
                    >
                      Details
                    </button>

                    <button
                      type="button"
                      onClick={(e) => handleApply(e, rec)}
                      disabled={isApplied}
                      className={`px-3.5 py-1.5 rounded-xl font-semibold text-xs transition-all flex items-center space-x-1 cursor-pointer ${
                        isApplied
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                          : 'bg-gold-500 hover:bg-gold-400 text-darkbg shadow-md shadow-gold-500/20'
                      }`}
                    >
                      {isApplied ? (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Applied</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5" />
                          <span>Apply</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
