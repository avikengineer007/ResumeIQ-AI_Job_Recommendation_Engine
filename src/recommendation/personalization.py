"""Personalization and constraint-aware ranking module.

Architecture Rules:
1. Hard Constraints (require_location, require_work_mode) are strictly enforced
   as filters BEFORE scoring to prevent compensating features from surfacing invalid jobs.
2. Soft Preferences (experience gap, role alignment, location preference, mode preference)
   are computed as continuous normalized components in [0.0, 1.0].
3. Final personalized score is computed via convex linear combination.
"""

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CandidatePreferences:
    target_role: str = ""
    years_of_experience: float = 0.0
    candidate_skills: list[str] = field(default_factory=list)
    preferred_locations: list[str] = field(default_factory=list)
    preferred_work_modes: list[str] = field(
        default_factory=list
    )  # remote, hybrid, onsite
    # Strict hard constraint flags
    require_location: bool = False
    require_work_mode: bool = False


@dataclass
class PersonalizedJobScore:
    job_id: str
    final_score: float
    rank: int
    s_rerank: float = 0.0
    s_sem: float = 0.0
    s_skill: float = 0.0
    s_exp: float = 0.0
    s_role: float = 0.0
    s_loc: float = 0.0
    s_mode: float = 0.0


def compute_experience_score(candidate_years: float, required_years: float) -> float:
    """Compute normalized experience alignment score in [0.0, 1.0].

    - Full credit (1.0) if candidate meets or exceeds requirements.
    - Exponential decay penalty if candidate falls below requirement.
    """
    if required_years <= 0.0 or candidate_years >= required_years:
        return 1.0

    gap = required_years - candidate_years
    # Decay rate lambda = 0.35: gap of 1 year -> 0.70, gap of 2 years -> 0.50
    # TODO(Phase 10): tune experience decay lambda on validation split
    return math.exp(-0.35 * gap)


def compute_role_score(candidate_role: str, job_title: str) -> float:
    """Compute role title lexical and semantic alignment score in [0.0, 1.0]."""
    if not candidate_role or not job_title:
        return 0.5  # Neutral prior if role unspecified

    c_words = set(re.findall(r"\b\w+\b", candidate_role.lower()))
    j_words = set(re.findall(r"\b\w+\b", job_title.lower()))

    # Ignore generic corporate words
    stopwords = {
        "senior",
        "junior",
        "lead",
        "staff",
        "principal",
        "manager",
        "engineer",
        "developer",
    }
    c_core = c_words - stopwords or c_words
    j_core = j_words - stopwords or j_words

    intersection = c_core.intersection(j_core)
    union = c_core.union(j_core)
    if not union:
        return 0.5

    jaccard = len(intersection) / float(len(union))
    return min(1.0, max(0.0, jaccard))


def compute_location_score(
    job_location: str, preferred_locations: Sequence[str]
) -> float:
    """Compute location alignment score in [0.0, 1.0]."""
    if not preferred_locations:
        return 1.0  # Open to any location

    job_loc_norm = job_location.lower().strip()
    if "remote" in job_loc_norm:
        return 0.95

    for pref in preferred_locations:
        pref_norm = pref.lower().strip()
        if pref_norm in job_loc_norm or job_loc_norm in pref_norm:
            return 1.0

    return 0.0


def compute_work_mode_score(job_mode: str, preferred_modes: Sequence[str]) -> float:
    """Compute work mode alignment score in [0.0, 1.0]."""
    if not preferred_modes:
        return 1.0  # Open to any work mode

    job_mode_norm = job_mode.lower().strip()
    for pref in preferred_modes:
        if pref.lower().strip() == job_mode_norm:
            return 1.0

    return 0.0


def filter_hard_constraints(
    candidates: Sequence[dict[str, Any]],
    preferences: CandidatePreferences,
) -> list[dict[str, Any]]:
    """Enforce strict hard constraints, filtering out jobs that violate required preferences.

    Hard constraints are applied as deterministic filters BEFORE scoring to ensure
    no linear combination can compensate for a disqualified attribute.
    """
    survivors: list[dict[str, Any]] = []

    for job in candidates:
        # Check Work Mode constraint
        if preferences.require_work_mode and preferences.preferred_work_modes:
            job_mode = str(job.get("work_mode", "")).lower().strip()
            allowed_modes = {
                m.lower().strip() for m in preferences.preferred_work_modes
            }
            if job_mode not in allowed_modes:
                continue

        # Check Location constraint
        if preferences.require_location and preferences.preferred_locations:
            job_loc = str(job.get("location", "")).lower().strip()
            job_mode = str(job.get("work_mode", "")).lower().strip()

            # Remote jobs satisfy location requirements unless user strictly requires onsite in location
            is_remote = "remote" in job_loc or job_mode == "remote"
            matches_pref = any(
                p.lower().strip() in job_loc or job_loc in p.lower().strip()
                for p in preferences.preferred_locations
            )
            if not (matches_pref or is_remote):
                continue

        survivors.append(job)

    return survivors


class PersonalizedScorer:
    """Computes personalized rankings over hard-filtered candidates using weighted multi-objective scoring."""

    def __init__(
        self,
        # TODO(Phase 10): tune personalization weights on validation split
        weights: dict[str, float] | None = None,
    ) -> None:
        # Defaults from configs/retrieval_config.yaml
        # TODO(Phase 10): tune on validation split (heuristic defaults)
        self.weights = weights or {
            "s_rerank": 0.35,
            "s_sem": 0.20,
            "s_skill": 0.25,
            "s_exp": 0.10,
            "s_role": 0.05,
            "s_loc": 0.025,
            "s_mode": 0.025,
        }
        total = sum(self.weights.values())
        self.norm_weights = (
            {k: v / total for k, v in self.weights.items()}
            if total > 0
            else self.weights
        )

    def score_candidates(
        self,
        candidates: Sequence[dict[str, Any]],
        preferences: CandidatePreferences,
        top_k: int = 10,
    ) -> list[PersonalizedJobScore]:
        """Filter candidates with hard constraints and rank survivors with soft personalized weights."""
        # Step 1: Hard Constraint Filtering
        filtered_candidates = filter_hard_constraints(candidates, preferences)
        if not filtered_candidates:
            return []

        # Step 2: Component Scoring
        scored_items: list[tuple[dict[str, Any], float, dict[str, float]]] = []

        for job in filtered_candidates:
            s_rerank = float(job.get("rerank_score", 0.0))
            s_sem = float(job.get("vector_score", 0.0))
            s_skill = float(job.get("skill_score", 0.0))

            req_exp = float(
                job.get("required_years", job.get("min_experience_years", 0.0))
            )
            s_exp = compute_experience_score(preferences.years_of_experience, req_exp)
            s_role = compute_role_score(
                preferences.target_role, str(job.get("title", ""))
            )
            s_loc = compute_location_score(
                str(job.get("location", "")), preferences.preferred_locations
            )
            s_mode = compute_work_mode_score(
                str(job.get("work_mode", "")), preferences.preferred_work_modes
            )

            # Convex linear combination
            final = (
                self.norm_weights.get("s_rerank", 0.0) * s_rerank
                + self.norm_weights.get("s_sem", 0.0) * s_sem
                + self.norm_weights.get("s_skill", 0.0) * s_skill
                + self.norm_weights.get("s_exp", 0.0) * s_exp
                + self.norm_weights.get("s_role", 0.0) * s_role
                + self.norm_weights.get("s_loc", 0.0) * s_loc
                + self.norm_weights.get("s_mode", 0.0) * s_mode
            )

            components = {
                "s_rerank": s_rerank,
                "s_sem": s_sem,
                "s_skill": s_skill,
                "s_exp": s_exp,
                "s_role": s_role,
                "s_loc": s_loc,
                "s_mode": s_mode,
            }
            scored_items.append((job, final, components))

        # Step 3: Sort descending and truncate to top_k
        scored_items.sort(key=lambda x: x[1], reverse=True)

        results: list[PersonalizedJobScore] = []
        for rank_idx, (job, final_sc, comp) in enumerate(scored_items[:top_k], start=1):
            results.append(
                PersonalizedJobScore(
                    job_id=str(job.get("job_id", job.get("id", ""))),
                    final_score=final_sc,
                    rank=rank_idx,
                    s_rerank=comp["s_rerank"],
                    s_sem=comp["s_sem"],
                    s_skill=comp["s_skill"],
                    s_exp=comp["s_exp"],
                    s_role=comp["s_role"],
                    s_loc=comp["s_loc"],
                    s_mode=comp["s_mode"],
                )
            )

        return results
