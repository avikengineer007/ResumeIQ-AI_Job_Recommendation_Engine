"""Faithfulness and grounding verifier for generated explanations.

Prevents ungrounded AI hallucinations and ensures zero-gap alignment between
the factual ExplanationEvidence and user-facing explanation statements.
"""

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from src.explainability.evidence import ExplanationEvidence

if TYPE_CHECKING:
    from src.explainability.templates import GeneratedExplanation


class UnfaithfulExplanationError(ValueError):
    """Raised when an explanation violates grounding evidence or introduces hallucinations."""

    pass


@dataclass
class VerificationReport:
    """Detailed audit report testing explanation faithfulness against ground truth evidence."""

    is_faithful: bool
    violations: list[str] = field(default_factory=list)
    verified_skills: list[str] = field(default_factory=list)
    unverified_claims: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_faithful": self.is_faithful,
            "violations": self.violations,
            "verified_skills": self.verified_skills,
            "unverified_claims": self.unverified_claims,
        }


class ExplanationVerifier:
    """Verifies that an explanation does not introduce hallucinations or contradict evidence."""

    def verify(
        self,
        explanation: "GeneratedExplanation",
        evidence: ExplanationEvidence,
    ) -> VerificationReport:
        """Run comprehensive faithfulness checks across explanation fields."""
        violations: list[str] = []
        verified_skills: list[str] = []
        unverified_claims: list[str] = []

        all_text = " ".join(
            [
                explanation.headline,
                explanation.summary,
                " ".join(explanation.skill_bullets),
                explanation.experience_statement,
                explanation.role_statement,
                explanation.logistics_statement,
                explanation.missing_skills_bullet,
                explanation.transparency_statement,
            ]
        )

        # 1. Skill Grounding & Hallucination Check
        known_skill_names = {
            s.skill_name.lower(): s.skill_name for s in evidence.matched_skills
        }
        known_skill_names.update(
            {s.skill_name.lower(): s.skill_name for s in evidence.missing_skills}
        )

        for s_lower, s_orig in known_skill_names.items():
            pattern = rf"\b{re.escape(s_lower)}\b"
            if re.search(pattern, all_text.lower()):
                verified_skills.append(s_orig)

        for bullet in explanation.skill_bullets:
            if ":" in bullet:
                _, items_str = bullet.split(":", 1)
                for item in re.split(r"[,;]", items_str):
                    clean_item = re.sub(r"\(.*?\)", "", item).strip()
                    clean_item = re.sub(r"\band\b.*", "", clean_item).strip()
                    if (
                        clean_item
                        and len(clean_item) > 1
                        and not clean_item.startswith("and ")
                    ):
                        if (
                            clean_item.lower() not in known_skill_names
                            and "more" not in clean_item.lower()
                            and "overlap" not in clean_item.lower()
                            and "identified" not in clean_item.lower()
                        ):
                            violations.append(
                                f"Explanation bullet cites skill '{clean_item}' which is absent from evidence."
                            )

        # 2. Honest Skill Gap Reporting Check
        has_missing_skills = len(evidence.missing_skills) > 0
        if has_missing_skills:
            if (
                "full skill coverage" in all_text.lower()
                or "100% skill overlap" in all_text.lower()
            ):
                violations.append(
                    f"Explanation claims full skill coverage, but evidence has "
                    f"{len(evidence.missing_skills)} missing skills."
                )

        # 3. Numeric Experience Fidelity Check
        exp_matches = re.findall(
            r"(\d+(?:\.\d+)?)\s*(?:years|year)",
            explanation.experience_statement.lower(),
        )
        if exp_matches:
            found_nums = {float(m) for m in exp_matches}
            expected_nums = {
                evidence.experience.candidate_years,
                evidence.experience.required_years,
            }
            if evidence.experience.gap_years > 0:
                expected_nums.add(evidence.experience.gap_years)

            for num in found_nums:
                if not any(abs(num - exp_n) < 0.1 for exp_n in expected_nums):
                    violations.append(
                        f"Experience statement mentions {num} years, which does not match candidate "
                        f"({evidence.experience.candidate_years}y), required ({evidence.experience.required_years}y), "
                        f"or gap ({evidence.experience.gap_years}y)."
                    )

        # 4. Work Arrangement Fidelity Check
        if (
            "remote" in explanation.logistics_statement.lower()
            and "fully remote" in explanation.logistics_statement.lower()
        ):
            if evidence.location.job_work_mode not in ["remote", "hybrid"]:
                violations.append(
                    f"Logistics statement claims remote position, but job posting specifies "
                    f"'{evidence.location.job_work_mode}'."
                )

        # 5. Identifier and Rank Fidelity Check
        if explanation.job_id != evidence.job_id:
            violations.append(
                f"Explanation job_id '{explanation.job_id}' does not match evidence job_id '{evidence.job_id}'."
            )
        if explanation.rank != evidence.scores.rank:
            violations.append(
                f"Explanation rank '{explanation.rank}' does not match evidence rank '{evidence.scores.rank}'."
            )

        # 6. Percentage and Calibrated Probability Fidelity Check
        pct_matches = re.findall(r"(?:~|\b)(\d+)%", all_text)
        if pct_matches:
            found_pcts = [int(p) for p in pct_matches]
            n_matched = len(evidence.matched_skills)
            n_missing = len(evidence.missing_skills)
            valid_pcts = {int(round((n_matched / max(1, n_matched + n_missing)) * 100))}
            if evidence.scores.calibrated_probability is not None:
                valid_pcts.add(int(round(evidence.scores.calibrated_probability * 100)))

            for pct in found_pcts:
                if not any(abs(pct - vp) <= 3 for vp in valid_pcts):
                    violations.append(
                        f"Explanation contains ungrounded percentage {pct}%, which differs from "
                        f"evidence-derived overlap or calibrated probability ({valid_pcts})."
                    )

        is_faithful = len(violations) == 0
        return VerificationReport(
            is_faithful=is_faithful,
            violations=violations,
            verified_skills=verified_skills,
            unverified_claims=unverified_claims,
        )
