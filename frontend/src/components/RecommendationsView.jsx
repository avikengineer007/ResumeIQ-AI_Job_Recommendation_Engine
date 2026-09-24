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
  Clock,
  DollarSign,
  ThumbsUp,
  ThumbsDown,
  Bookmark,
  Send,
  ShieldCheck,
  AlertTriangle,
  Info,
  Check,
  Zap,
  TrendingUp,
  BookOpen
} from 'lucide-react';
import { generateRecommendations, submitFeedback } from '../services/api';

export default function RecommendationsView({ activeResume }) {
  // Preference state
  const [targetRole, setTargetRole] = useState("Machine Learning Engineer");
  const [selectedModes, setSelectedModes] = useState(["remote", "hybrid"]);
  const [requireMode, setRequireMode] = useState(false);
  const [requireLocation, setRequireLocation] = useState(false);
  const [topK, setTopK] = useState(10);
  const [selectedLocation, setSelectedLocation] = useState("San Francisco, CA");

  // Recommendation items & status
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [expandedId, setExpandedId] = useState(null);
  const [savedJobs, setSavedJobs] = useState(new Set());
  const [appliedJobs, setAppliedJobs] = useState(new Set());
  const [feedbackRecords, setFeedbackRecords] = useState({});
  const [toastMessage, setToastMessage] = useState(null);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const handleFetchRecommendations = async () => {
    setLoading(true);
    const payload = {
      target_role: targetRole,
      preferred_work_modes: selectedModes,
      preferred_locations: selectedLocation ? [selectedLocation] : [],
      require_work_mode: requireMode,
      require_location: requireLocation,
      top_k: topK
    };

    const res = await generateRecommendations(payload, activeResume);
    setRecommendations(res.recommendations || []);
    if (res.recommendations?.length > 0) {
      setExpandedId(res.recommendations[0].job_id);
    }
    setLoading(false);
  };

  useEffect(() => {
    handleFetchRecommendations();
  }, [activeResume]);

  const toggleWorkMode = (mode) => {
    setSelectedModes(prev =>
      prev.includes(mode) ? prev.filter(m => m !== mode) : [...prev, mode]
    );
  };

  const handleApply = async (job) => {
    setAppliedJobs(prev => new Set(prev).add(job.job_id));
    await submitFeedback({
      job_id: job.job_id,
      action: 'applied',
      feedback_text: 'One-click application submitted through recommendations feed.'
    });
    showToast(`Application successfully submitted for ${job.title}!`);
  };

  const handleSave = async (job) => {
    const isSaved = savedJobs.has(job.job_id);
    setSavedJobs(prev => {
      const next = new Set(prev);
      if (isSaved) next.delete(job.job_id);
      else next.add(job.job_id);
      return next;
    });

    await submitFeedback({
      job_id: job.job_id,
      action: isSaved ? 'unsaved' : 'saved'
    });
    showToast(isSaved ? `Removed ${job.title} from saved jobs.` : `Saved ${job.title} to your bookmarks!`);
  };

  const handleRating = async (jobId, action) => {
    setFeedbackRecords(prev => ({ ...prev, [jobId]: action }));
    await submitFeedback({
      job_id: jobId,
      action: action
    });
    showToast(`Feedback recorded: marked as ${action === 'thumbs_up' ? 'relevant' : 'less relevant'}.`);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center space-x-3 px-5 py-3.5 rounded-2xl bg-surface-100 border border-gold-500/50 shadow-gold-glow text-white text-sm">
          <CheckCircle2 className="w-5 h-5 text-gold-400" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Control Panel: Candidate Preferences & Constraints */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-surface-border space-y-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-gold-400 text-xs font-mono uppercase tracking-wider mb-1">
              <Sparkles className="w-4 h-4 text-gold-400" />
              <span>Phase 10 & 11 Two-Stage Recommendation Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-display font-bold text-white tracking-tight">
              Personalized Recommendations
            </h1>
            <p className="text-xs sm:text-sm text-gray-400 mt-1">
              Hybrid dense & lexical retrieval, Cross-Encoder reranking, and Platt/Isotonic calibrated matching against <span className="text-gold-300 font-semibold">{activeResume?.title?.split('(')[0]}</span>.
            </p>
          </div>

          <button
            onClick={handleFetchRecommendations}
            disabled={loading}
            className="flex items-center justify-center space-x-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-gold-500 via-gold-400 to-amber-300 text-darkbg font-bold text-sm tracking-wide shadow-gold-glow hover:brightness-110 active:scale-95 transition-all disabled:opacity-50"
          >
            <Zap className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Re-Ranking Jobs...' : 'Update Recommendations'}</span>
          </button>
        </div>

        {/* Filter Controls Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2 border-t border-white/5">
          {/* Target Role */}
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-1.5 uppercase tracking-wider">
              Target Role Query
            </label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full bg-surface-200/90 border border-white/10 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-gold-500/50"
              placeholder="e.g. Staff ML Engineer"
            />
          </div>

          {/* Location Preference */}
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-1.5 uppercase tracking-wider">
              Preferred Location
            </label>
            <input
              type="text"
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="w-full bg-surface-200/90 border border-white/10 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-gold-500/50"
              placeholder="e.g. San Francisco, CA or Remote"
            />
          </div>

          {/* Work Mode Multi-select */}
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-1.5 uppercase tracking-wider">
              Work Mode Preference
            </label>
            <div className="flex space-x-1.5">
              {['remote', 'hybrid', 'onsite'].map(mode => {
                const isSelected = selectedModes.includes(mode);
                return (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => toggleWorkMode(mode)}
                    className={`flex-1 py-2 text-[11px] font-medium rounded-xl capitalize transition-all border ${
                      isSelected
                        ? 'bg-gold-500/20 text-gold-300 border-gold-500/50 font-semibold'
                        : 'bg-surface-200/50 text-gray-400 border-white/5 hover:text-white'
                    }`}
                  >
                    {mode}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Hard Constraints */}
          <div>
            <label className="block text-xs font-mono text-gray-400 mb-1.5 uppercase tracking-wider">
              Hard Constraints
            </label>
            <div className="space-y-1.5 pt-0.5">
              <label className="flex items-center space-x-2 text-xs text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={requireMode}
                  onChange={(e) => setRequireMode(e.target.checked)}
                  className="rounded bg-surface-200 border-white/20 text-gold-500 focus:ring-0"
                />
                <span>Strict Work Mode Match</span>
              </label>
              <label className="flex items-center space-x-2 text-xs text-gray-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={requireLocation}
                  onChange={(e) => setRequireLocation(e.target.checked)}
                  className="rounded bg-surface-200 border-white/20 text-gold-500 focus:ring-0"
                />
                <span>Strict Location Filter</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Results Count & Model Version Banner */}
      <div className="flex items-center justify-between text-xs text-gray-400 px-2 font-mono">
        <div>
          Showing <span className="text-gold-400 font-bold">{recommendations.length}</span> top recommendations
        </div>
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Section 11 Grounded Verification & Zero Fabrication</span>
        </div>
      </div>

      {/* Recommendations Feed */}
      <div className="space-y-4">
        {recommendations.length === 0 ? (
          <div className="glass-panel rounded-3xl p-12 text-center space-y-4 border border-white/10">
            <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto" />
            <h3 className="text-xl font-display font-semibold text-white">No Matching Roles Found</h3>
            <p className="text-sm text-gray-400 max-w-md mx-auto">
              Your strict hard constraints filtered out all candidate positions. Try relaxing strict work mode or location filters.
            </p>
          </div>
        ) : (
          recommendations.map((rec) => {
            const isExpanded = expandedId === rec.job_id;
            const isSaved = savedJobs.has(rec.job_id);
            const isApplied = appliedJobs.has(rec.job_id);
            const feedback = feedbackRecords[rec.job_id];
            const probPercent = Math.round((rec.calibrated_probability || rec.score) * 100);

            return (
              <div
                key={rec.job_id}
                className={`glass-panel rounded-2xl border transition-all duration-300 ${
                  isExpanded
                    ? 'border-gold-500/50 bg-surface-100/90 shadow-gold-glow'
                    : 'border-white/10 hover:border-gold-500/30 bg-surface-100/50'
                }`}
              >
                {/* Header Card Summary */}
                <div className="p-6 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
                  
                  {/* Left: Job Info & Match Probability Badge */}
                  <div className="flex items-start space-x-4 flex-1">
                    {/* Calibrated Probability Radial / Pill */}
                    <div className="flex flex-col items-center justify-center w-16 h-16 rounded-2xl bg-darkbg border border-gold-500/40 p-2 text-center shadow-gold-glow shrink-0">
                      <span className="font-display font-extrabold text-lg text-gold-gradient leading-none">
                        {probPercent}%
                      </span>
                      <span className="text-[9px] uppercase font-mono tracking-tighter text-gray-400 mt-1">
                        Calibrated
                      </span>
                    </div>

                    <div className="space-y-1.5 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded-md bg-gold-500/10 text-gold-400 border border-gold-500/30">
                          Rank #{rec.rank}
                        </span>
                        <h2 className="text-lg font-display font-bold text-white tracking-tight">
                          {rec.title}
                        </h2>
                      </div>

                      <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs text-gray-400 font-sans">
                        <span className="flex items-center space-x-1.5 text-gray-300">
                          <Building className="w-3.5 h-3.5 text-gold-400" />
                          <span>{rec.company}</span>
                        </span>
                        <span className="flex items-center space-x-1.5">
                          <MapPin className="w-3.5 h-3.5 text-gold-400" />
                          <span>{rec.location || 'Remote'}</span>
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[11px] uppercase font-mono tracking-wider bg-surface-200 text-gray-300 border border-white/5">
                          {rec.work_mode}
                        </span>
                        {rec.salary_range && (
                          <span className="flex items-center space-x-1 text-emerald-400 font-mono">
                            <DollarSign className="w-3.5 h-3.5" />
                            <span>{rec.salary_range}</span>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Actions */}
                  <div className="flex items-center space-x-2 self-stretch lg:self-auto justify-end">
                    {/* Thumbs Up / Down */}
                    <button
                      onClick={() => handleRating(rec.job_id, 'thumbs_up')}
                      className={`p-2 rounded-xl border transition-colors ${
                        feedback === 'thumbs_up'
                          ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                          : 'bg-surface-200/50 border-white/5 text-gray-400 hover:text-white hover:bg-surface-200'
                      }`}
                      title="Relevant match"
                    >
                      <ThumbsUp className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleRating(rec.job_id, 'thumbs_down')}
                      className={`p-2 rounded-xl border transition-colors ${
                        feedback === 'thumbs_down'
                          ? 'bg-red-500/20 border-red-500 text-red-400'
                          : 'bg-surface-200/50 border-white/5 text-gray-400 hover:text-white hover:bg-surface-200'
                      }`}
                      title="Irrelevant or misaligned"
                    >
                      <ThumbsDown className="w-4 h-4" />
                    </button>

                    {/* Bookmark Save */}
                    <button
                      onClick={() => handleSave(rec)}
                      className={`p-2 rounded-xl border transition-colors ${
                        isSaved
                          ? 'bg-gold-500/20 border-gold-500 text-gold-300'
                          : 'bg-surface-200/50 border-white/5 text-gray-400 hover:text-white hover:bg-surface-200'
                      }`}
                      title={isSaved ? "Saved" : "Save job"}
                    >
                      <Bookmark className="w-4 h-4" />
                    </button>

                    {/* Apply Button */}
                    <button
                      onClick={() => handleApply(rec)}
                      disabled={isApplied}
                      className={`flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                        isApplied
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 cursor-default'
                          : 'bg-gold-500 text-darkbg hover:brightness-110 shadow-gold-glow active:scale-95'
                      }`}
                    >
                      {isApplied ? (
                        <>
                          <Check className="w-3.5 h-3.5" />
                          <span>Applied</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5" />
                          <span>1-Click Apply</span>
                        </>
                      )}
                    </button>

                    {/* Expand Accordion Toggle */}
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : rec.job_id)}
                      className="p-2 rounded-xl bg-surface-200/50 border border-white/5 text-gray-400 hover:text-white transition-colors"
                      title="Toggle Explainability Breakdown"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-gold-400" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>

                </div>

                {/* Evidence-Grounded Explainability Drawer */}
                {isExpanded && rec.explanation && (
                  <div className="border-t border-white/10 p-6 bg-darkbg/50 rounded-b-2xl space-y-6 animate-fadeIn">
                    
                    {/* Rationale Summary */}
                    <div className="p-4 rounded-xl bg-surface-200/60 border border-gold-500/20 flex items-start space-x-3">
                      <ShieldCheck className="w-5 h-5 text-gold-400 shrink-0 mt-0.5" />
                      <div>
                        <span className="text-xs font-mono font-semibold text-gold-400 uppercase tracking-wider block">
                          Evidence-Grounded Rationale
                        </span>
                        <p className="text-sm text-gray-200 mt-1 leading-relaxed">
                          {rec.explanation.summary}
                        </p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      
                      {/* Left: Matched Skills & Identified Gaps */}
                      <div className="space-y-4">
                        {/* Matched Skills */}
                        <div className="space-y-2">
                          <span className="text-xs font-mono text-emerald-400 uppercase tracking-wider flex items-center space-x-1.5">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Direct Matched Competencies ({rec.explanation.matched_skills?.length || 0})</span>
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {rec.explanation.matched_skills?.map((skill, sIdx) => (
                              <span
                                key={sIdx}
                                className="px-2.5 py-1 rounded-lg text-xs font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/30"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Honest Skill Gaps (Section 11 Transparency) */}
                        {rec.explanation.missing_skills?.length > 0 && (
                          <div className="space-y-2 pt-2">
                            <span className="text-xs font-mono text-amber-400 uppercase tracking-wider flex items-center space-x-1.5">
                              <BookOpen className="w-3.5 h-3.5" />
                              <span>Identified Skill Gaps ({rec.explanation.missing_skills?.length})</span>
                            </span>
                            <div className="flex flex-wrap gap-1.5">
                              {rec.explanation.missing_skills?.map((gap, gIdx) => (
                                <span
                                  key={gIdx}
                                  className="px-2.5 py-1 rounded-lg text-xs font-mono bg-amber-500/10 text-amber-300 border border-amber-500/30"
                                >
                                  {gap}
                                </span>
                              ))}
                            </div>
                            <p className="text-[11px] text-gray-400 italic">
                              Recommendation: Demonstrating familiarity with these auxiliary tools can further maximize interview conversion.
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Right: Experience Alignment & Score Decomposition */}
                      <div className="space-y-4">
                        {/* Experience Alignment */}
                        {rec.explanation.experience_alignment && (
                          <div className="p-3.5 rounded-xl bg-surface-200/40 border border-white/5 space-y-2 text-xs">
                            <span className="font-mono text-gold-400 uppercase tracking-wider text-[11px] block">
                              Experience Tenure Alignment
                            </span>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400">Candidate Verified Tenure:</span>
                              <span className="font-mono font-semibold text-white">
                                {rec.explanation.experience_alignment.candidate_years} yrs
                              </span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-gray-400">Position Requirement:</span>
                              <span className="font-mono font-semibold text-white">
                                {rec.explanation.experience_alignment.required_years} yrs
                              </span>
                            </div>
                            <div className="flex items-center justify-between pt-1 border-t border-white/5">
                              <span className="text-gray-400">Tenure Margin:</span>
                              <span className={`font-mono font-bold ${
                                rec.explanation.experience_alignment.delta >= 0 ? 'text-emerald-400' : 'text-amber-400'
                              }`}>
                                {rec.explanation.experience_alignment.delta >= 0 ? `+${rec.explanation.experience_alignment.delta} yrs advantage` : `${rec.explanation.experience_alignment.delta} yrs`}
                              </span>
                            </div>
                          </div>
                        )}

                        {/* Multi-Stage Score Decomposition */}
                        {rec.score_breakdown && (
                          <div className="space-y-2 text-xs">
                            <span className="font-mono text-gray-400 uppercase tracking-wider text-[11px] block">
                              Multi-Stage Scoring Breakdown
                            </span>
                            <div className="space-y-1.5 font-mono">
                              <div>
                                <div className="flex justify-between text-[11px] mb-0.5">
                                  <span className="text-gray-400">CrossEncoder Rerank:</span>
                                  <span className="text-gold-300">{rec.score_breakdown.cross_encoder_rerank}</span>
                                </div>
                                <div className="w-full bg-surface-200 h-1.5 rounded-full overflow-hidden">
                                  <div
                                    className="bg-gold-500 h-full rounded-full"
                                    style={{ width: `${rec.score_breakdown.cross_encoder_rerank * 100}%` }}
                                  />
                                </div>
                              </div>

                              <div>
                                <div className="flex justify-between text-[11px] mb-0.5">
                                  <span className="text-gray-400">Dense Vector Similarity:</span>
                                  <span className="text-emerald-300">{rec.score_breakdown.dense_vector_similarity}</span>
                                </div>
                                <div className="w-full bg-surface-200 h-1.5 rounded-full overflow-hidden">
                                  <div
                                    className="bg-emerald-500 h-full rounded-full"
                                    style={{ width: `${rec.score_breakdown.dense_vector_similarity * 100}%` }}
                                  />
                                </div>
                              </div>

                              <div>
                                <div className="flex justify-between text-[11px] mb-0.5">
                                  <span className="text-gray-400">Lexical BM25 Match:</span>
                                  <span className="text-blue-300">{rec.score_breakdown.bm25_lexical_match}</span>
                                </div>
                                <div className="w-full bg-surface-200 h-1.5 rounded-full overflow-hidden">
                                  <div
                                    className="bg-blue-500 h-full rounded-full"
                                    style={{ width: `${rec.score_breakdown.bm25_lexical_match * 100}%` }}
                                  />
                                </div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>

                    </div>

                    {/* Evidence Citations */}
                    {rec.explanation.evidence_snippets?.length > 0 && (
                      <div className="p-3.5 rounded-xl bg-darkbg border border-white/5 space-y-1">
                        <span className="text-[10px] font-mono text-gray-500 uppercase tracking-widest block">
                          Verified Audit Citations
                        </span>
                        {rec.explanation.evidence_snippets.map((snip, snIdx) => (
                          <p key={snIdx} className="text-xs text-gray-400 font-mono">
                            • {snip}
                          </p>
                        ))}
                      </div>
                    )}

                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
