"""Resume parsing module.

Extracts structured work experience, tenure duration, degrees, fields of study,
projects, and certifications, retaining exact character offsets (source spans)
for every extracted item.
"""

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.preprocessing.section_detector import (
    ResumeSection,
    SectionDetector,
    SectionType,
)

# Degree patterns
DEGREE_PATTERNS = [
    r"\b(?:Ph\.?D\.?|Doctor of Philosophy)\b",
    r"\b(?:M\.?Tech\.?|M\.?S\.?|M\.?Sc\.?|Master of (?:Science|Technology|Engineering|Business Administration|Arts))\b",
    r"\b(?:B\.?Tech\.?|B\.?S\.?|B\.?Sc\.?|B\.?E\.?|Bachelor of (?:Science|Technology|Engineering|Arts|Business Administration))\b",
    r"\b(?:MBA|MCA|BCA)\b",
    r"\b(?:Associate(?:'s)? Degree)\b",
    r"\b(?:Diploma)\b",
]
_COMPILED_DEGREES = [re.compile(p, re.IGNORECASE) for p in DEGREE_PATTERNS]

# Field of study patterns
FIELD_PATTERNS = [
    r"\b(?:Computer Science(?: and Engineering)?|Information Technology|Software Engineering)\b",
    r"\b(?:Artificial Intelligence(?: and Machine Learning)?|Data Science)\b",
    r"\b(?:Electrical(?: and Electronics)? Engineering|Mechanical Engineering|Civil Engineering)\b",
    r"\b(?:Mathematics|Statistics|Physics|Economics|Finance|Business Analytics)\b",
]
_COMPILED_FIELDS = [re.compile(p, re.IGNORECASE) for p in FIELD_PATTERNS]

# Date range extraction patterns supporting international formats (dots, slashes, month names)
DATE_RANGE_REGEX = re.compile(
    r"\b((?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|"
    r"\d{1,2}[/.-]\d{4}|\d{4}[/.-]\d{1,2}|\d{4}))"
    r"(?:\s*(?:-|–|—|to)\s*)"
    r"((?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
    r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|"
    r"\d{1,2}[/.-]\d{4}|\d{4}[/.-]\d{1,2}|\d{4}|Present|Current))\b",
    re.IGNORECASE,
)

YEAR_REGEX = re.compile(r"\b(19\d{2}|20\d{2})\b")
MONTH_NAME_MAP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


ROLE_TITLE_REGEX = re.compile(
    r"\b(?:engineer|developer|intern|manager|lead|analyst|scientist|consultant|architect|designer|lecturer|specialist|administrator|fellow|researcher|associate|director|advisor|instructor|professor|head)\b",
    re.IGNORECASE,
)


@dataclass
class SourceSpan:
    section: str
    start_char: int
    end_char: int

    def __str__(self) -> str:
        return f"{self.section}:{self.start_char}-{self.end_char}"


@dataclass
class ParsedExperience:
    title: str
    org: str | None
    date_range: str | None
    start_year: int | None
    end_year: int | None
    months: int
    description: str
    source_span: SourceSpan


@dataclass
class ParsedEducation:
    degree: str
    field: str | None
    year: int | None
    source_span: SourceSpan


@dataclass
class ParsedProject:
    name: str
    description: str
    source_span: SourceSpan


@dataclass
class ParsedCertification:
    name: str
    source_span: SourceSpan


@dataclass
class ParsedResume:
    sections: dict[SectionType, ResumeSection] = field(default_factory=dict)
    experience: list[ParsedExperience] = field(default_factory=list)
    total_years: float = 0.0
    education: list[ParsedEducation] = field(default_factory=list)
    projects: list[ParsedProject] = field(default_factory=list)
    certifications: list[ParsedCertification] = field(default_factory=list)
    raw_text: str = ""


class ResumeParser:
    """Parses plain text resume into structured components."""

    def __init__(self, section_detector: SectionDetector | None = None) -> None:
        self.detector = section_detector or SectionDetector()

    def parse(self, text: str) -> ParsedResume:
        """Parse raw resume text into sections, experience, education, projects, and certifications."""
        sections_list = self.detector.detect_sections(text)
        sections_map = {sec.section_type: sec for sec in sections_list}

        parsed = ParsedResume(
            sections=sections_map,
            raw_text=text,
        )

        # 1. Parse Experience
        if SectionType.EXPERIENCE in sections_map:
            sec = sections_map[SectionType.EXPERIENCE]
            parsed.experience = self._parse_experience(sec)
            parsed.total_years = self._calculate_total_years(parsed.experience)

        # 2. Parse Education
        if SectionType.EDUCATION in sections_map:
            sec = sections_map[SectionType.EDUCATION]
            parsed.education = self._parse_education(sec)

        # 3. Parse Projects
        if SectionType.PROJECTS in sections_map:
            sec = sections_map[SectionType.PROJECTS]
            parsed.projects = self._parse_projects(sec)

        # 4. Parse Certifications
        if SectionType.CERTIFICATIONS in sections_map:
            sec = sections_map[SectionType.CERTIFICATIONS]
            parsed.certifications = self._parse_certifications(sec)

        return parsed

    def _parse_experience(self, section: ResumeSection) -> list[ParsedExperience]:
        """Extract individual roles, organizations, and tenure from the experience section."""
        items: list[ParsedExperience] = []
        lines = [line.strip() for line in section.text.splitlines() if line.strip()]

        current_title: str | None = None
        current_org: str | None = None
        current_date_str: str | None = None
        current_start_year: int | None = None
        current_end_year: int | None = None
        current_desc_lines: list[str] = []
        item_start_char = section.start_char

        def flush_current(end_char: int) -> None:
            nonlocal current_title, current_org, current_date_str, current_start_year, current_end_year
            nonlocal current_desc_lines, item_start_char
            if current_title:
                # Calculate months
                months = 0
                if current_start_year and current_end_year:
                    months = max(1, (current_end_year - current_start_year) * 12)
                elif current_start_year:
                    curr_year = datetime.now(UTC).year
                    months = max(1, (curr_year - current_start_year) * 12)

                items.append(
                    ParsedExperience(
                        title=current_title,
                        org=current_org,
                        date_range=current_date_str,
                        start_year=current_start_year,
                        end_year=current_end_year,
                        months=months,
                        description=" ".join(current_desc_lines),
                        source_span=SourceSpan(
                            section="Experience",
                            start_char=item_start_char,
                            end_char=end_char,
                        ),
                    )
                )
            current_title = None
            current_org = None
            current_date_str = None
            current_start_year = None
            current_end_year = None
            current_desc_lines = []

        curr_offset = section.start_char
        for line in lines:
            line_pos = section.text.find(line, curr_offset - section.start_char)
            abs_start = section.start_char + line_pos if line_pos != -1 else curr_offset

            date_match = DATE_RANGE_REGEX.search(line)
            is_bullet = line.startswith(("•", "* ", "- ", "– "))
            is_desc_phrase = any(
                w in line.lower()
                for w in [
                    "worked",
                    "built",
                    "developed",
                    "designed",
                    "shipped",
                    "responsible",
                    "managed",
                    "promotion",
                    "contributed",
                    "improved",
                ]
            )

            is_title_candidate = (
                not is_bullet
                and not is_desc_phrase
                and not line.endswith(".")
                and bool(ROLE_TITLE_REGEX.search(line))
                and len(line) < 80
            )

            # Case 1: Active title exists and this line provides its date range (and is not a description sentence)
            if (
                date_match
                and current_title
                and not current_date_str
                and not is_title_candidate
                and not is_desc_phrase
                and len(line) < 50
            ):
                current_date_str = date_match.group(0)
                start_str, end_str = date_match.group(1), date_match.group(2)
                current_start_year = self._extract_year(start_str)
                if "present" in end_str.lower() or "current" in end_str.lower():
                    current_end_year = datetime.now(UTC).year
                else:
                    current_end_year = self._extract_year(end_str)

                rem = line[: date_match.start()].strip(" |-–—,")
                if rem and not current_org:
                    current_org = rem

            # Case 2: New role boundary detected
            elif is_title_candidate or (
                date_match
                and not current_title
                and not is_bullet
                and not is_desc_phrase
                and len(line) < 50
            ):
                flush_current(abs_start)
                item_start_char = abs_start

                if date_match:
                    current_date_str = date_match.group(0)
                    start_str, end_str = date_match.group(1), date_match.group(2)
                    current_start_year = self._extract_year(start_str)
                    if "present" in end_str.lower() or "current" in end_str.lower():
                        current_end_year = datetime.now(UTC).year
                    else:
                        current_end_year = self._extract_year(end_str)

                    title_part = line[: date_match.start()].strip(" |-–—,")
                    if title_part:
                        current_title, current_org = self._split_title_org(title_part)
                    else:
                        current_title = "Experience"
                else:
                    # Check for single-year mention in title line like "Research Fellow at Oxford (2021)"
                    single_year = self._extract_year(line)
                    if single_year:
                        current_start_year = single_year
                        current_end_year = single_year
                        current_date_str = str(single_year)
                    current_title, current_org = self._split_title_org(line)
            else:
                current_desc_lines.append(line)

            curr_offset = abs_start + len(line)

        flush_current(section.end_char)
        return items

    def _split_title_org(self, line: str) -> tuple[str, str | None]:
        """Split a header line like 'Senior ML Engineer at Acme Corp' or 'Acme Corp - ML Engineer'."""
        delims = [" at ", " @ ", " - ", " | "]
        for d in delims:
            if d in line:
                parts = line.split(d, 1)
                return parts[0].strip(), parts[1].strip()
        return line.strip(), None

    def _extract_year(self, text: str) -> int | None:
        """Find a 4-digit year in string."""
        m = YEAR_REGEX.search(text)
        return int(m.group(1)) if m else None

    def _calculate_total_years(self, experiences: list[ParsedExperience]) -> float:
        """Calculate total non-overlapping years across all experience items."""
        intervals: list[tuple[int, int]] = []
        for exp in experiences:
            if exp.start_year and exp.end_year:
                s_y = min(exp.start_year, exp.end_year)
                e_y = max(exp.start_year, exp.end_year)
                intervals.append((s_y, max(s_y + 1, e_y)))
            elif exp.months > 0:
                now_y = datetime.now(UTC).year
                years_span = max(1, round(exp.months / 12))
                intervals.append((now_y - years_span, now_y))

        if not intervals:
            total_months = sum(e.months for e in experiences)
            return round(total_months / 12.0, 1)

        # Merge overlapping intervals
        intervals.sort(key=lambda x: x[0])
        merged: list[tuple[int, int]] = []
        for start, end in intervals:
            if not merged or merged[-1][1] < start:
                merged.append((start, end))
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))

        total_years = sum(end - start for start, end in merged)
        return float(max(0.0, total_years))

    def _parse_education(self, section: ResumeSection) -> list[ParsedEducation]:
        """Extract degrees, fields of study, and years from the education section."""
        items: list[ParsedEducation] = []
        lines = [line.strip() for line in section.text.splitlines() if line.strip()]

        for line in lines:
            degree_found: str | None = None
            for p in _COMPILED_DEGREES:
                m = p.search(line)
                if m:
                    degree_found = m.group(0)
                    break

            if degree_found:
                field_found: str | None = None
                for fp in _COMPILED_FIELDS:
                    fm = fp.search(line)
                    if fm:
                        field_found = fm.group(0)
                        break

                year_found = self._extract_year(line)
                line_offset = section.text.find(line)
                abs_start = section.start_char + (
                    line_offset if line_offset != -1 else 0
                )

                items.append(
                    ParsedEducation(
                        degree=degree_found,
                        field=field_found,
                        year=year_found,
                        source_span=SourceSpan(
                            section="Education",
                            start_char=abs_start,
                            end_char=abs_start + len(line),
                        ),
                    )
                )

        return items

    def _parse_projects(self, section: ResumeSection) -> list[ParsedProject]:
        """Extract project items from projects section."""
        items: list[ParsedProject] = []
        lines = [line.strip() for line in section.text.splitlines() if line.strip()]

        for line in lines:
            if len(line) < 10:
                continue
            line_offset = section.text.find(line)
            abs_start = section.start_char + (line_offset if line_offset != -1 else 0)

            # Split title and description if separated by colon or dash
            if ":" in line:
                name, desc = line.split(":", 1)
            elif " - " in line:
                name, desc = line.split(" - ", 1)
            else:
                name = line[:40].strip()
                desc = line

            items.append(
                ParsedProject(
                    name=name.strip(),
                    description=desc.strip(),
                    source_span=SourceSpan(
                        section="Projects",
                        start_char=abs_start,
                        end_char=abs_start + len(line),
                    ),
                )
            )

        return items

    def _parse_certifications(
        self, section: ResumeSection
    ) -> list[ParsedCertification]:
        """Extract certification names from certifications section."""
        items: list[ParsedCertification] = []
        lines = [line.strip() for line in section.text.splitlines() if line.strip()]

        for line in lines:
            line_offset = section.text.find(line)
            abs_start = section.start_char + (line_offset if line_offset != -1 else 0)
            items.append(
                ParsedCertification(
                    name=line.lstrip("•-* ").strip(),
                    source_span=SourceSpan(
                        section="Certifications",
                        start_char=abs_start,
                        end_char=abs_start + len(line),
                    ),
                )
            )

        return items
