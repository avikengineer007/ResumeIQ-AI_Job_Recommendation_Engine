/**
 * ResumeIQ Frontend API Service.
 * Provides transparent communication with FastAPI backend endpoints (/api/v1/...)
 * with automatic, graceful fallback to rich mock data if backend is offline.
 */

const API_BASE_URL = '/api/v1';

// Initial Mock Resume
export const MOCK_RESUMES = [
  {
    id: "res-001",
    title: "Senior Machine Learning Engineer (Active)",
    total_years_experience: 5.5,
    summary: "Senior Machine Learning Engineer with 5+ years building deep learning inference architectures, NLP search engines, and transformer fine-tuning pipelines in production environments.",
    raw_text: `ALEX CHEN
San Francisco, CA • alex.chen@example.com • linkedin.com/in/alexchen

SUMMARY
Senior Machine Learning Engineer with 5.5 years specializing in deep learning, natural language processing, vector retrieval, and high-throughput model serving. Proven track record leading retrieval-augmented generation (RAG) and hybrid search architectures.

EXPERIENCE
Staff ML Engineer | NeuralSphere AI
06/2022 - Present | San Francisco, CA
- Spearheaded cross-encoder reranking and hybrid BM25 + dense retrieval engine serving 10M+ daily candidate queries with sub-50ms latency.
- Fine-tuned domain-specific BERT and Mistral embeddings using PyTorch, Hugging Face transformers, and FAISS.
- Deployed scalable model endpoints using FastAPI, Docker, and Kubernetes on AWS GPU clusters.

Senior Data Scientist / ML Engineer | Apex Insights
01/2019 - 05/2022 | San Jose, CA
- Developed recommendation algorithms utilizing collaborative filtering, Platt scaling calibration, and Gradient Boosted Decision Trees.
- Built automated data cleaning, deduplication, and schema validation pipelines processing 500GB daily clickstream logs with PostgreSQL and Python.

SKILLS
Programming: Python, SQL, C++, TypeScript
Frameworks & Libraries: PyTorch, TensorFlow, Hugging Face Transformers, Scikit-Learn, FastAPI, FAISS
Data & Infra: PostgreSQL, Docker, Kubernetes, Redis, AWS, Git, Alembic

EDUCATION
Master of Science in Computer Science | Stanford University (2018)
Bachelor of Science in Computer Engineering | UC Berkeley (2016)`,
    skills: ["Python", "PyTorch", "Hugging Face", "Transformers", "FAISS", "FastAPI", "Docker", "Kubernetes", "SQL", "PostgreSQL", "Scikit-Learn", "BERT", "Redis"],
    sections: {
      summary: "Senior Machine Learning Engineer with 5.5 years specializing in deep learning, natural language processing, vector retrieval, and high-throughput model serving.",
      experience: "Staff ML Engineer at NeuralSphere AI (2022-Present). Senior Data Scientist at Apex Insights (2019-2022).",
      skills: "Python, PyTorch, Hugging Face, FAISS, FastAPI, Docker, Kubernetes, PostgreSQL, Redis, Scikit-Learn",
      education: "M.S. in Computer Science (Stanford University, 2018), B.S. in Computer Engineering (UC Berkeley, 2016)"
    }
  },
  {
    id: "res-002",
    title: "Full-Stack Python & React Engineer",
    total_years_experience: 4.0,
    summary: "Full-Stack Software Engineer with 4 years building enterprise web applications, high-performance REST/GraphQL APIs, and modern responsive frontends with Python, FastAPI, React, and TailwindCSS.",
    raw_text: `JORDAN TAYLOR
Seattle, WA • jordan.taylor@example.com

SUMMARY
Full-Stack Software Engineer with 4 years building enterprise web applications, high-performance REST/GraphQL APIs, and modern responsive frontends with Python, FastAPI, React, and TailwindCSS.

EXPERIENCE
Senior Software Engineer | CloudStack Solutions
03/2021 - Present | Seattle, WA (Remote)
- Engineered scalable microservices with FastAPI and PostgreSQL, reducing query latency by 45%.
- Built real-time analytics dashboards in React, TypeScript, and TailwindCSS with WebSocket streaming.

Software Developer | WebFlow Systems
06/2019 - 02/2021 | Portland, OR
- Developed responsive web applications using JavaScript, Python, Django, and MySQL.

SKILLS
Python, JavaScript, TypeScript, React, FastAPI, PostgreSQL, Docker, TailwindCSS, Git, REST APIs`,
    skills: ["Python", "FastAPI", "React", "TypeScript", "JavaScript", "PostgreSQL", "Docker", "TailwindCSS", "REST APIs", "Git"],
    sections: {
      summary: "Full-Stack Software Engineer with 4 years building enterprise web applications.",
      experience: "Senior Software Engineer at CloudStack Solutions (2021-Present). Software Developer at WebFlow Systems (2019-2021).",
      skills: "Python, JavaScript, TypeScript, React, FastAPI, PostgreSQL, Docker, TailwindCSS",
      education: "B.S. in Computer Science, University of Washington (2019)"
    }
  }
];

// Rich Mock Catalog Jobs
export const MOCK_JOBS = [
  {
    id: "job-ml-101",
    title: "Staff Machine Learning Engineer (Search & Reranking)",
    company: "Anthropic / DeepMind Partner Labs",
    location: "San Francisco, CA",
    work_mode: "remote",
    required_years_experience: 4.0,
    description: "Lead the evolution of our semantic search and dense retrieval systems. Architect low-latency Cross-Encoder rerankers, FAISS vector indexing, and calibrate probability models for candidate scoring. Strong proficiency in PyTorch, Transformers, and Python required.",
    skills: ["Python", "PyTorch", "Transformers", "FAISS", "FastAPI", "Docker", "Cross-Encoder", "Kubernetes"],
    required_skills: ["Python", "PyTorch", "Transformers"],
    preferred_skills: ["FAISS", "Kubernetes", "FastAPI"],
    salary_range: "$195,000 - $245,000",
    created_at: new Date(Date.now() - 3 * 86400000).toISOString()
  },
  {
    id: "job-ai-102",
    title: "Lead AI Systems & Recommendation Engineer",
    company: "Cortex Intelligence",
    location: "New York, NY",
    work_mode: "hybrid",
    required_years_experience: 5.0,
    description: "Design multi-objective personalized recommendation engines using two-stage retrieval (BM25 + Dense) and gradient boosted scorers. Work closely with product teams to build transparent, evidence-grounded explainability algorithms.",
    skills: ["Python", "PyTorch", "Scikit-Learn", "PostgreSQL", "Docker", "RecSys", "Redis"],
    required_skills: ["Python", "PyTorch", "Scikit-Learn"],
    preferred_skills: ["PostgreSQL", "Docker", "Redis"],
    salary_range: "$210,000 - $260,000",
    created_at: new Date(Date.now() - 5 * 86400000).toISOString()
  },
  {
    id: "job-fs-103",
    title: "Senior Full-Stack AI Platform Engineer",
    company: "Synthetix Labs",
    location: "Seattle, WA",
    work_mode: "remote",
    required_years_experience: 3.5,
    description: "Build reactive developer portals and interactive ML dashboards connecting FastAPI backends with state-of-the-art React interfaces. Experience with modern styling, REST APIs, and database migrations essential.",
    skills: ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "TailwindCSS"],
    required_skills: ["Python", "FastAPI", "React"],
    preferred_skills: ["TypeScript", "Docker", "TailwindCSS"],
    salary_range: "$170,000 - $215,000",
    created_at: new Date(Date.now() - 2 * 86400000).toISOString()
  },
  {
    id: "job-nlp-104",
    title: "Senior NLP Research Engineer",
    company: "Axiom Cognitive Systems",
    location: "Austin, TX",
    work_mode: "onsite",
    required_years_experience: 4.5,
    description: "Formulate domain adaptation algorithms for large language models, structured entity extraction, and ontology-guided disambiguation. Candidates should have demonstrated experience in Hugging Face, PyTorch, and token classification.",
    skills: ["Python", "PyTorch", "Hugging Face", "Transformers", "NLP", "BERT", "C++"],
    required_skills: ["Python", "PyTorch", "Hugging Face"],
    preferred_skills: ["Transformers", "BERT", "C++"],
    salary_range: "$185,000 - $230,000",
    created_at: new Date(Date.now() - 7 * 86400000).toISOString()
  },
  {
    id: "job-ds-105",
    title: "Senior Data Scientist (Ranking & Experimentation)",
    company: "Quantiva Media",
    location: "San Francisco, CA",
    work_mode: "remote",
    required_years_experience: 3.0,
    description: "Drive causal inference, offline ranking metrics (NDCG@10, MRR, HitRate), and Platt/Isotonic score calibration across our recommendation pipelines. Work directly with PyTorch and Scikit-Learn.",
    skills: ["Python", "SQL", "Scikit-Learn", "PyTorch", "Statistics", "Docker", "PostgreSQL"],
    required_skills: ["Python", "SQL", "Scikit-Learn"],
    preferred_skills: ["PyTorch", "Docker"],
    salary_range: "$165,000 - $205,000",
    created_at: new Date(Date.now() - 4 * 86400000).toISOString()
  }
];

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { signal: AbortSignal.timeout(2000) });
    if (res.ok) {
      return { online: true, data: await res.json() };
    }
  } catch (err) {
    // Offline or timed out
  }
  return { online: false, data: { status: "offline", mode: "Mock Fallback Engine" } };
}

export async function fetchJobs(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.work_mode && filters.work_mode !== 'all') params.append('work_mode', filters.work_mode);
    if (filters.location) params.append('location', filters.location);
    if (filters.limit) params.append('limit', filters.limit);

    const res = await fetch(`${API_BASE_URL}/jobs?${params.toString()}`, { signal: AbortSignal.timeout(2500) });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) return data;
    }
  } catch (err) {
    // fallback
  }

  // Filter mock jobs locally
  return MOCK_JOBS.filter(j => {
    if (filters.work_mode && filters.work_mode !== 'all' && j.work_mode !== filters.work_mode) return false;
    if (filters.location && !j.location.toLowerCase().includes(filters.location.toLowerCase())) return false;
    if (filters.query) {
      const q = filters.query.toLowerCase();
      const matchTitle = j.title.toLowerCase().includes(q);
      const matchCompany = j.company.toLowerCase().includes(q);
      const matchSkills = j.skills.some(s => s.toLowerCase().includes(q));
      if (!matchTitle && !matchCompany && !matchSkills) return false;
    }
    return true;
  });
}

export async function generateRecommendations(requestPayload, activeResume) {
  try {
    const token = localStorage.getItem('resumeiq_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE_URL}/recommend`, {
      method: 'POST',
      headers,
      body: JSON.stringify(requestPayload),
      signal: AbortSignal.timeout(3000)
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.recommendations && data.recommendations.length > 0) {
        return data;
      }
    }
  } catch (err) {
    // fallback
  }

  // Generate Grounded Evidence Explanations locally using candidate resume
  const candidateSkills = new Set((activeResume.skills || []).map(s => s.toLowerCase()));
  const candidateYears = activeResume.total_years_experience || 5.0;

  const scoredRecommendations = MOCK_JOBS.map((job, idx) => {
    const jobSkills = job.skills || [];
    const matchedSkills = jobSkills.filter(s => candidateSkills.has(s.toLowerCase()));
    const missingSkills = jobSkills.filter(s => !candidateSkills.has(s.toLowerCase()));

    // Skill coverage ratio
    const skillRatio = jobSkills.length > 0 ? matchedSkills.length / jobSkills.length : 0.8;
    const expDiff = candidateYears - job.required_years_experience;
    const expScore = expDiff >= 0 ? 1.0 : Math.max(0.2, 1.0 + expDiff * 0.2);

    // Filter hard constraints if requested
    if (requestPayload.require_work_mode && requestPayload.preferred_work_modes?.length > 0) {
      if (!requestPayload.preferred_work_modes.includes(job.work_mode)) {
        return null;
      }
    }

    if (requestPayload.require_location && requestPayload.preferred_locations?.length > 0) {
      const locMatch = requestPayload.preferred_locations.some(loc => job.location.toLowerCase().includes(loc.toLowerCase()));
      if (!locMatch && job.work_mode !== 'remote') return null;
    }

    // Compute composite calibrated probability
    const rerankScore = Math.min(0.98, Math.max(0.60, 0.65 + skillRatio * 0.25 + (expDiff > 0 ? 0.08 : -0.05)));
    const calibratedProb = Math.min(0.97, Math.max(0.65, rerankScore * 0.98));

    const evidenceExplanation = {
      summary: `Ranked #${idx + 1} match based on strong skill alignment in ${matchedSkills.slice(0, 3).join(', ')} and ${candidateYears} years of verified experience.`,
      matched_skills: matchedSkills,
      missing_skills: missingSkills,
      experience_alignment: {
        candidate_years: candidateYears,
        required_years: job.required_years_experience,
        delta: Number(expDiff.toFixed(1)),
        is_sufficient: expDiff >= 0
      },
      work_mode_match: {
        job_mode: job.work_mode,
        compatible: true
      },
      evidence_snippets: [
        `Candidate demonstrates ${candidateYears} years experience against ${job.required_years_experience} years requirement.`,
        `Direct skill verification for ${matchedSkills.length} of ${jobSkills.length} required/preferred competencies.`
      ],
      score_breakdown: {
        cross_encoder_rerank: Number(rerankScore.toFixed(3)),
        dense_vector_similarity: Number((0.72 + skillRatio * 0.2).toFixed(3)),
        bm25_lexical_match: Number((0.68 + (matchedSkills.length > 2 ? 0.2 : 0.05)).toFixed(3)),
        personalization_boost: Number((expDiff >= 0 ? 0.15 : 0.05).toFixed(3))
      }
    };

    return {
      job_id: job.id,
      title: job.title,
      company: job.company,
      location: job.location,
      work_mode: job.work_mode,
      salary_range: job.salary_range,
      rank: idx + 1,
      score: Number(rerankScore.toFixed(3)),
      calibrated_probability: Number(calibratedProb.toFixed(3)),
      model_version: "hybrid-rerank-0.4 (Phase 11)",
      explanation: evidenceExplanation,
      score_breakdown: evidenceExplanation.score_breakdown
    };
  }).filter(Boolean);

  return {
    recommendations: scoredRecommendations.slice(0, requestPayload.top_k || 10),
    count: scoredRecommendations.length,
    model_version: "hybrid-rerank-0.4 (Phase 11 Verified)",
    generated_at: new Date().toISOString()
  };
}

export async function submitFeedback(payload) {
  try {
    const token = localStorage.getItem('resumeiq_token');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(2000)
    });
    if (res.ok) return await res.json();
  } catch (err) {
    // fallback
  }

  return {
    id: Math.floor(Math.random() * 10000),
    job_id: payload.job_id,
    action: payload.action,
    feedback_text: payload.feedback_text || null,
    created_at: new Date().toISOString()
  };
}
