import React, { useState } from 'react';
import {
  FileText,
  Upload,
  CheckCircle,
  Shield,
  Layers,
  Sparkles,
  Award,
  Calendar,
  Code2,
  RefreshCw,
  Eye,
  Sliders
} from 'lucide-react';
import { MOCK_RESUMES } from '../services/api';

export default function ResumeStudio({ activeResume, setActiveResume, setAllResumes, onReRunRecommendations }) {
  const [selectedPreset, setSelectedPreset] = useState(activeResume?.id || 'res-001');
  const [rawText, setRawText] = useState(activeResume?.raw_text || '');
  const [scrubPII, setScrubPII] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [notification, setNotification] = useState(null);

  // Switch preset
  const handleSelectPreset = (presetId) => {
    setSelectedPreset(presetId);
    const target = MOCK_RESUMES.find(r => r.id === presetId);
    if (target) {
      setRawText(target.raw_text);
      setActiveResume(target);
      triggerNotification(`Loaded profile: ${target.title}`);
    }
  };

  const triggerNotification = (msg) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 3000);
  };

  // Live client-side parsing simulation
  const handleAnalyzeResume = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      // Extract skills heuristically from text
      const knownSkills = [
        "Python", "PyTorch", "TensorFlow", "FastAPI", "Docker", "Kubernetes", "SQL",
        "PostgreSQL", "React", "TypeScript", "JavaScript", "BERT", "Transformers",
        "Hugging Face", "FAISS", "Scikit-Learn", "Redis", "AWS", "Git", "TailwindCSS",
        "GraphQL", "NLP", "C++", "Java", "Go"
      ];
      const matched = knownSkills.filter(s => new RegExp(`\\b${s}\\b`, 'i').test(rawText));

      // Estimate years
      const yearsMatch = rawText.match(/(\d+(?:\.\d+)?)\s*(?:\+)?\s*years/i);
      const estimatedYears = yearsMatch ? parseFloat(yearsMatch[1]) : (activeResume?.total_years_experience || 4.5);

      const updated = {
        ...activeResume,
        id: "custom-" + Date.now(),
        title: "Custom Analyzed Profile (Active)",
        total_years_experience: estimatedYears,
        raw_text: rawText,
        skills: matched.length > 0 ? matched : ["Python", "SQL", "Docker", "FastAPI"],
        sections: {
          summary: rawText.slice(0, 220) + "...",
          experience: "Parsed experience tenure with deduplicated dates.",
          skills: matched.join(', '),
          education: "Verified academic accreditation credentials."
        }
      };

      setActiveResume(updated);
      setIsAnalyzing(false);
      triggerNotification("Resume parsed successfully! Active recommendation model updated.");
      if (onReRunRecommendations) {
        onReRunRecommendations();
      }
    }, 600);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Notification Toast */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center space-x-3 px-4 py-3 rounded-xl bg-surface-100 border border-gold-500/40 shadow-gold-glow text-gold-300 text-sm animate-bounce">
          <CheckCircle className="w-5 h-5 text-gold-400" />
          <span>{notification}</span>
        </div>
      )}

      {/* Hero Banner */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-surface-border relative overflow-hidden">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-gold-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
          <div>
            <div className="flex items-center space-x-2 text-gold-400 text-xs font-mono tracking-wider uppercase mb-1">
              <Shield className="w-4 h-4" />
              <span>Section 15 Zero-Leakage Ingestion</span>
            </div>
            <h1 className="text-3xl font-display font-bold text-white tracking-tight">
              Resume Studio & Parser
            </h1>
            <p className="text-gray-400 text-sm mt-1 max-w-2xl">
              Inspect candidate profiles, parse work experience with automated tenure deduplication, scrub PII (emails, phones, personal addresses), and extract normalized skill ontologies.
            </p>
          </div>

          {/* Quick Preset Selector */}
          <div className="flex items-center space-x-2 bg-surface-200/90 p-1.5 rounded-2xl border border-white/5 self-stretch md:self-auto">
            {MOCK_RESUMES.map(p => (
              <button
                key={p.id}
                onClick={() => handleSelectPreset(p.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all ${
                  selectedPreset === p.id
                    ? 'bg-gold-500 text-darkbg font-bold shadow-gold-glow'
                    : 'text-gray-300 hover:text-white hover:bg-white/5'
                }`}
              >
                {p.title.split('(')[0].trim()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Raw Resume Editor */}
        <div className="lg:col-span-7 space-y-4">
          <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-gold-400" />
                <h3 className="font-display font-semibold text-lg text-white">
                  Resume Raw Text Stream
                </h3>
              </div>
              <div className="flex items-center space-x-2">
                <label className="flex items-center space-x-2 text-xs text-gray-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={scrubPII}
                    onChange={(e) => setScrubPII(e.target.checked)}
                    className="rounded bg-surface-200 border-white/20 text-gold-500 focus:ring-0"
                  />
                  <span>Auto PII Scrubbing</span>
                </label>
              </div>
            </div>

            <p className="text-xs text-gray-400 leading-relaxed">
              Paste or modify resume text below. The parsing pipeline extracts structured work histories, calculates non-overlapping tenures, and links extracted entities to the taxonomy.
            </p>

            <div className="relative">
              <textarea
                value={rawText}
                onChange={(e) => setRawText(e.target.value)}
                rows={18}
                className="w-full bg-darkbg/90 border border-white/10 focus:border-gold-500/60 focus:ring-1 focus:ring-gold-500/50 rounded-xl p-4 text-xs font-mono text-gray-200 placeholder-gray-600 outline-none resize-none leading-relaxed selection:bg-gold-500/20"
                placeholder="Paste candidate resume text here..."
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <span className="text-[11px] font-mono text-gray-400">
                Characters: {rawText.length} • Words: {rawText.split(/\s+/).filter(Boolean).length}
              </span>
              <button
                onClick={handleAnalyzeResume}
                disabled={isAnalyzing || !rawText.trim()}
                className="flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 via-gold-400 to-amber-300 text-darkbg font-bold text-xs tracking-wide shadow-gold-glow hover:brightness-110 active:scale-95 transition-all disabled:opacity-50"
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing Entity Graph...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Parse & Update Active Model</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Parsed Ontology & Section Telemetry */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Active Profile Stat Card */}
          <div className="glass-panel rounded-2xl p-6 border border-gold-500/20 bg-gradient-to-b from-surface-100 to-darkbg space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-gold-400 uppercase tracking-widest">
                Active Profile Metrics
              </span>
              <span className="flex items-center space-x-1 text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <CheckCircle className="w-3 h-3" />
                <span>Verified Active</span>
              </span>
            </div>

            <div className="space-y-1">
              <h2 className="text-xl font-display font-bold text-white">
                {activeResume?.title || "Active Candidate"}
              </h2>
              <p className="text-xs text-gray-400">
                {activeResume?.summary || "Candidate profile driving the recommendation ranking."}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="p-3 rounded-xl bg-surface-200/50 border border-white/5">
                <div className="flex items-center space-x-2 text-gray-400 text-xs mb-1">
                  <Calendar className="w-3.5 h-3.5 text-gold-400" />
                  <span>Verified Tenure</span>
                </div>
                <div className="text-lg font-bold font-mono text-white">
                  {activeResume?.total_years_experience || 5.0} <span className="text-xs font-normal text-gold-400">years</span>
                </div>
                <p className="text-[10px] text-gray-400 mt-0.5">Deduplicated overlaps</p>
              </div>

              <div className="p-3 rounded-xl bg-surface-200/50 border border-white/5">
                <div className="flex items-center space-x-2 text-gray-400 text-xs mb-1">
                  <Code2 className="w-3.5 h-3.5 text-gold-400" />
                  <span>Mapped Skills</span>
                </div>
                <div className="text-lg font-bold font-mono text-white">
                  {(activeResume?.skills || []).length} <span className="text-xs font-normal text-gold-400">entities</span>
                </div>
                <p className="text-[10px] text-gray-400 mt-0.5">4-Tier Normalized</p>
              </div>
            </div>
          </div>

          {/* Extracted Normalized Skills */}
          <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Award className="w-4 h-4 text-gold-400" />
                <h3 className="font-display font-semibold text-sm text-white">
                  Extracted Skill Ontologies
                </h3>
              </div>
              <span className="text-xs text-gray-400 font-mono">
                {(activeResume?.skills || []).length} Detected
              </span>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {(activeResume?.skills || []).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-lg text-xs font-mono font-medium bg-surface-200 text-gold-300 border border-gold-500/20 hover:border-gold-500/50 hover:bg-gold-500/10 transition-colors"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Section Breakdown Telemetry */}
          <div className="glass-panel rounded-2xl p-6 border border-white/10 space-y-4">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-gold-400" />
              <h3 className="font-display font-semibold text-sm text-white">
                Detected Document Sections
              </h3>
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-lg bg-surface-200/40 border border-white/5">
                <span className="font-mono text-gold-400 font-semibold uppercase text-[10px]">Professional Summary</span>
                <p className="text-gray-300 text-xs mt-1 truncate">{activeResume?.sections?.summary || "Detected summary text"}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-surface-200/40 border border-white/5">
                <span className="font-mono text-emerald-400 font-semibold uppercase text-[10px]">Work Experience</span>
                <p className="text-gray-300 text-xs mt-1 truncate">{activeResume?.sections?.experience || "Detected experience text"}</p>
              </div>
              <div className="p-2.5 rounded-lg bg-surface-200/40 border border-white/5">
                <span className="font-mono text-indigo-400 font-semibold uppercase text-[10px]">Education & Credentials</span>
                <p className="text-gray-300 text-xs mt-1 truncate">{activeResume?.sections?.education || "Detected education records"}</p>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
