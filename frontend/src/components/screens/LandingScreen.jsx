import React from 'react';
import {
  Sparkles,
  ShieldCheck,
  Cpu,
  Search,
  FileText,
  Sliders,
  Target,
  ArrowRight,
  CheckCircle2,
  Lock,
  Layers,
  BarChart3,
} from 'lucide-react';

export default function LandingScreen({ onNavigate }) {
  return (
    <div className="space-y-16 py-6 animate-fadeIn">
      {/* Hero Section */}
      <section className="relative text-center max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-400 text-xs font-mono">
          <Sparkles className="w-3.5 h-3.5 text-gold-400" />
          <span>Research Platform & Production Recommendation Engine</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-display font-extrabold tracking-tight text-white leading-tight">
          Skill-Aware Semantic Search with{' '}
          <span className="text-gold-gradient">Zero Hallucinations</span>
        </h1>

        <p className="text-lg text-gray-300 max-w-2xl mx-auto leading-relaxed">
          Upload your resume to discover hyper-personalized job recommendations.
          Every match is transparently verified against factual source spans
          using hybrid BM25 + dense retrieval, cross-encoder reranking, and
          Platt/Isotonic calibrated scoring.
        </p>

        {/* Hero CTA buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <button
            onClick={() => onNavigate('upload')}
            className="px-6 py-3.5 rounded-xl bg-gold-500 hover:bg-gold-400 text-darkbg font-semibold text-sm transition-all duration-200 shadow-lg shadow-gold-500/20 flex items-center space-x-2 group cursor-pointer"
          >
            <span>Upload Resume</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <button
            onClick={() => onNavigate('recommendation_dashboard')}
            className="px-6 py-3.5 rounded-xl bg-surface-card hover:bg-surface-card/80 border border-surface-border text-white font-medium text-sm transition-all duration-200 cursor-pointer flex items-center space-x-2"
          >
            <Target className="w-4 h-4 text-gold-400" />
            <span>Explore Recommendations</span>
          </button>
          <button
            onClick={() => onNavigate('search')}
            className="px-6 py-3.5 rounded-xl bg-surface-card hover:bg-surface-card/80 border border-surface-border text-white font-medium text-sm transition-all duration-200 cursor-pointer flex items-center space-x-2"
          >
            <Search className="w-4 h-4 text-blue-400" />
            <span>Live Job Search</span>
          </button>
        </div>
      </section>

      {/* 3 Core Architecture Pillars */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-surface-card border border-surface-border backdrop-blur-sm space-y-4 hover:border-gold-500/40 transition-colors">
          <div className="w-12 h-12 rounded-xl bg-gold-500/10 border border-gold-500/20 flex items-center justify-center text-gold-400">
            <Cpu className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white font-display">
            Hybrid Dense + Lexical Fusion
          </h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Combines BM25 tokenized lexical matching with FAISS IndexFlatIP dense
            embeddings (MiniLM/mpnet) using Reciprocal Rank Fusion (RRF k=60)
            and cross-encoder reranking.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-surface-card border border-surface-border backdrop-blur-sm space-y-4 hover:border-emerald-500/40 transition-colors">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white font-display">
            Evidence-Grounded Explanations
          </h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Strict explanation verifier rejects any claim, skill, or percentage
            not grounded in the factual evidence. Zero LLM hallucinations, with
            full source span auditability.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-surface-card border border-surface-border backdrop-blur-sm space-y-4 hover:border-blue-500/40 transition-colors">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Lock className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white font-display">
            PII Masking & Privacy First
          </h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Automatic regex and Presidio/spaCy PII scrubbing replaces emails,
            phone numbers, and physical addresses with typed tokens before
            neural representation and vector indexing.
          </p>
        </div>
      </section>

      {/* Research & Production Benchmarks Bar */}
      <section className="rounded-2xl bg-gradient-to-r from-surface-card via-surface-card/90 to-surface-card border border-surface-border p-8">
        <h2 className="text-center font-display font-bold text-xl text-white mb-6">
          Rigorous Research & Evaluation Benchmarks
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
          <div className="space-y-1">
            <div className="text-2xl font-bold font-mono text-gold-400">
              100%
            </div>
            <div className="text-xs text-gray-400">Factual Grounding</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold font-mono text-emerald-400">
              4-Tier
            </div>
            <div className="text-xs text-gray-400">Skill Normalizer</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold font-mono text-blue-400">
              &lt; 45ms
            </div>
            <div className="text-xs text-gray-400">Rerank Latency</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold font-mono text-purple-400">
              10k
            </div>
            <div className="text-xs text-gray-400">Bootstrap CIs</div>
          </div>
        </div>
      </section>

      {/* 13 Screens Sitemap Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white font-display flex items-center space-x-2">
            <Layers className="w-4 h-4 text-gold-400" />
            <span>Complete 13-Screen System Map</span>
          </h3>
          <span className="text-xs font-mono text-gray-400">
            Phase 11 Specification
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
          {[
            { id: 'landing', label: '1. Landing Hero', icon: Sparkles },
            { id: 'auth', label: '2. Login / Register', icon: Lock },
            { id: 'upload', label: '3. Resume Upload', icon: FileText },
            { id: 'resume_analysis', label: '4. Resume Analysis', icon: CheckCircle2 },
            { id: 'search', label: '5. Search Catalog', icon: Search },
            { id: 'filters', label: '6. Filters Control', icon: Sliders },
            { id: 'recommendation_dashboard', label: '7. Recommendations', icon: Target },
            { id: 'job_details', label: '8. Job Details', icon: Layers },
            { id: 'match_explanation', label: '9. Match Explanation', icon: ShieldCheck },
            { id: 'skill_gap', label: '10. Skill Gap Analyzer', icon: BarChart3 },
            { id: 'saved_jobs', label: '11. Saved Jobs', icon: CheckCircle2 },
            { id: 'preferences', label: '12. Preferences', icon: Sliders },
            { id: 'feedback', label: '13. Relevance Feedback', icon: Sparkles },
          ].map(screen => {
            const Icon = screen.icon;
            return (
              <button
                key={screen.id}
                onClick={() => onNavigate(screen.id)}
                className="p-3 rounded-xl bg-surface-card hover:bg-gold-500/10 border border-surface-border hover:border-gold-500/40 text-left transition-all duration-150 flex items-center space-x-2.5 group cursor-pointer"
              >
                <Icon className="w-4 h-4 text-gold-400 group-hover:scale-110 transition-transform flex-shrink-0" />
                <span className="text-xs font-medium text-gray-300 group-hover:text-white truncate">
                  {screen.label}
                </span>
              </button>
            );
          })}
        </div>
      </section>
    </div>
  );
}
