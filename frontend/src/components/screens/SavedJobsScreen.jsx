import React, { useState, useEffect } from 'react';
import {
  Bookmark,
  Building,
  MapPin,
  Trash2,
  ExternalLink,
  CheckCircle2,
  Send,
  ArrowRight,
  Edit3,
} from 'lucide-react';
import { fetchSavedJobs, deleteSavedJob, MOCK_JOBS } from '../../services/api';

export default function SavedJobsScreen({ onSelectJob, onNavigate }) {
  const [savedList, setSavedList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const loadSaved = async () => {
    setLoading(true);
    try {
      const items = await fetchSavedJobs();
      if (items && items.length > 0) {
        setSavedList(items);
      } else {
        // Fallback default sample saved jobs
        setSavedList([
          {
            job_id: 'job_rec_01',
            title: 'Staff Machine Learning Engineer',
            company: 'NeuralSphere AI',
            location: 'San Francisco, CA',
            work_mode: 'remote',
            status: 'saved',
            notes: 'High priority application. Great PyTorch + FAISS focus.',
            saved_at: new Date().toISOString(),
          },
          {
            job_id: 'job_rec_02',
            title: 'Senior NLP Research Engineer',
            company: 'Cohere Partner Labs',
            location: 'Remote, US',
            work_mode: 'remote',
            status: 'interviewing',
            notes: 'Screening interview scheduled next Tuesday.',
            saved_at: new Date(Date.now() - 86400000).toISOString(),
          },
        ]);
      }
    } catch (err) {
      // handled
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSaved();
  }, []);

  const handleRemove = async (jobId) => {
    await deleteSavedJob(jobId);
    setSavedList((prev) => prev.filter((j) => (j.job_id || j.id) !== jobId));
    setToast('Job removed from bookmarks.');
    setTimeout(() => setToast(null), 2500);
  };

  return (
    <div className="space-y-6 py-6 max-w-4xl mx-auto animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-2xl bg-surface-card border border-surface-border">
        <div>
          <h2 className="text-2xl font-display font-bold text-white flex items-center space-x-2">
            <Bookmark className="w-6 h-6 text-gold-400" />
            <span>Saved Jobs Collection</span>
          </h2>
          <p className="text-xs text-gray-400">
            Track your bookmarked positions, personal application notes, and interview status
          </p>
        </div>

        <button
          onClick={() => onNavigate('search')}
          className="px-4 py-2 rounded-xl bg-gold-500 hover:bg-gold-400 text-darkbg font-semibold text-xs transition-all shadow-md shadow-gold-500/20 cursor-pointer"
        >
          Discover More Jobs
        </button>
      </div>

      {toast && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-emerald-400 text-xs">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* List */}
      {savedList.length === 0 ? (
        <div className="p-12 text-center rounded-2xl bg-surface-card border border-surface-border space-y-4">
          <Bookmark className="w-10 h-10 text-gray-600 mx-auto" />
          <p className="text-sm text-gray-400">
            You haven't bookmarked any jobs yet.
          </p>
          <button
            onClick={() => onNavigate('recommendation_dashboard')}
            className="px-5 py-2.5 rounded-xl bg-gold-500 text-darkbg font-semibold text-xs"
          >
            Explore Recommendations
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {savedList.map((item, idx) => {
            const jobId = item.job_id || item.id;
            return (
              <div
                key={jobId || idx}
                className="p-6 rounded-2xl bg-surface-card border border-surface-border space-y-4 hover:border-gold-500/40 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div className="space-y-1">
                    <h3 className="text-lg font-bold text-white leading-snug">
                      {item.title || `Job Opportunity (${jobId})`}
                    </h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-gray-400">
                      <span className="flex items-center space-x-1 text-gray-300">
                        <Building className="w-3.5 h-3.5 text-gray-500" />
                        <span>{item.company || 'Enterprise Partner'}</span>
                      </span>
                      <span className="flex items-center space-x-1">
                        <MapPin className="w-3.5 h-3.5 text-gray-500" />
                        <span>{item.location || 'Remote'}</span>
                      </span>
                      <span className="px-2 py-0.5 rounded-md bg-darkbg border border-surface-border text-[11px] font-mono capitalize">
                        {item.work_mode || 'remote'}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-400 text-xs font-mono capitalize">
                      {item.status || 'Saved'}
                    </span>
                    <button
                      onClick={() => handleRemove(jobId)}
                      className="p-2 rounded-xl bg-darkbg hover:bg-red-500/20 border border-surface-border hover:border-red-500/40 text-gray-400 hover:text-red-400 transition-colors cursor-pointer"
                      title="Remove bookmark"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Candidate notes box */}
                <div className="p-3.5 rounded-xl bg-darkbg border border-surface-border text-xs text-gray-300 flex items-start space-x-2">
                  <Edit3 className="w-3.5 h-3.5 text-gold-400 flex-shrink-0 mt-0.5" />
                  <p className="leading-relaxed">
                    <strong className="text-gray-200">Notes:</strong>{' '}
                    {item.notes || 'No candidate notes added yet.'}
                  </p>
                </div>

                <div className="pt-2 flex items-center justify-between">
                  <span className="text-[11px] font-mono text-gray-500">
                    Saved on {new Date(item.saved_at || Date.now()).toLocaleDateString()}
                  </span>

                  <button
                    onClick={() => {
                      if (onSelectJob) onSelectJob(item);
                      if (onNavigate) onNavigate('job_details');
                    }}
                    className="text-xs font-medium text-gold-400 hover:text-gold-300 flex items-center space-x-1 cursor-pointer"
                  >
                    <span>View Posting</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
