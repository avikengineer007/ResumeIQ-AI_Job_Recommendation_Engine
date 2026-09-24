import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ThreeBackground from './components/ThreeBackground';
import RecommendationsView from './components/RecommendationsView';
import JobCatalogView from './components/JobCatalogView';
import ResumeStudio from './components/ResumeStudio';
import ExplainabilityDeepDive from './components/ExplainabilityDeepDive';
import { MOCK_RESUMES, checkBackendHealth } from './services/api';
import { Sparkles, Shield, Cpu, Database, Award } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('recommendations');
  const [allResumes, setAllResumes] = useState(MOCK_RESUMES);
  const [activeResume, setActiveResume] = useState(MOCK_RESUMES[0]);
  const [backendStatus, setBackendStatus] = useState({ online: false, data: {} });

  useEffect(() => {
    async function checkHealth() {
      const status = await checkBackendHealth();
      setBackendStatus(status);
    }
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-screen bg-darkbg text-gray-100 flex flex-col font-sans selection:bg-gold-500/30 selection:text-gold-200">
      {/* Ambient 3D Particle Constellation Background */}
      <ThreeBackground />

      {/* Main App Container */}
      <div className="relative z-10 flex flex-col min-h-screen">
        {/* Navigation Bar */}
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          backendStatus={backendStatus}
          activeResume={activeResume}
          setActiveResume={setActiveResume}
          allResumes={allResumes}
        />

        {/* Dynamic Content View */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {activeTab === 'recommendations' && (
            <RecommendationsView activeResume={activeResume} />
          )}

          {activeTab === 'jobs' && (
            <JobCatalogView activeResume={activeResume} />
          )}

          {activeTab === 'resume' && (
            <ResumeStudio
              activeResume={activeResume}
              setActiveResume={setActiveResume}
              setAllResumes={setAllResumes}
              onReRunRecommendations={() => setActiveTab('recommendations')}
            />
          )}

          {activeTab === 'explainability' && (
            <ExplainabilityDeepDive />
          )}
        </main>

        {/* Global Footer */}
        <footer className="mt-auto border-t border-surface-border bg-darkbg/90 backdrop-blur-md py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-gray-400">
            <div className="flex items-center space-x-3">
              <span className="font-display font-bold text-sm text-gold-gradient">
                ResumeIQ
              </span>
              <span>•</span>
              <span>AI Job Recommendation Engine</span>
              <span>•</span>
              <span className="font-mono text-[11px] text-gold-400">Zero-Fabrication Architecture</span>
            </div>

            <div className="flex flex-wrap items-center gap-6 font-mono text-[11px]">
              <span className="flex items-center space-x-1">
                <Cpu className="w-3.5 h-3.5 text-gold-400" />
                <span>Hybrid Rerank v0.4</span>
              </span>
              <span className="flex items-center space-x-1">
                <Shield className="w-3.5 h-3.5 text-emerald-400" />
                <span>Argon2id + PII Scrubbed</span>
              </span>
              <span className="flex items-center space-x-1">
                <Database className="w-3.5 h-3.5 text-blue-400" />
                <span>PostgreSQL + FAISS</span>
              </span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
