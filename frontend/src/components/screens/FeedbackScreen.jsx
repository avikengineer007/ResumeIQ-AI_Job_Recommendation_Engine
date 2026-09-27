import React, { useState } from 'react';
import {
  Sparkles,
  ThumbsUp,
  ThumbsDown,
  Star,
  Send,
  CheckCircle2,
  AlertCircle,
  MessageSquare,
  ShieldCheck,
  ArrowRight,
} from 'lucide-react';
import { submitFeedback } from '../../services/api';

export default function FeedbackScreen({ onNavigate }) {
  const [selectedAction, setSelectedAction] = useState('thumbs_up');
  const [starRating, setStarRating] = useState(5);
  const [feedbackText, setFeedbackText] = useState('');
  const [jobId, setJobId] = useState('job_rec_01');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);
  const [history, setHistory] = useState([
    {
      id: 1,
      job_id: 'job_rec_01',
      action: 'thumbs_up',
      feedback_text: 'High precision match on PyTorch & FAISS requirements.',
      rating: 5,
      date: 'Today, 2:15 PM',
    },
    {
      id: 2,
      job_id: 'job_rec_03',
      action: 'applied',
      feedback_text: 'Applied directly. Clear explanation of missing Docker skill.',
      rating: 4,
      date: 'Yesterday',
    },
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await submitFeedback({
        job_id: jobId,
        action: selectedAction,
        feedback_text: `[Rating: ${starRating}/5] ${feedbackText}`,
      });
      setHistory((prev) => [
        {
          id: Date.now(),
          job_id: jobId,
          action: selectedAction,
          feedback_text: feedbackText,
          rating: starRating,
          date: 'Just now',
        },
        ...prev,
      ]);
      setToast('Feedback recorded! Contributes to reinforcement tuning on validation.');
      setFeedbackText('');
      setTimeout(() => setToast(null), 3000);
    } catch (err) {
      // handled
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8 space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-display font-bold text-white flex items-center justify-center space-x-2">
          <MessageSquare className="w-6 h-6 text-gold-400" />
          <span>Candidate Relevance & Quality Feedback</span>
        </h2>
        <p className="text-xs text-gray-400">
          Provide human feedback to benchmark ranking alignment, explanation clarity, and calibration quality
        </p>
      </div>

      {toast && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-emerald-400 text-xs">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Main Feedback Form Card */}
      <form
        onSubmit={handleSubmit}
        className="p-8 rounded-2xl bg-surface-card border border-surface-border space-y-6 shadow-xl"
      >
        {/* Interaction Action Selection */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
            Recommendation Interaction
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { id: 'thumbs_up', label: 'Relevant', icon: ThumbsUp },
              { id: 'thumbs_down', label: 'Not Relevant', icon: ThumbsDown },
              { id: 'applied', label: 'Applied', icon: CheckCircle2 },
              { id: 'saved', label: 'Saved for Later', icon: Star },
            ].map((btn) => {
              const Icon = btn.icon;
              const active = selectedAction === btn.id;
              return (
                <button
                  key={btn.id}
                  type="button"
                  onClick={() => setSelectedAction(btn.id)}
                  className={`py-3 px-3 rounded-xl border text-xs font-medium flex flex-col items-center justify-center space-y-1.5 transition-all cursor-pointer ${
                    active
                      ? 'bg-gold-500/20 border-gold-500 text-gold-300 font-semibold shadow-sm'
                      : 'bg-darkbg border-surface-border text-gray-400 hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{btn.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 1-5 Star Clarity Rating */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono flex items-center justify-between">
            <span>Match & Explanation Quality</span>
            <span className="text-gold-400 font-mono">{starRating} of 5 Stars</span>
          </label>
          <div className="flex items-center space-x-2 bg-darkbg p-3 rounded-xl border border-surface-border">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setStarRating(star)}
                className="p-1 cursor-pointer transition-transform hover:scale-110"
              >
                <Star
                  className={`w-6 h-6 ${
                    star <= starRating
                      ? 'text-gold-400 fill-gold-400'
                      : 'text-gray-600'
                  }`}
                />
              </button>
            ))}
          </div>
        </div>

        {/* Comments Box */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
            Detailed Observations / Explanation Audit
          </label>
          <textarea
            rows={3}
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="Tell us why this job matched or didn't match your background (e.g. required skill was missing or over-weighted)..."
            className="w-full px-3.5 py-2.5 rounded-xl bg-darkbg border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500 transition-colors leading-relaxed"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 rounded-xl bg-gold-500 hover:bg-gold-400 text-darkbg font-semibold text-xs transition-all shadow-md shadow-gold-500/20 flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          <span>{loading ? 'Submitting...' : 'Submit Feedback to Evaluation Harness'}</span>
        </button>
      </form>

      {/* Audit Log History */}
      <div className="space-y-4">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider font-mono px-1">
          Recent Feedback Records
        </h3>
        <div className="space-y-3">
          {history.map((record) => (
            <div
              key={record.id}
              className="p-4 rounded-xl bg-surface-card border border-surface-border flex items-start justify-between gap-4 text-xs font-mono"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2 text-white">
                  <span className="text-gold-400 font-bold capitalize">
                    {record.action.replace('_', ' ')}
                  </span>
                  <span>•</span>
                  <span className="text-gray-400">{record.job_id}</span>
                </div>
                <p className="text-gray-300 font-sans text-xs">
                  {record.feedback_text || 'No comment provided.'}
                </p>
              </div>

              <div className="text-right flex-shrink-0 text-gray-500 text-[11px]">
                {record.date}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
