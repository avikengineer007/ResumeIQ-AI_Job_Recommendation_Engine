"""Skill matcher module comparing candidate skill profile against job posting requirements."""

from dataclasses import dataclass, field
from typing import Any

from src.skill_normalization.taxonomy import SkillTaxonomy


@dataclass
class MatchedSkillDetail:
    job_skill_id: str
    job_skill_name: str
    candidate_skill_id: str
    candidate_skill_name: str
    match_type: str  # exact, parent_hierarchy, related
    score: float
    importance: str  # required or preferred


@dataclass
class MissingSkillDetail:
    skill_id: str
    name: str
    importance: str  # required or preferred


@dataclass
class SkillMatchResult:
    matched_skills: list[MatchedSkillDetail] = field(default_factory=list)
    related_skills: list[MatchedSkillDetail] = field(default_factory=list)
    missing_skills: list[MissingSkillDetail] = field(default_factory=list)
    skill_score: float = 0.0
    matched_count: int = 0
    total_required: int = 0
    total_preferred: int = 0


class SkillMatcher:
    """Computes exact, hierarchical parent, and related skill matches with calibrated discounting."""

    def __init__(
        self,
        taxonomy: SkillTaxonomy,
        # TODO(Phase 10): tune parent credit discount on validation split rather than keeping heuristic default
        parent_discount: float = 0.60,
        # TODO(Phase 10): tune related credit discount on validation split rather than keeping heuristic default
        related_discount: float = 0.40,
        # TODO(Phase 10): tune required skill weight on validation split
        required_weight: float = 1.0,
        # TODO(Phase 10): tune preferred skill weight on validation split
        preferred_weight: float = 0.5,
    ) -> None:
        self.taxonomy = taxonomy
        self.parent_discount = parent_discount
        self.related_discount = related_discount
        self.required_weight = required_weight
        self.preferred_weight = preferred_weight

    def match(
        self,
        candidate_skill_ids: list[str],
        job_skills: list[dict[str, Any]],
    ) -> SkillMatchResult:
        """Compare candidate skills against job skills.

        Args:
            candidate_skill_ids: List of canonical skill IDs from candidate resume.
            job_skills: List of dicts with keys {"skill_id", "name", "importance"} (or JobSkillItem).

        Returns:
            Structured SkillMatchResult with matched, related, missing items and overall score.
        """
        cand_set = set(candidate_skill_ids)
        result = SkillMatchResult()

        total_possible_score = 0.0
        earned_score = 0.0

        for item in job_skills:
            jsid = item.get("skill_id") if isinstance(item, dict) else item.skill_id
            jname = item.get("name") if isinstance(item, dict) else item.name
            importance = (
                item.get("importance") if isinstance(item, dict) else item.importance
            ) or "required"
            weight = (
                self.required_weight
                if importance == "required"
                else self.preferred_weight
            )

            if importance == "required":
                result.total_required += 1
            else:
                result.total_preferred += 1

            total_possible_score += weight

            # 1. Exact match
            if jsid in cand_set:
                detail = MatchedSkillDetail(
                    job_skill_id=jsid,
                    job_skill_name=jname,
                    candidate_skill_id=jsid,
                    candidate_skill_name=jname,
                    match_type="exact",
                    score=1.0,
                    importance=importance,
                )
                result.matched_skills.append(detail)
                result.matched_count += 1
                earned_score += 1.0 * weight
                continue

            # 2. Hierarchical match: does candidate possess a child skill that satisfies a parent job skill?
            # Example: Job asks for 'Machine Learning' and candidate has 'PyTorch' or 'Deep Learning'
            matched_child = False
            for csid in cand_set:
                parents = self.taxonomy.get_all_parents(csid)
                if jsid in parents:
                    c_skill = self.taxonomy.get_skill(csid)
                    detail = MatchedSkillDetail(
                        job_skill_id=jsid,
                        job_skill_name=jname,
                        candidate_skill_id=csid,
                        candidate_skill_name=(
                            c_skill.canonical_name if c_skill else csid
                        ),
                        match_type="parent_hierarchy",
                        score=self.parent_discount,
                        importance=importance,
                    )
                    result.related_skills.append(detail)
                    earned_score += self.parent_discount * weight
                    matched_child = True
                    break

            if matched_child:
                continue

            # 3. Direct related skill match
            # Example: Job asks for 'MySQL' and candidate has 'PostgreSQL'
            matched_related = False
            for csid in cand_set:
                related = self.taxonomy.get_related_skills(csid)
                for rel_id, rel_weight in related:
                    if rel_id == jsid:
                        c_skill = self.taxonomy.get_skill(csid)
                        discount = min(self.related_discount, rel_weight)
                        detail = MatchedSkillDetail(
                            job_skill_id=jsid,
                            job_skill_name=jname,
                            candidate_skill_id=csid,
                            candidate_skill_name=(
                                c_skill.canonical_name if c_skill else csid
                            ),
                            match_type="related",
                            score=discount,
                            importance=importance,
                        )
                        result.related_skills.append(detail)
                        earned_score += discount * weight
                        matched_related = True
                        break
                if matched_related:
                    break

            if matched_related:
                continue

            # 4. If neither exact nor related, mark as missing
            result.missing_skills.append(
                MissingSkillDetail(
                    skill_id=jsid,
                    name=jname,
                    importance=importance,
                )
            )

        if total_possible_score > 0:
            result.skill_score = round(earned_score / total_possible_score, 4)
        else:
            result.skill_score = 0.0

        return result
