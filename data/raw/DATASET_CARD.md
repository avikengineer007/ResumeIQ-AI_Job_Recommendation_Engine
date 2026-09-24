# Dataset Card: Job & Resume Benchmark

## Overview
This benchmark evaluates skill-aware semantic job search and recommendation models.

## Provenance and Licensing
- Job datasets: Open and synthetic job postings (licenses tracked per batch).
- Resumes: Anonymized volunteer profiles and synthetic profiles with explicit consent.
- Skill Taxonomy: Curated subset inspired by ESCO / O*NET classifications.

## Privacy & Ethical Guarantees
- Zero PII: Raw personal identifying information (names, emails, phones, physical addresses) is strictly stripped prior to downstream NLP or embedding pipelines.
- Sensitive Attributes: Protected categories (gender, race, religion, sexual orientation, disability, age) are never extracted, stored, or incorporated as features.
