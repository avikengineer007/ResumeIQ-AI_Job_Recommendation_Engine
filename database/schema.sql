-- AI-Powered Skill-Aware Semantic Job Search and Personalized Recommendation System
-- Canonical Database Schema (Section 28)
-- PostgreSQL 15+ Compatibility

-- 1. Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Trigger Function for Automatic updated_at Timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Core Tables

-- Table 1: users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table 2: resumes
CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    raw_text TEXT,
    cleaned_text TEXT,
    sections_json JSONB DEFAULT '{}'::jsonb,
    total_years_experience NUMERIC(4, 1) DEFAULT 0.0,
    is_primary BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_resumes_updated_at
BEFORE UPDATE ON resumes
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table 3: skills
CREATE TABLE IF NOT EXISTS skills (
    id VARCHAR(128) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(128),
    parent_skill_id VARCHAR(128) REFERENCES skills(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table 4: jobs
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(128) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    work_mode VARCHAR(32) NOT NULL DEFAULT 'remote', -- remote, hybrid, onsite
    required_years_experience NUMERIC(4, 1) NOT NULL DEFAULT 0.0,
    description TEXT,
    raw_json JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_jobs_updated_at
BEFORE UPDATE ON jobs
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table 5: job_skills
CREATE TABLE IF NOT EXISTS job_skills (
    id BIGSERIAL PRIMARY KEY,
    job_id VARCHAR(128) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id VARCHAR(128) NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance VARCHAR(32) NOT NULL DEFAULT 'required', -- required, preferred, bonus
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_job_skill UNIQUE (job_id, skill_id)
);

-- Table 6: resume_skills
CREATE TABLE IF NOT EXISTS resume_skills (
    id BIGSERIAL PRIMARY KEY,
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    skill_id VARCHAR(128) NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency VARCHAR(32) DEFAULT 'intermediate',
    source_section VARCHAR(64),
    confidence NUMERIC(4, 3) NOT NULL DEFAULT 1.000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_resume_skill UNIQUE (resume_id, skill_id)
);

-- Table 7: user_preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    target_role VARCHAR(255),
    preferred_locations JSONB NOT NULL DEFAULT '[]'::jsonb,
    preferred_work_modes JSONB NOT NULL DEFAULT '[]'::jsonb,
    min_salary NUMERIC(12, 2),
    require_location BOOLEAN NOT NULL DEFAULT FALSE,
    require_work_mode BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_user_preferences_updated_at
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Table 8: search_history
CREATE TABLE IF NOT EXISTS search_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query_text TEXT,
    filters_applied JSONB NOT NULL DEFAULT '{}'::jsonb,
    results_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table 9: recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resume_id UUID NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    job_id VARCHAR(128) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    model_version VARCHAR(64) NOT NULL DEFAULT 'hybrid-rerank-0.4',
    rank INTEGER NOT NULL,
    score NUMERIC(6, 4) NOT NULL,
    calibrated_probability NUMERIC(6, 4),
    explanation_json JSONB DEFAULT '{}'::jsonb,
    scores_breakdown_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table 10: feedback
CREATE TABLE IF NOT EXISTS feedback (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(128) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    recommendation_id BIGINT REFERENCES recommendations(id) ON DELETE SET NULL,
    action VARCHAR(32) NOT NULL, -- clicked, applied, dismissed, saved, thumbs_up, thumbs_down
    feedback_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table 11: saved_jobs
CREATE TABLE IF NOT EXISTS saved_jobs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(128) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_saved_job UNIQUE (user_id, job_id)
);

-- 4. B-Tree & Filter Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
CREATE INDEX IF NOT EXISTS idx_jobs_is_active_work_mode ON jobs(is_active, work_mode);
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_job_skills_job_id ON job_skills(job_id);
CREATE INDEX IF NOT EXISTS idx_job_skills_skill_id ON job_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_resume_skills_resume_id ON resume_skills(resume_id);
CREATE INDEX IF NOT EXISTS idx_resume_skills_skill_id ON resume_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_user_created ON search_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_created ON recommendations(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recommendations_job_id ON recommendations(job_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user_job ON feedback(user_id, job_id);
CREATE INDEX IF NOT EXISTS idx_saved_jobs_user_id ON saved_jobs(user_id);

-- 5. GIN Indexes for Structured JSONB Querying
CREATE INDEX IF NOT EXISTS idx_resumes_sections_gin ON resumes USING gin(sections_json);
CREATE INDEX IF NOT EXISTS idx_user_pref_locations_gin ON user_preferences USING gin(preferred_locations);
CREATE INDEX IF NOT EXISTS idx_user_pref_modes_gin ON user_preferences USING gin(preferred_work_modes);
CREATE INDEX IF NOT EXISTS idx_recommendations_explanation_gin ON recommendations USING gin(explanation_json);
CREATE INDEX IF NOT EXISTS idx_jobs_raw_json_gin ON jobs USING gin(raw_json);
