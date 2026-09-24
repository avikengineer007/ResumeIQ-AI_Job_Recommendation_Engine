"""Evidence object builder for evidence-grounded explainability.

Extracts, structures, and links factual evidence directly from candidate resumes,
job postings, skill taxonomies, and multi-objective recommendation scores.
"""

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from src.recommendation.personalization import (
    CandidatePreferences,
    PersonalizedJobScore,
)


@dataclass
class SkillEvidence:
    """Factual evidence for an individual skill comparison."""

    skill_id: str
    skill_name: str
    match_type: str  # "exact", "parent", "related", "fuzzy", "missing"
    importance: str = "required"  # "required", "preferred", "bonus"
    confidence: float = 1.0
    source_span: str | None = None
    job_context: str | None = None


@dataclass
class ExperienceEvidence:
    """Factual evidence comparing experience requirements."""

    candidate_years: float
    required_years: float
    gap_years: float  # required - candidate (<= 0 means candidate meets/exceeds)
    meets_requirement: bool
    seniority_alignment: str  # "matched", "underqualified", "overqualified"


@dataclass
class RoleEvidence:
    """Factual evidence for role title and domain alignment."""

    candidate_role: str
    job_title: str
    matched_keywords: list[str] = field(default_factory=list)
    alignment_score: float = 0.5


@dataclass
class LocationEvidence:
    """Factual evidence for location and work arrangement alignment."""

    job_location: str
    job_work_mode: str
    preferred_locations: list[str] = field(default_factory=list)
    preferred_work_modes: list[str] = field(default_factory=list)
    is_match: bool = True
    match_reason: str = "Open to location and work arrangement"


@dataclass
class ScoreEvidence:
    """Factual evidence breaking down recommendation score contributions."""

    final_score: float
    rank: int
    calibrated_probability: float | None = None
    component_scores: dict[str, float] = field(default_factory=dict)
    primary_driver: str = "semantic_similarity"


@dataclass
class ExplanationEvidence:
    """Complete, structured evidence container for a single candidate-job recommendation."""

    job_id: str
    job_title: str
    company: str
    matched_skills: list[SkillEvidence] = field(default_factory=list)
    missing_skills: list[SkillEvidence] = field(default_factory=list)
    experience: ExperienceEvidence = field(
        default_factory=lambda: ExperienceEvidence(
            candidate_years=0.0,
            required_years=0.0,
            gap_years=0.0,
            meets_requirement=True,
            seniority_alignment="matched",
        )
    )
    role: RoleEvidence = field(
        default_factory=lambda: RoleEvidence(candidate_role="", job_title="")
    )
    location: LocationEvidence = field(
        default_factory=lambda: LocationEvidence(job_location="", job_work_mode="")
    )
    scores: ScoreEvidence = field(
        default_factory=lambda: ScoreEvidence(final_score=0.0, rank=1)
    )
    provenance_snippets: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert evidence container to serializable dictionary."""
        return asdict(self)

    @property
    def matched_skill_names(self) -> list[str]:
        return [s.skill_name for s in self.matched_skills]

    @property
    def missing_skill_names(self) -> list[str]:
        return [s.skill_name for s in self.missing_skills]


def _safe_float(val: Any, default: float = 0.0) -> float:
    """Safely convert any value to float with graceful default fallback."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def _extract_skill_set(skills_raw: Any) -> list[dict[str, str]]:
    """Helper to convert skills from varying representations to normalized list of dicts."""
    if skills_raw is None:
        return []
    if hasattr(skills_raw, "tolist"):
        skills_raw = skills_raw.tolist()
    if isinstance(skills_raw, str):
        skills_raw = [s.strip() for s in skills_raw.split(",") if s.strip()]
    if not isinstance(skills_raw, (list, tuple, set)):
        return []

    extracted = []
    for item in skills_raw:
        if item is None:
            continue
        if isinstance(item, dict):
            s_name = str(item.get("name") or item.get("skill_id") or "").strip()
            s_id = str(item.get("skill_id") or s_name.lower().replace(" ", "_"))
            if s_name:
                extracted.append({"skill_id": s_id, "skill_name": s_name})
        elif hasattr(item, "name") or hasattr(item, "skill_id"):
            s_name = str(
                getattr(item, "name", "") or getattr(item, "skill_id", "")
            ).strip()
            s_id = str(getattr(item, "skill_id", s_name.lower().replace(" ", "_")))
            if s_name:
                extracted.append({"skill_id": s_id, "skill_name": s_name})
        elif isinstance(item, str) and item.strip():
            extracted.append(
                {
                    "skill_id": item.strip().lower().replace(" ", "_"),
                    "skill_name": item.strip(),
                }
            )
        elif isinstance(item, (int, float)):
            s_name = str(item).strip()
            extracted.append({"skill_id": s_name, "skill_name": s_name})
    return extracted


class EvidenceBuilder:
    """Builds verifiable ExplanationEvidence objects from pipeline components."""

    def __init__(self, skill_taxonomy: Any = None) -> None:
        self.taxonomy = skill_taxonomy

    def build_evidence(
        self,
        candidate_resume: dict[str, Any],
        job_posting: dict[str, Any],
        score_info: PersonalizedJobScore | dict[str, Any] | None = None,
        preferences: CandidatePreferences | None = None,
        calibrated_probability: float | None = None,
    ) -> ExplanationEvidence:
        """Extract and structure all factual evidence linking candidate to job."""
        job_id = str(
            job_posting.get("job_id") or job_posting.get("id") or "unknown_job"
        )
        job_title = str(
            job_posting.get("title") or job_posting.get("role") or "Job Position"
        )
        company = str(job_posting.get("company") or "Company")

        # 1. Skill Evidence Analysis
        c_skills_list = _extract_skill_set(candidate_resume.get("skills", []))
        j_skills_list = _extract_skill_set(job_posting.get("skills", []))

        c_names_map = {s["skill_name"].lower(): s for s in c_skills_list}
        c_ids_map = {s["skill_id"]: s for s in c_skills_list}

        matched_skills: list[SkillEvidence] = []
        missing_skills: list[SkillEvidence] = []

        # Determine job required vs preferred skills
        req_skills_raw = _extract_skill_set(job_posting.get("required_skills", []))
        req_ids = {s["skill_id"] for s in req_skills_raw}

        for j_skill in j_skills_list:
            j_id = j_skill["skill_id"]
            j_name = j_skill["skill_name"]
            j_name_lower = j_name.lower()
            importance = "required" if (j_id in req_ids or not req_ids) else "preferred"

            # Check direct match
            if j_id in c_ids_map or j_name_lower in c_names_map:
                matched_skills.append(
                    SkillEvidence(
                        skill_id=j_id,
                        skill_name=j_name,
                        match_type="exact",
                        importance=importance,
                        confidence=1.0,
                    )
                )
            else:
                # Check taxonomy hierarchy if available
                taxonomy_match = None
                if self.taxonomy is not None:
                    # check parent or related
                    j_parents = set(self.taxonomy.get_parents(j_id))
                    j_related = set(self.taxonomy.get_related(j_id))
                    for c_id, c_data in c_ids_map.items():
                        if c_id in j_parents:
                            taxonomy_match = ("parent", c_data["skill_name"], 0.8)
                            break
                        elif c_id in j_related:
                            taxonomy_match = ("related", c_data["skill_name"], 0.7)
                            break

                if taxonomy_match:
                    match_type, rel_name, conf = taxonomy_match
                    matched_skills.append(
                        SkillEvidence(
                            skill_id=j_id,
                            skill_name=j_name,
                            match_type=match_type,
                            importance=importance,
                            confidence=conf,
                            job_context=f"Candidate has {match_type} skill {rel_name}",
                        )
                    )
                else:
                    missing_skills.append(
                        SkillEvidence(
                            skill_id=j_id,
                            skill_name=j_name,
                            match_type="missing",
                            importance=importance,
                            confidence=0.0,
                        )
                    )

        # 2. Experience Evidence
        c_years_raw = candidate_resume.get("total_years")
        if c_years_raw is None:
            c_years_raw = candidate_resume.get("years_of_experience", 0.0)
        candidate_years = _safe_float(c_years_raw, 0.0)

        j_years_raw = job_posting.get("required_years")
        if j_years_raw is None:
            j_years_raw = job_posting.get("min_experience_years")
        if j_years_raw is None:
            j_years_raw = job_posting.get("years_required", 0.0)
        required_years = _safe_float(j_years_raw, 0.0)

        gap_years = max(0.0, required_years - candidate_years)
        meets_exp = candidate_years >= required_years

        if candidate_years >= required_years + 3.0 and required_years > 0:
            seniority = "overqualified"
        elif candidate_years >= required_years:
            seniority = "matched"
        else:
            seniority = "underqualified"

        exp_evidence = ExperienceEvidence(
            candidate_years=round(candidate_years, 1),
            required_years=round(required_years, 1),
            gap_years=round(gap_years, 1),
            meets_requirement=meets_exp,
            seniority_alignment=seniority,
        )

        # 3. Role Evidence
        target_role = ""
        if preferences and preferences.target_role:
            target_role = preferences.target_role
        else:
            pref_raw = candidate_resume.get("preferences", {})
            if isinstance(pref_raw, dict):
                target_role = str(pref_raw.get("role", pref_raw.get("target_role", "")))

        cand_tokens = set(re.findall(r"\b\w+\b", target_role.lower()))
        job_tokens = set(re.findall(r"\b\w+\b", job_title.lower()))
        stopwords = {
            "senior",
            "junior",
            "lead",
            "staff",
            "principal",
            "developer",
            "engineer",
        }
        matched_kw = list(
            (cand_tokens & job_tokens) - stopwords or (cand_tokens & job_tokens)
        )

        role_evidence = RoleEvidence(
            candidate_role=target_role,
            job_title=job_title,
            matched_keywords=matched_kw,
            alignment_score=len(matched_kw) / max(1, len(cand_tokens | job_tokens)),
        )

        # 4. Location & Work Arrangement Evidence
        job_loc = str(job_posting.get("location") or "Remote")
        job_mode = str(job_posting.get("work_mode") or "remote").lower().strip()

        pref_locs = []
        pref_modes = []
        if preferences:
            pref_locs = preferences.preferred_locations or []
            pref_modes = preferences.preferred_work_modes or []
        else:
            pref_raw = candidate_resume.get("preferences", {})
            if isinstance(pref_raw, dict):
                pref_locs = pref_raw.get("locations", []) or []
                pref_modes = pref_raw.get("work_modes", []) or []

        is_loc_match = True
        reason = "Compatible location and arrangement"

        if job_mode == "remote":
            reason = "Fully remote position matches candidate availability"
        elif pref_modes and job_mode not in [m.lower().strip() for m in pref_modes]:
            is_loc_match = False
            reason = f"Job is {job_mode}, which differs from preferences ({', '.join(pref_modes)})"
        elif pref_locs and not any(p.lower() in job_loc.lower() for p in pref_locs):
            is_loc_match = False
            reason = f"Job located in {job_loc}, outside preferred locations ({', '.join(pref_locs)})"
        else:
            reason = f"Job location {job_loc} ({job_mode}) aligns with preferences"

        loc_evidence = LocationEvidence(
            job_location=job_loc,
            job_work_mode=job_mode,
            preferred_locations=pref_locs,
            preferred_work_modes=pref_modes,
            is_match=is_loc_match,
            match_reason=reason,
        )

        # 5. Score Evidence & Primary Driver
        final_score = 0.0
        rank = 1
        comp_scores: dict[str, float] = {}

        if isinstance(score_info, PersonalizedJobScore):
            final_score = score_info.final_score
            rank = score_info.rank
            comp_scores = {
                "rerank_score": score_info.s_rerank,
                "semantic_score": score_info.s_sem,
                "skill_score": score_info.s_skill,
                "experience_score": score_info.s_exp,
                "role_score": score_info.s_role,
                "location_score": score_info.s_loc,
                "work_mode_score": score_info.s_mode,
            }
        elif isinstance(score_info, dict):
            final_score = _safe_float(score_info.get("final_score", 0.0))
            rank = int(_safe_float(score_info.get("rank", 1.0)))
            comp_scores = {
                k: _safe_float(v)
                for k, v in score_info.items()
                if k not in ["final_score", "rank", "job_id"]
            }

        driver_map = {
            "rerank_score": "Cross-Encoder Relevance",
            "semantic_score": "Semantic Context Match",
            "skill_score": "Verified Skill Overlap",
            "experience_score": "Experience & Seniority Fit",
            "role_score": "Role Alignment",
        }
        primary_driver = "Semantic Relevance"
        if comp_scores:
            best_comp = max(comp_scores.items(), key=lambda x: x[1])[0]
            primary_driver = driver_map.get(
                best_comp, best_comp.replace("_", " ").title()
            )

        score_evidence = ScoreEvidence(
            final_score=round(final_score, 4),
            rank=rank,
            calibrated_probability=(
                round(_safe_float(calibrated_probability), 4)
                if calibrated_probability is not None
                else None
            ),
            component_scores=comp_scores,
            primary_driver=primary_driver,
        )

        # 6. Provenance Text Snippets
        snippets: list[str] = []
        resume_summary = candidate_resume.get("summary") or candidate_resume.get(
            "text", ""
        )
        if isinstance(resume_summary, str) and resume_summary.strip():
            snippets.append(f"Resume: {resume_summary[:160].strip()}...")
        job_desc = job_posting.get("description") or job_posting.get("text", "")
        if isinstance(job_desc, str) and job_desc.strip():
            snippets.append(f"Job Description: {job_desc[:160].strip()}...")

        return ExplanationEvidence(
            job_id=job_id,
            job_title=job_title,
            company=company,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            experience=exp_evidence,
            role=role_evidence,
            location=loc_evidence,
            scores=score_evidence,
            provenance_snippets=snippets,
        )
