import React, { useState } from 'react';
import {
  Building,
  MapPin,
  Calendar,
  Briefcase,
  DollarSign,
  Bookmark,
  Send,
  ShieldCheck,
  BarChart3,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from 'lucide-react';
import { saveJob, submitFeedback } from '../../services/api';

export default function JobDetailsScreen({
  job,
  activeResume,
  onNavigate,
}) {
  const [isSaved, setIsSaved] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const [toast, setToast] = useState(null);

  if (!job) {
    return (
      <div className="py-20 text-center space-y-4">
        <p className="text-sm text-gray-400">No job selected.</p>
        <button
          onClick={() => onNavigate('search')}
          className="px-4 py-2 rounded-xl bg-gold-500 text-darkbg text-xs font-semibold"
        >
          Return to Search
        </button>
      </div>
    );
  }

  const candidateSkills = new Set(
    (activeResume?.skills || []).map((s) => s.toLowerCase())
  );
  const jobSkills = job.skills || [];

  const handleSave = async () => {
    await saveJob(job.job_id || job.id);
    setIsSaved(true);
    setToast('Job bookmarked to saved collection.');
    setTimeout(() => setToast(null), 2500);
  };

  const handleApply = async () => {
    await submitFeedback({
      job_id: job.job_id || job.id,
      action: 'applied',
      feedback_text: 'Direct application from Job Details view.',
    });
    setIsApplied(true);
    setToast('Application submitted successfully!');
    setTimeout(() => setToast(null), 2500);
  };

  return (
    <div className="space-y-6 py-6 max-w-4xl mx-auto animate-fadeIn">
      {/* Back navigation */}
      <button
        onClick={() => onNavigate('recommendation_dashboard')}
        className="inline-flex items-center space-x-1.5 text-xs text-gray-400 hover:text-white transition-colors cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Recommendations</span>
      </button>

      {toast && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-emerald-400 text-xs">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Hero Overview Card */}
      <div className="p-8 rounded-2xl bg-surface-card border border-surface-border space-y-6 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-3xl font-display font-bold text-white leading-tight">
              {job.title}
            </h2>
            <div className="flex flex-wrap items-center gap-4 text-xs text-gray-300">
              <span className="flex items-center space-x-1 font-medium">
                <Building className="w-4 h-4 text-gold-400" />
                <span>{job.company}</span>
              </span>
              <span className="flex items-center space-x-1">
                <MapPin className="w-4 h-4 text-gray-500" />
                <span>{job.location}</span>
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-darkbg border border-surface-border font-mono capitalize">
                {job.work_mode}
              </span>
              {job.salary_range && (
                <span className="font-mono text-gold-400 font-semibold">
                  {job.salary_range}
                </span>
              )}
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleSave}
              className={`p-3 rounded-xl border transition-colors cursor-pointer ${
                isSaved
                  ? 'bg-gold-500/20 border-gold-500/50 text-gold-400'
                  : 'bg-darkbg border-surface-border text-gray-400 hover:text-white'
              }`}
            >
              <Bookmark className="w-5 h-5" />
            </button>

            <button
              onClick={handleApply}
              disabled={isApplied}
              className={`px-6 py-3 rounded-xl font-semibold text-xs transition-all shadow-md cursor-pointer flex items-center space-x-2 ${
                isApplied
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                  : 'bg-gold-500 hover:bg-gold-400 text-darkbg shadow-gold-500/20'
              }`}
            >
              {isApplied ? (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Application Sent</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Apply Now</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Deep Dive Action Bar */}
        <div className="p-4 rounded-xl bg-darkbg border border-surface-border flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-2 text-xs text-gray-300">
            <Sparkles className="w-4 h-4 text-gold-400" />
            <span>AI Recommendation Diagnostics:</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate('match_explanation')}
              className="px-3.5 py-1.5 rounded-lg bg-surface-card hover:bg-gold-500/10 border border-surface-border hover:border-gold-500/40 text-xs text-gold-300 font-medium transition-colors cursor-pointer flex items-center space-x-1.5"
            >
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Zero-Hallucination Evidence</span>
            </button>

            <button
              onClick={() => onNavigate('skill_gap')}
              className="px-3.5 py-1.5 rounded-lg bg-surface-card hover:bg-gold-500/10 border border-surface-border hover:border-gold-500/40 text-xs text-amber-300 font-medium transition-colors cursor-pointer flex items-center space-x-1.5"
            >
              <BarChart3 className="w-4 h-4 text-amber-400" />
              <span>Skill Gap Roadmap</span>
            </button>
          </div>
        </div>
      </div>

      {/* Skills Coverage Matrix */}
      <div className="p-6 rounded-2xl bg-surface-card border border-surface-border space-y-4">
        <h3 className="text-sm font-bold text-white font-display uppercase tracking-wider font-mono">
          Required Competencies & Candidate Match
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {jobSkills.map((s, i) => {
            const hasSkill = candidateSkills.has(s.toLowerCase());
            return (
              <div
                key={i}
                className={`p-3 rounded-xl border flex items-center justify-between text-xs font-mono ${
                  hasSkill
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-darkbg border-surface-border text-gray-400'
                }`}
              >
                <span>{s}</span>
                {hasSkill ? (
                  <span className="flex items-center space-x-1 text-emerald-400 font-semibold">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Candidate Verified</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-1 text-amber-400/80">
                    <AlertCircle className="w-4 h-4" />
                    <span>Skill Gap</span>
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Description Section */}
      <div className="p-8 rounded-2xl bg-surface-card border border-surface-border space-y-4">
        <h3 className="text-sm font-bold text-white font-display uppercase tracking-wider font-mono">
          Full Job Description & Responsibilities
        </h3>
        <div className="text-xs text-gray-300 leading-relaxed space-y-3 font-sans whitespace-pre-line">
          {job.description ||
            `We are looking for a talent to join our high-growth engineering organization. The ideal candidate has experience building robust, scalable software, designing clean API contracts, and collaborating with cross-functional teams.`}
        </div>
      </div>
    </div>
  );
}
