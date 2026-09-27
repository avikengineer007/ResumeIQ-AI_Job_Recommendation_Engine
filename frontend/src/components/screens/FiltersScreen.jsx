import React from 'react';
import {
  Sliders,
  MapPin,
  Briefcase,
  CheckCircle2,
  Calendar,
  Layers,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

export default function FiltersScreen({
  filterState,
  setFilterState,
  onNavigate,
}) {
  const {
    targetRole = 'Machine Learning Engineer',
    selectedModes = ['remote', 'hybrid'],
    requireMode = false,
    selectedLocation = 'San Francisco, CA',
    requireLocation = false,
    minYears = 2.0,
    topK = 10,
  } = filterState;

  const handleModeToggle = (mode) => {
    const current = new Set(selectedModes);
    if (current.has(mode)) {
      if (current.size > 1) current.delete(mode);
    } else {
      current.add(mode);
    }
    setFilterState({ ...filterState, selectedModes: Array.from(current) });
  };

  const handleReset = () => {
    setFilterState({
      targetRole: 'Machine Learning Engineer',
      selectedModes: ['remote', 'hybrid'],
      requireMode: false,
      selectedLocation: '',
      requireLocation: false,
      minYears: 1.0,
      topK: 10,
    });
  };

  return (
    <div className="max-w-2xl mx-auto py-8 space-y-8 animate-fadeIn">
      {/* Title */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-display font-bold text-white flex items-center justify-center space-x-2">
          <Sliders className="w-6 h-6 text-gold-400" />
          <span>Recommendation Filters & Constraints</span>
        </h2>
        <p className="text-xs text-gray-400">
          Tune recommendation parameters, hard constraints, and ranking candidate depth
        </p>
      </div>

      {/* Main Filter Configuration Card */}
      <div className="p-8 rounded-2xl bg-surface-card border border-surface-border space-y-6 shadow-xl">
        {/* Target Role */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
            Target Job Title / Role
          </label>
          <input
            type="text"
            value={targetRole}
            onChange={(e) =>
              setFilterState({ ...filterState, targetRole: e.target.value })
            }
            placeholder="e.g. Machine Learning Engineer, Staff Backend Developer"
            className="w-full px-3.5 py-2.5 rounded-xl bg-darkbg border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500 transition-colors"
          />
        </div>

        {/* Work Arrangement Mode */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
              Work Arrangement Modes
            </label>
            <label className="flex items-center space-x-2 text-xs text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={requireMode}
                onChange={(e) =>
                  setFilterState({
                    ...filterState,
                    requireMode: e.target.checked,
                  })
                }
                className="rounded border-surface-border text-gold-500 focus:ring-0 bg-darkbg"
              />
              <span className="font-semibold text-gold-400">
                Strict Hard Filter (Exclude Non-Matches)
              </span>
            </label>
          </div>

          <div className="grid grid-cols-3 gap-3">
            {['remote', 'hybrid', 'onsite'].map((mode) => {
              const active = selectedModes.includes(mode);
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

        {/* Location & Strict Filter */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
              Preferred Location
            </label>
            <label className="flex items-center space-x-2 text-xs text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={requireLocation}
                onChange={(e) =>
                  setFilterState({
                    ...filterState,
                    requireLocation: e.target.checked,
                  })
                }
                className="rounded border-surface-border text-gold-500 focus:ring-0 bg-darkbg"
              />
              <span className="font-semibold text-gold-400">
                Strict Location Match
              </span>
            </label>
          </div>

          <div className="relative">
            <MapPin className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={selectedLocation}
              onChange={(e) =>
                setFilterState({
                  ...filterState,
                  selectedLocation: e.target.value,
                })
              }
              placeholder="e.g. San Francisco, CA or Remote"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-darkbg border border-surface-border text-white text-xs focus:outline-none focus:border-gold-500 transition-colors"
            />
          </div>
        </div>

        {/* Minimum Years Experience Slider */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="font-bold text-gray-300 uppercase tracking-wider font-mono">
              Minimum Experience
            </span>
            <span className="font-mono text-gold-400 font-bold">
              {minYears} Years
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="12"
            step="0.5"
            value={minYears}
            onChange={(e) =>
              setFilterState({
                ...filterState,
                minYears: parseFloat(e.target.value),
              })
            }
            className="w-full accent-gold-500 cursor-pointer"
          />
        </div>

        {/* Top-K Recommendations Depth */}
        <div className="space-y-2">
          <label className="text-xs font-bold text-gray-300 uppercase tracking-wider font-mono">
            Candidate Retrieval Depth (Top-K)
          </label>
          <div className="grid grid-cols-4 gap-3">
            {[5, 10, 20, 50].map((k) => (
              <button
                key={k}
                type="button"
                onClick={() => setFilterState({ ...filterState, topK: k })}
                className={`py-2 rounded-xl border text-xs font-mono transition-all cursor-pointer ${
                  topK === k
                    ? 'bg-gold-500 text-darkbg font-bold border-gold-500 shadow-sm'
                    : 'bg-darkbg border-surface-border text-gray-400 hover:text-white'
                }`}
              >
                Top {k}
              </button>
            ))}
          </div>
        </div>

        {/* Buttons */}
        <div className="pt-4 border-t border-surface-border flex items-center justify-between">
          <button
            type="button"
            onClick={handleReset}
            className="px-4 py-2 rounded-xl bg-darkbg border border-surface-border text-gray-400 hover:text-white text-xs transition-colors cursor-pointer"
          >
            Reset Defaults
          </button>

          <button
            type="button"
            onClick={() => onNavigate('recommendation_dashboard')}
            className="px-6 py-2.5 rounded-xl bg-gold-500 hover:bg-gold-400 text-darkbg font-semibold text-xs transition-all shadow-md shadow-gold-500/20 flex items-center space-x-2 cursor-pointer"
          >
            <span>Apply Filters & View Feed</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
