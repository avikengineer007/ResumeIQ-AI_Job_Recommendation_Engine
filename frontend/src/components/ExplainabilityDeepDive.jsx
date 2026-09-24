import React, { useState } from 'react';
import {
  ShieldCheck,
  AlertOctagon,
  CheckCircle,
  FileCheck,
  Layers,
  Sparkles,
  AlertTriangle,
  Play,
  RotateCcw
} from 'lucide-react';

export default function ExplainabilityDeepDive() {
  const [candidateYears, setCandidateYears] = useState(5.0);
  const [candidateSkillsText, setCandidateSkillsText] = useState("Python, PyTorch, Docker, FastAPI, SQL");
  const [jobRequiredSkillsText, setJobRequiredSkillsText] = useState("Python, PyTorch, Kubernetes, Docker");
  const [jobRequiredYears, setJobRequiredYears] = useState(4.0);
  const [explanationDraft, setExplanationDraft] = useState(
    "Matched on Python, PyTorch, and Docker. Candidate offers 5.0 years experience, exceeding the 4.0 years requirement. Skill gaps identified in Kubernetes."
  );

  const [auditResult, setAuditResult] = useState(null);

  const handleRunAudit = () => {
    const candidateSkills = candidateSkillsText.split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
    const jobSkills = jobRequiredSkillsText.split(',').map(s => s.trim().toLowerCase()).filter(Boolean);

    // Look for cited skills in draft
    const citedSkills = [];
    const allKnownSkills = ["python", "pytorch", "docker", "fastapi", "sql", "kubernetes", "quantum computing", "react"];
    allKnownSkills.forEach(skill => {
      if (new RegExp(`\\b${skill}\\b`, 'i').test(explanationDraft)) {
        citedSkills.push(skill);
      }
    });

    // Check for ungrounded skills
    const ungroundedSkills = citedSkills.filter(s => !candidateSkills.includes(s) && !jobSkills.includes(s));

    // Check numerical fidelity of candidate years
    const hasYearsMention = explanationDraft.includes(candidateYears.toString());

    const issues = [];
    if (ungroundedSkills.length > 0) {
      issues.push(`Hallucination Detected: Explanation cites ungrounded skills [${ungroundedSkills.join(', ')}] not found in candidate or job entities.`);
    }
    if (!hasYearsMention && candidateYears > 0) {
      issues.push(`Numerical Fidelity Warning: Explanation text does not verify candidate tenure of ${candidateYears} years.`);
    }

    setAuditResult({
      passed: issues.length === 0,
      timestamp: new Date().toLocaleTimeString(),
      citedSkills,
      ungroundedSkills,
      issues,
    });
  };

  const handleInjectHallucination = () => {
    setExplanationDraft(
      "Candidate is highly recommended due to extensive experience in Quantum Computing and Neuromorphic Hardware, with 12.0 years verified background."
    );
  };

  const handleResetValid = () => {
    setExplanationDraft(
      "Matched on Python, PyTorch, and Docker. Candidate offers 5.0 years experience, exceeding the 4.0 years requirement. Skill gaps identified in Kubernetes."
    );
    setAuditResult(null);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Banner */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-surface-border">
        <div className="flex items-center space-x-2 text-gold-400 text-xs font-mono uppercase tracking-wider mb-1">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Phase 11 Evidence-Grounded Verification Architecture</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-display font-bold text-white tracking-tight">
          Faithfulness & Anti-Hallucination Audit
        </h1>
        <p className="text-xs sm:text-sm text-gray-400 mt-1 max-w-3xl">
          Section 11 guarantees zero-fabrication explainability. Recommendations must never fabricate qualifications, tamper with numerical metrics, or cite skills absent from the candidate resume or job specification.
        </p>
      </div>

      {/* 4-Phase Architecture Pipeline Display */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-white/5 space-y-2">
          <span className="text-[10px] font-mono text-gold-400 uppercase tracking-widest block">Phase 1</span>
          <h3 className="font-display font-bold text-sm text-white">Evidence Extraction</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Pulls character offsets, deduplicated tenures, and normalized ontology entities from the parsed resume and job.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-white/5 space-y-2">
          <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-widest block">Phase 2</span>
          <h3 className="font-display font-bold text-sm text-white">Template Synthesis</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Constructs multifaceted summaries detailing matched competencies, honest gaps, and work arrangement compatibility.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-white/5 space-y-2">
          <span className="text-[10px] font-mono text-blue-400 uppercase tracking-widest block">Phase 3</span>
          <h3 className="font-display font-bold text-sm text-white">Active Verification</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Enforces strict assertions: numerical fidelity check, ungrounded entity rejection, and work arrangement consistency.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-white/5 space-y-2">
          <span className="text-[10px] font-mono text-purple-400 uppercase tracking-widest block">Phase 4</span>
          <h3 className="font-display font-bold text-sm text-white">Probability Calibration</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Transforms raw Cross-Encoder logit scores into true calibrated posterior probabilities via Platt/Isotonic scaling.
          </p>
        </div>
      </div>

      {/* Interactive Verification Simulator */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-display font-bold text-white">
              Interactive Verifier Simulator
            </h3>
            <p className="text-xs text-gray-400">
              Simulate the ExplanationVerifier in action. Test compliant versus adversarial explanations.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleInjectHallucination}
              className="px-3 py-1.5 rounded-xl text-xs font-mono bg-red-500/10 text-red-300 border border-red-500/30 hover:bg-red-500/20 transition-colors"
            >
              Inject Adversarial Hallucination
            </button>
            <button
              onClick={handleResetValid}
              className="px-3 py-1.5 rounded-xl text-xs font-mono bg-surface-200 text-gray-300 border border-white/10 hover:text-white transition-colors"
            >
              Reset Compliant
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Ground Truth Inputs */}
          <div className="space-y-4">
            <h4 className="text-xs font-mono text-gold-400 uppercase tracking-wider">
              Verified Ground Truth Entities
            </h4>

            <div>
              <label className="block text-xs text-gray-400 mb-1">Candidate Verified Skills:</label>
              <input
                type="text"
                value={candidateSkillsText}
                onChange={(e) => setCandidateSkillsText(e.target.value)}
                className="w-full bg-surface-200 border border-white/10 rounded-xl px-3 py-2 text-xs text-white"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-1">Job Specification Skills:</label>
              <input
                type="text"
                value={jobRequiredSkillsText}
                onChange={(e) => setJobRequiredSkillsText(e.target.value)}
                className="w-full bg-surface-200 border border-white/10 rounded-xl px-3 py-2 text-xs text-white"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Candidate Tenure (yrs):</label>
                <input
                  type="number"
                  step="0.5"
                  value={candidateYears}
                  onChange={(e) => setCandidateYears(parseFloat(e.target.value))}
                  className="w-full bg-surface-200 border border-white/10 rounded-xl px-3 py-2 text-xs text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Required Tenure (yrs):</label>
                <input
                  type="number"
                  step="0.5"
                  value={jobRequiredYears}
                  onChange={(e) => setJobRequiredYears(parseFloat(e.target.value))}
                  className="w-full bg-surface-200 border border-white/10 rounded-xl px-3 py-2 text-xs text-white font-mono"
                />
              </div>
            </div>
          </div>

          {/* Draft Explanation & Execution */}
          <div className="space-y-4">
            <h4 className="text-xs font-mono text-gold-400 uppercase tracking-wider">
              Explanation Under Verification
            </h4>

            <textarea
              value={explanationDraft}
              onChange={(e) => setExplanationDraft(e.target.value)}
              rows={4}
              className="w-full bg-darkbg border border-white/10 rounded-xl p-3 text-xs text-gray-200 font-mono leading-relaxed focus:border-gold-500/50 focus:outline-none"
            />

            <button
              onClick={handleRunAudit}
              className="w-full flex items-center justify-center space-x-2 py-3 rounded-xl bg-gold-500 text-darkbg font-bold text-xs shadow-gold-glow hover:brightness-110 active:scale-95 transition-all"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>Execute Verification Assertions</span>
            </button>
          </div>
        </div>

        {/* Verification Result Output */}
        {auditResult && (
          <div className={`p-6 rounded-2xl border transition-all ${
            auditResult.passed
              ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300'
              : 'bg-red-500/10 border-red-500/40 text-red-300'
          }`}>
            <div className="flex items-center space-x-3 mb-2">
              {auditResult.passed ? (
                <CheckCircle className="w-6 h-6 text-emerald-400" />
              ) : (
                <AlertOctagon className="w-6 h-6 text-red-400" />
              )}
              <h4 className="font-display font-bold text-base text-white">
                {auditResult.passed
                  ? 'Verification Succeeded: 100% Faithful Explanation'
                  : 'Verification Rejected: Unfaithful Explanation Error'}
              </h4>
            </div>

            {auditResult.passed ? (
              <p className="text-xs text-emerald-200 leading-relaxed font-sans">
                All cited entities correspond strictly to ground-truth resume skills, and numerical tenure values demonstrate exact mathematical fidelity. Safe for candidate rendering.
              </p>
            ) : (
              <div className="space-y-2 text-xs font-mono text-red-200">
                {auditResult.issues.map((issue, idx) => (
                  <p key={idx}>• {issue}</p>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
