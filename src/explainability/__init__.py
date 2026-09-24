"""Evidence-grounded explainability layer package.

Provides verifiable, factual explanation generation and hallucination auditing
for job recommendations.
"""

from src.explainability.evidence import (
    EvidenceBuilder,
    ExperienceEvidence,
    ExplanationEvidence,
    LocationEvidence,
    RoleEvidence,
    ScoreEvidence,
    SkillEvidence,
)
from src.explainability.templates import GeneratedExplanation, TemplateExplainer
from src.explainability.verifier import (
    ExplanationVerifier,
    UnfaithfulExplanationError,
    VerificationReport,
)

__all__ = [
    "EvidenceBuilder",
    "SkillEvidence",
    "ExperienceEvidence",
    "RoleEvidence",
    "LocationEvidence",
    "ScoreEvidence",
    "ExplanationEvidence",
    "GeneratedExplanation",
    "TemplateExplainer",
    "ExplanationVerifier",
    "VerificationReport",
    "UnfaithfulExplanationError",
]
