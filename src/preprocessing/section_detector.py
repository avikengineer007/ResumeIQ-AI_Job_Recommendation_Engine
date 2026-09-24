"""Section detection module for resumes.

Detects standard sections (Skills, Experience, Education, Projects, Certifications)
and tracks character offsets for all section boundaries.
"""

import re
from dataclasses import dataclass
from enum import StrEnum


class SectionType(StrEnum):
    HEADER = "header"
    SUMMARY = "summary"
    SKILLS = "skills"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    OTHER = "other"


@dataclass
class ResumeSection:
    section_type: SectionType
    raw_header: str
    text: str
    start_char: int
    end_char: int


# Section header regex patterns
SECTION_PATTERNS: dict[SectionType, list[str]] = {
    SectionType.SUMMARY: [
        r"summary",
        r"professional summary",
        r"career objective",
        r"objective",
        r"about me",
        r"profile",
    ],
    SectionType.SKILLS: [
        r"skills",
        r"technical skills",
        r"core competencies",
        r"technologies",
        r"skills\s*&\s*abilities",
        r"expertise",
        r"key skills",
        r"tools\s*&\s*technologies",
    ],
    SectionType.EXPERIENCE: [
        r"experience",
        r"work experience",
        r"professional experience",
        r"employment history",
        r"work history",
        r"career history",
        r"internships?",
    ],
    SectionType.EDUCATION: [
        r"education",
        r"academic background",
        r"academic qualifications",
        r"qualifications",
        r"educational background",
    ],
    SectionType.PROJECTS: [
        r"projects",
        r"key projects",
        r"academic projects",
        r"personal projects",
        r"selected projects",
        r"technical projects",
    ],
    SectionType.CERTIFICATIONS: [
        r"certifications?",
        r"licenses?\s*(&|and)?\s*certifications?",
        r"courses?\s*(&|and)?\s*certifications?",
        r"professional certifications?",
        r"credentials",
    ],
}


class SectionDetector:
    """Detects sections in plain resume text using pattern matching."""

    def __init__(self) -> None:
        self.compiled_patterns: list[tuple[SectionType, re.Pattern[str]]] = []
        for sec_type, patterns in SECTION_PATTERNS.items():
            pattern_str = (
                r"^(?:#+\s*)?(?:[-*]\s*)?(?:" + "|".join(patterns) + r")\s*:?$"
            )
            compiled = re.compile(pattern_str, re.IGNORECASE)
            self.compiled_patterns.append((sec_type, compiled))

    def detect_sections(self, text: str) -> list[ResumeSection]:
        """Split resume text into typed sections with start and end character offsets."""
        if not text.strip():
            return []

        lines = text.splitlines(keepends=True)
        header_indices: list[tuple[int, SectionType, str, int]] = []
        current_offset = 0

        # Pass 1: Identify all line indices and offsets that act as section headers
        for line in lines:
            stripped = line.strip()
            # Headers are typically short lines (< 50 chars)
            if stripped and len(stripped) < 50:
                # False positive guards: do not treat bullets, sentences with periods, or descriptive phrases as headers
                if (
                    stripped.endswith((".", ","))
                    or any(
                        w in stripped.lower()
                        for w in [
                            "used",
                            "including",
                            "such as",
                            "gained",
                            "proficient in",
                            "experience with",
                        ]
                    )
                    or stripped.startswith(("•", "* ", "- "))
                    or line.startswith(("   ", "\t"))
                ):
                    current_offset += len(line)
                    continue

                # Remove markdown formatting or underlines
                clean_line = re.sub(r"^#+\s*", "", stripped).rstrip(":")
                for sec_type, regex in self.compiled_patterns:
                    if regex.match(clean_line) or regex.match(stripped):
                        header_indices.append(
                            (current_offset, sec_type, stripped, len(line))
                        )
                        break
            current_offset += len(line)

        # If no explicit headers were identified, return entire document as OTHER
        if not header_indices:
            return [
                ResumeSection(
                    section_type=SectionType.OTHER,
                    raw_header="",
                    text=text,
                    start_char=0,
                    end_char=len(text),
                )
            ]

        sections: list[ResumeSection] = []

        # Header section before first detected section
        first_header_start = header_indices[0][0]
        if first_header_start > 0:
            pre_text = text[:first_header_start].strip()
            if pre_text:
                sections.append(
                    ResumeSection(
                        section_type=SectionType.HEADER,
                        raw_header="Header",
                        text=pre_text,
                        start_char=0,
                        end_char=first_header_start,
                    )
                )

        # Slice between consecutive section headers
        for i, (start_char, sec_type, raw_hdr, hdr_len) in enumerate(header_indices):
            body_start = start_char + hdr_len
            if i + 1 < len(header_indices):
                body_end = header_indices[i + 1][0]
            else:
                body_end = len(text)

            body_raw = text[body_start:body_end]
            leading_ws = len(body_raw) - len(body_raw.lstrip())
            trailing_ws = len(body_raw) - len(body_raw.rstrip())

            actual_body_start = body_start + leading_ws
            actual_body_end = max(actual_body_start, body_end - trailing_ws)
            body_text = text[actual_body_start:actual_body_end]

            sections.append(
                ResumeSection(
                    section_type=sec_type,
                    raw_header=raw_hdr,
                    text=body_text,
                    start_char=actual_body_start,
                    end_char=actual_body_end,
                )
            )

        return sections
