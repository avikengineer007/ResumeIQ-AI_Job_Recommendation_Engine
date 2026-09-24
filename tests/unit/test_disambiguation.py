"""Comprehensive unit tests for context-aware ambiguous token disambiguation.

Validates disambiguation logic across challenging adversarial cases:
- 'Go' (language) vs 'go' (verb, go-to-market, go live)
- 'Spring' (Java framework) vs 'spring' (season, semester, internship)
- 'Swift' (Apple language) vs 'swift' (adjective: swift action/response)
- 'Rust' (language) vs 'rust' (corrosion, mechanical)
- 'R' (language) vs 'R' (letter, section R)
- 'C' (language) vs 'C' (grade, vitamin C, section C)
"""

from pathlib import Path

import pytest

from src.skill_extraction.dictionary_matcher import DictionaryMatcher
from src.skill_normalization.taxonomy import SkillTaxonomy


@pytest.fixture
def matcher(project_root: Path) -> DictionaryMatcher:
    taxonomy = SkillTaxonomy.load_from_dir(project_root / "data" / "processed")
    return DictionaryMatcher(taxonomy)


@pytest.mark.parametrize(
    "text,expected_skill_id",
    [
        # Go language with technical context
        ("Built distributed Go microservices with Docker and Kubernetes.", "sk_golang"),
        ("Senior backend engineer specializing in Go and concurrency.", "sk_golang"),
        # Spring framework with technical context
        ("Designed enterprise APIs using Spring Boot and Hibernate.", "sk_spring"),
        ("Backend Java developer with deep Spring framework expertise.", "sk_spring"),
        # Swift iOS language
        ("Developed iOS mobile applications in Swift and SwiftUI.", "sk_swift"),
        ("Apple platform developer proficient in Swift and Xcode.", "sk_swift"),
        # Rust systems language
        ("Engineered low-latency systems in Rust with memory safety.", "sk_rust"),
        ("Backend systems programmer writing Rust and C++.", "sk_rust"),
        # R statistical language
        (
            "Conducted statistical modeling and data analysis using R and Python.",
            "sk_r_lang",
        ),
        ("Applied biostatistics and data analysis in R language.", "sk_r_lang"),
        # C language
        ("Developed embedded Linux firmware in C and assembly.", "sk_c_lang"),
        ("Kernel development and systems programming in C language.", "sk_c_lang"),
    ],
)
def test_disambiguation_positive_cases(
    matcher: DictionaryMatcher, text: str, expected_skill_id: str
) -> None:
    mentions = matcher.extract_skills(text)
    matched_ids = {m.canonical_skill_id for m in mentions}
    assert (
        expected_skill_id in matched_ids
    ), f"Expected {expected_skill_id} in {matched_ids} for: {text}"


@pytest.mark.parametrize(
    "text,rejected_skill_id",
    [
        # Go as common English verb / business phrases
        ("Led the product go-to-market strategy across 10 regions.", "sk_golang"),
        ("Prepared the production deployment to go live on Friday.", "sk_golang"),
        ("Must go through extensive compliance reviews before release.", "sk_golang"),
        ("Always on the go managing multiple cross-functional teams.", "sk_golang"),
        # Spring as season / academic calendar
        (
            "Completed a software engineering spring internship in New York.",
            "sk_spring",
        ),
        ("Maintained Dean's Honor List during Spring 2022 and Fall 2023.", "sk_spring"),
        ("Conducted campus recruitment during the spring semester.", "sk_spring"),
        # Swift as adjective
        (
            "Took swift action to mitigate DDoS vulnerability and restore uptime.",
            "sk_swift",
        ),
        (
            "Received client commendation for swift response to critical outage.",
            "sk_swift",
        ),
        # Rust as physical corrosion
        (
            "Inspected physical machinery for rust prevention and structural wear.",
            "sk_rust",
        ),
        # Non-programming R and C
        ("Referred to Section R of the compliance manual.", "sk_r_lang"),
        ("Maintained a Grade C average in non-technical electives.", "sk_c_lang"),
    ],
)
def test_disambiguation_adversarial_negative_cases(
    matcher: DictionaryMatcher, text: str, rejected_skill_id: str
) -> None:
    mentions = matcher.extract_skills(text)
    matched_ids = {m.canonical_skill_id for m in mentions}
    assert (
        rejected_skill_id not in matched_ids
    ), f"Expected {rejected_skill_id} NOT in {matched_ids} for: {text}"
