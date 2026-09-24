"""Template-based explanation engine for faithful, evidence-grounded recommendations.

Architecture Rules:
1. Zero Hallucination: Explanations are strictly generated from verified ExplanationEvidence.
2. Honest Skill Gap Reporting: Missing required and preferred skills are clearly itemized.
3. Multi-Aspect Transparency: Covers skills, experience, role match, logistics, and scoring drivers.
4. Active Verification: Automatically runs ExplanationVerifier to audit every output before return.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from src.explainability.evidence import ExplanationEvidence
from src.explainability.verifier import (
    ExplanationVerifier,
    UnfaithfulExplanationError,
    VerificationReport,
)


@dataclass
class GeneratedExplanation:
    """Structured, multi-aspect explanation object for a recommendation."""

    job_id: str
    job_title: str
    company: str
    rank: int
    headline: str
    summary: str
    skill_bullets: list[str] = field(default_factory=list)
    experience_statement: str = ""
    role_statement: str = ""
    logistics_statement: str = ""
    missing_skills_bullet: str = ""
    transparency_statement: str = ""
    is_verified: bool = False
    verification_report: VerificationReport | None = None

    def to_markdown(self) -> str:
        """Render the explanation in polished Markdown format."""
        md = [
            f"### #{self.rank} {self.job_title} at {self.company}",
            f"**{self.headline}**",
            "",
            f"{self.summary}",
            "",
            "#### Skill Alignment & Gap Analysis",
        ]
        for bullet in self.skill_bullets:
            md.append(f"- {bullet}")

        if self.missing_skills_bullet:
            md.append(f"- {self.missing_skills_bullet}")

        md.extend(
            [
                "",
                "#### Qualification & Preference Fit",
                f"- **Experience**: {self.experience_statement}",
                f"- **Role Focus**: {self.role_statement}",
                f"- **Work Arrangement**: {self.logistics_statement}",
                "",
                f"> **System Confidence**: {self.transparency_statement}",
            ]
        )
        return "\n".join(md)

    def to_dict(self) -> dict[str, Any]:
        """Convert explanation to dictionary representation."""
        data = asdict(self)
        if self.verification_report is not None:
            data["verification_report"] = self.verification_report.to_dict()
        return data


class TemplateExplainer:
    """Generates deterministic, faithful explanations from ExplanationEvidence."""

    def __init__(self, verifier: ExplanationVerifier | None = None) -> None:
        self.verifier = verifier or ExplanationVerifier()

    def explain(
        self,
        evidence: ExplanationEvidence,
        auto_verify: bool = True,
        strict: bool = False,
    ) -> GeneratedExplanation:
        """Transform structured evidence into a multi-faceted explanation with active verification."""
        # 1. Headline & Summary
        n_matched = len(evidence.matched_skills)
        n_missing = len(evidence.missing_skills)
        total_skills = n_matched + n_missing
        match_pct = int(round((n_matched / max(1, total_skills)) * 100))

        headline = f"Strong Match ({match_pct}% skill overlap) driven by {evidence.scores.primary_driver}"
        if n_matched == 0:
            headline = f"Potential Match exploring cross-functional transfer for {evidence.job_title}"
        elif n_missing == 0 and total_skills > 0:
            headline = f"Complete Skill Match ({match_pct}%) for {evidence.job_title}"

        # Summary statement
        if evidence.experience.meets_requirement:
            summary = (
                f"Recommended for {evidence.job_title} at {evidence.company} based on matching "
                f"{n_matched} required skill competency areas and meeting the experience threshold."
            )
        else:
            summary = (
                f"Recommended for {evidence.job_title} at {evidence.company} with high skill alignment "
                f"({n_matched} matches), though candidate has {evidence.experience.candidate_years} years vs "
                f"{evidence.experience.required_years} years requested."
            )

        # 2. Skill Bullets
        exact_matches = [
            s.skill_name for s in evidence.matched_skills if s.match_type == "exact"
        ]
        related_matches = [
            f"{s.skill_name} ({s.match_type} background)"
            for s in evidence.matched_skills
            if s.match_type in ["parent", "related", "fuzzy"]
        ]

        skill_bullets: list[str] = []
        if exact_matches:
            skill_bullets.append(
                f"**Direct skill matches**: {', '.join(exact_matches[:6])}"
                + (
                    f" and {len(exact_matches) - 6} more"
                    if len(exact_matches) > 6
                    else ""
                )
            )
        if related_matches:
            skill_bullets.append(
                f"**Related competencies**: {', '.join(related_matches[:4])}"
            )
        if not skill_bullets:
            skill_bullets.append(
                "No direct skill overlap identified; recommended based on semantic profile similarity."
            )

        # Missing skills / gap bullet
        req_missing = [
            s.skill_name for s in evidence.missing_skills if s.importance == "required"
        ]
        pref_missing = [
            s.skill_name for s in evidence.missing_skills if s.importance != "required"
        ]

        if req_missing and pref_missing:
            missing_bullet = (
                f"**Skill gaps to bridge**: Missing required skills ({', '.join(req_missing[:4])}) "
                f"and preferred skills ({', '.join(pref_missing[:3])})"
            )
        elif req_missing:
            missing_bullet = f"**Skill gaps to bridge**: Missing required skills: {', '.join(req_missing[:5])}"
        elif pref_missing:
            missing_bullet = f"**Optional growth areas**: Missing preferred skills: {', '.join(pref_missing[:5])}"
        else:
            missing_bullet = "**Skill gaps**: None identified — full skill coverage."

        # 3. Experience Statement
        exp = evidence.experience
        if exp.required_years == 0.0:
            exp_stmt = f"No minimum experience required; candidate offers {exp.candidate_years} years."
        elif exp.seniority_alignment == "overqualified":
            exp_stmt = (
                f"Candidate possesses {exp.candidate_years} years of experience, exceeding the "
                f"required {exp.required_years} years (strong senior profile)."
            )
        elif exp.meets_requirement:
            exp_stmt = (
                f"Candidate meets requirement with {exp.candidate_years} years of experience "
                f"(requires {exp.required_years} years)."
            )
        else:
            exp_stmt = (
                f"Candidate has {exp.candidate_years} years of experience, reflecting a "
                f"{exp.gap_years}-year gap against the requested {exp.required_years} years."
            )

        # 4. Role Statement
        role = evidence.role
        if role.matched_keywords:
            role_stmt = (
                f"Target role aligns with title '{role.job_title}' sharing key focus areas: "
                f"{', '.join(role.matched_keywords)}."
            )
        elif role.candidate_role:
            role_stmt = f"Target role '{role.candidate_role}' has cross-functional relevance to '{role.job_title}'."
        else:
            role_stmt = f"Position title is '{role.job_title}'."

        # 5. Logistics Statement
        loc = evidence.location
        logistics_stmt = loc.match_reason

        # 6. Transparency Statement
        scores = evidence.scores
        if scores.calibrated_probability is not None:
            cal_pct = int(round(scores.calibrated_probability * 100))
            prob_str = f"Estimated Match Confidence: ~{cal_pct}% (provisional)"
        else:
            prob_str = f"Personalized Fit Score: {scores.final_score:.2f}"

        transparency_stmt = (
            f"{prob_str} | Rank #{scores.rank} | Key Driver: {scores.primary_driver}."
        )

        explanation = GeneratedExplanation(
            job_id=evidence.job_id,
            job_title=evidence.job_title,
            company=evidence.company,
            rank=scores.rank,
            headline=headline,
            summary=summary,
            skill_bullets=skill_bullets,
            experience_statement=exp_stmt,
            role_statement=role_stmt,
            logistics_statement=logistics_stmt,
            missing_skills_bullet=missing_bullet,
            transparency_statement=transparency_stmt,
        )

        # Active verification
        if auto_verify:
            report = self.verifier.verify(explanation, evidence)
            explanation.is_verified = report.is_faithful
            explanation.verification_report = report

            if strict and not report.is_faithful:
                raise UnfaithfulExplanationError(
                    f"Generated explanation failed strict verification: {report.violations}"
                )

        return explanation
