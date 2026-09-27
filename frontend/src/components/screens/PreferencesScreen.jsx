import React, { useState, useEffect } from 'react';
import {
  Sliders,
  DollarSign,
  MapPin,
  Briefcase,
  CheckCircle2,
  Shield,
  Save,
  ArrowRight,
} from 'lucide-react';
import { fetchUserPreferences, updateUserPreferences } from '../../services/api';

export default function PreferencesScreen({ onNavigate }) {
  const [targetRole, setTargetRole] = useState('Machine Learning Engineer');
  const [preferredLocations, setPreferredLocations] = useState([
    'San Francisco, CA',
    'Remote',
  ]);
  const [preferredWorkModes, setPreferredWorkModes] = useState([
    'remote',
    'hybrid',
  ]);
  const [minSalary, setMinSalary] = useState(175000);
  const [requireWorkMode, setRequireWorkMode] = useState(false);
  const [requireLocation, setRequireLocation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    async function load() {
      const data = await fetchUserPreferences();
      if (data) {
        if (data.target_role) setTargetRole(data.target_role);
        if (data.preferred_locations) setPreferredLocations(data.preferred_locations);
        if (data.preferred_work_modes) setPreferredWorkModes(data.preferred_work_modes);
        if (data.min_salary) setMinSalary(data.min_salary);
        if (typeof data.require_work_mode === 'boolean')
          setRequireWorkMode(data.require_work_mode);
        if (typeof data.require_location === 'boolean')
          setRequireLocation(data.require_location);
      }
    }
    load();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updateUserPreferences({
        target_role: targetRole,
        preferred_locations: preferredLocations,
        preferred_work_modes: preferredWorkModes,
        min_salary: minSalary,
        require_work_mode: requireWorkMode,
        require_location: requireLocation,
      });
      setToast('Personal career preferences saved to database!');
      setTimeout(() => setToast(null), 3000);
    } catch (err) {
      // handled
    } finally {
      setLoading(false);
    }
  };

  const handleModeToggle = (mode) => {
    const s = new Set(preferredWorkModes);
    if (s.has(mode)) {
      if (s.size > 1) s.delete(mode);
    } else {
      s.add(mode);
    }
    setPreferredWorkModes(Array.from(s));
  };

  return (
    <div className="max-w-2xl mx-auto py-8 space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-display font-bold text-white flex items-center justify-center space-x-2">
          <Sliders className="w-6 h-6 text-gold-400" />
          <span>Candidate Career Preferences</span>
        </h2>
        <p className="text-xs text-gray-400">
          Set career targets, salary requirements, and hard filters saved across sessions
        </p>
      </div>

      {toast && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center space-x-2 text-emerald-400 text-xs">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{toast}</span>
        </div>
      )}

      {/* Preferences Card Form */}
      <form
        onSubmit={handleSave}
        className="p-8 rounded-2xl bg-surface-card border border-surface-border space-y-6 shadow-xl"
      >
        {/* Target Role */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
            Target Job Title
          </label>
          <input
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="Staff Machine Learning Engineer"
            className="w-full px-3.5 py-2.5 rounded-xl bg-darkbg border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500 transition-colors"
          />
        </div>

        {/* Work Arrangement Mode */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
              Work Modes
            </label>
            <label className="flex items-center space-x-2 text-xs text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={requireWorkMode}
                onChange={(e) => setRequireWorkMode(e.target.checked)}
                className="rounded border-surface-border text-gold-500 focus:ring-0 bg-darkbg"
              />
              <span className="font-semibold text-gold-400">
                Hard Constraint
              </span>
            </label>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {['remote', 'hybrid', 'onsite'].map((mode) => {
              const active = preferredWorkModes.includes(mode);
              return (
                <button
                  key={mode}
                  type="button"
                  onClick={() => handleModeToggle(mode)}
                  className={`py-2.5 px-3 rounded-xl border text-xs font-medium capitalize transition-all cursor-pointer ${
                    active
                      ? 'bg-gold-500/20 border-gold-500/50 text-gold-300 font-semibold shadow-sm'
                      : 'bg-darkbg border-surface-border text-gray-400 hover:text-white'
                  }`}
                >
                  {mode}
                </button>
              );
            })}
          </div>
        </div>

        {/* Minimum Salary Slider */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="font-bold text-gray-300 uppercase tracking-wider font-mono">
              Minimum Base Salary Expectation
            </span>
            <span className="font-mono text-gold-400 font-bold">
              ${minSalary.toLocaleString()} USD
            </span>
          </div>
          <input
            type="range"
            min="60000"
            max="350000"
            step="5000"
            value={minSalary}
            onChange={(e) => setMinSalary(parseInt(e.target.value))}
            className="w-full accent-gold-500 cursor-pointer"
          />
        </div>

        {/* Preferred Location */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
              Target Locations
            </label>
            <label className="flex items-center space-x-2 text-xs text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={requireLocation}
                onChange={(e) => setRequireLocation(e.target.checked)}
                className="rounded border-surface-border text-gold-500 focus:ring-0 bg-darkbg"
              />
              <span className="font-semibold text-gold-400">
                Hard Constraint
              </span>
            </label>
          </div>
          <div className="relative">
            <MapPin className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={preferredLocations.join(', ')}
              onChange={(e) =>
                setPreferredLocations(
                  e.target.value.split(',').map((s) => s.trim()).filter(Boolean)
                )
              }
              placeholder="San Francisco, CA, Remote, New York, NY"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-darkbg border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500 transition-colors"
            />
          </div>
        </div>

        {/* Submit */}
        <div className="pt-4 border-t border-surface-border flex items-center justify-between">
          <button
            type="button"
            onClick={() => onNavigate('recommendation_dashboard')}
            className="px-4 py-2.5 rounded-xl bg-darkbg border border-surface-border text-gray-400 hover:text-white text-xs cursor-pointer"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-gold-500 hover:bg-gold-400 text-darkbg font-semibold text-xs transition-all shadow-md shadow-gold-500/20 flex items-center space-x-2 cursor-pointer"
          >
            <Save className="w-4 h-4" />
            <span>{loading ? 'Saving...' : 'Save Preferences'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}
