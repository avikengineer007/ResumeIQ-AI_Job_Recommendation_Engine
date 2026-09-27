import React from 'react';
import {
  BarChart3,
  AlertTriangle,
  CheckCircle2,
  ArrowLeft,
  ArrowRight,
  BookOpen,
  GraduationCap,
  Sparkles,
  TrendingUp,
} from 'lucide-react';

export default function SkillGapScreen({
  job,
  activeResume,
  onNavigate,
}) {
  const currentJob = job || {
    title: 'Staff Machine Learning Engineer',
    company: 'NeuralSphere AI',
    explanation: {
      matched_skills: ['Python', 'PyTorch', 'FAISS', 'FastAPI'],
      missing_skills: ['AWS Bedrock', 'Triton Inference Server', 'vLLM', 'Ray'],
    },
  };

  const matched = currentJob.explanation?.matched_skills || ['Python', 'SQL'];
  const missing = currentJob.explanation?.missing_skills || [
    'AWS Bedrock',
    'Triton Server',
    'Ray',
  ];

  const total = matched.length + missing.length;
  const coveragePct = Math.round((matched.length / Math.max(1, total)) * 100);

  const learningRoadmap = [
    {
      skill: missing[0] || 'Distributed Inference (Triton/vLLM)',
      category: 'Model Serving',
      estTime: '2-3 weeks',
      recommendation:
        'Deploy sample HuggingFace models with Triton C++ backend or vLLM PagedAttention inference server.',
    },
    {
      skill: missing[1] || 'Cloud AI Infrastructure (AWS Bedrock)',
      category: 'Cloud Deployments',
      estTime: '1-2 weeks',
      recommendation:
        'Complete AWS Bedrock hands-on tutorial for foundation model API invocation and IAM role management.',
    },
    {
      skill: missing[2] || 'Ray Train / Tune',
      category: 'Distributed Computing',
      estTime: '2 weeks',
      recommendation:
        'Scale PyTorch DDP pipelines across multi-worker clusters with Ray Train and Ray Core primitives.',
    },
  ];

  return (
    <div className="space-y-6 py-6 max-w-4xl mx-auto animate-fadeIn">
      {/* Back button */}
      <button
        onClick={() => onNavigate('recommendation_dashboard')}
        className="inline-flex items-center space-x-1.5 text-xs text-gray-400 hover:text-white transition-colors cursor-pointer"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Recommendations</span>
      </button>

      {/* Overview Card */}
      <div className="p-8 rounded-2xl bg-surface-card border border-surface-border space-y-6 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono">
              <BarChart3 className="w-4 h-4" />
              <span>Diagnostic Skill Gap Analysis</span>
            </div>
            <h2 className="text-2xl font-display font-bold text-white">
              Skill Overlap & Gap Breakdown
            </h2>
            <p className="text-xs text-gray-400">
              Comparing profile against requirements for {currentJob.title} at {currentJob.company}
            </p>
          </div>

          <div className="bg-darkbg p-4 rounded-xl border border-surface-border flex items-center space-x-4">
            <div className="text-center">
              <div className="text-2xl font-bold font-mono text-gold-400">
                {coveragePct}%
              </div>
              <div className="text-[10px] text-gray-400 font-mono">Skill Match</div>
            </div>
            <div className="w-px h-8 bg-surface-border" />
            <div className="text-center">
              <div className="text-2xl font-bold font-mono text-amber-400">
                {missing.length}
              </div>
              <div className="text-[10px] text-gray-400 font-mono">Gaps to Bridge</div>
            </div>
          </div>
        </div>

        {/* Visual Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-mono text-gray-400">
            <span>
              {matched.length} Matched / {total} Total Required Competencies
            </span>
            <span>{coveragePct}% Coverage</span>
          </div>
          <div className="w-full h-3 rounded-full bg-darkbg border border-surface-border overflow-hidden flex">
            <div
              className="bg-emerald-500 h-full transition-all duration-500"
              style={{ width: `${coveragePct}%` }}
              title="Matched Skills"
            />
            <div
              className="bg-amber-500/80 h-full transition-all duration-500"
              style={{ width: `${100 - coveragePct}%` }}
              title="Missing Skill Gaps"
            />
          </div>
        </div>
      </div>

      {/* Identified Missing Skills & Roadmap */}
      <div className="p-8 rounded-2xl bg-surface-card border border-surface-border space-y-6">
        <h3 className="text-base font-bold text-white font-display flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-gold-400" />
          <span>Recommended Skill-Bridging Roadmap</span>
        </h3>

        <div className="space-y-4">
          {learningRoadmap.map((item, idx) => (
            <div
              key={idx}
              className="p-5 rounded-xl bg-darkbg border border-surface-border space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center space-x-2.5">
                  <span className="w-6 h-6 rounded-full bg-amber-500/20 text-amber-300 font-mono text-xs flex items-center justify-center font-bold">
                    {idx + 1}
                  </span>
                  <span className="text-sm font-bold text-white font-mono">
                    {item.skill}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-surface-card border border-surface-border text-gray-400">
                    {item.category}
                  </span>
                </div>
                <span className="text-xs font-mono text-gold-400">
                  Est. {item.estTime}
                </span>
              </div>

              <p className="text-xs text-gray-300 leading-relaxed pl-8">
                {item.recommendation}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
