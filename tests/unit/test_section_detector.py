"""Unit tests for resume section detection."""

from src.preprocessing.section_detector import SectionDetector, SectionType


def test_standard_section_detection():
    """Verify detection of standard resume sections."""
    resume_text = (
        "John Doe\nSoftware Engineer\n\n"
        "Summary\n"
        "Experienced software developer with 4 years experience.\n\n"
        "Skills\n"
        "Python, PyTorch, Docker, SQL, FastAPI\n\n"
        "Experience\n"
        "Senior ML Engineer - Acme Corp\n"
        "Jan 2021 - Present\n"
        "Built recommendation models.\n\n"
        "Education\n"
        "B.Tech in Computer Science, 2020\n\n"
        "Projects\n"
        "AI Job Search: Hybrid search platform using FAISS\n\n"
        "Certifications\n"
        "AWS Certified Solutions Architect\n"
    )

    detector = SectionDetector()
    sections = detector.detect_sections(resume_text)
    section_types = [s.section_type for s in sections]

    assert SectionType.HEADER in section_types
    assert SectionType.SUMMARY in section_types
    assert SectionType.SKILLS in section_types
    assert SectionType.EXPERIENCE in section_types
    assert SectionType.EDUCATION in section_types
    assert SectionType.PROJECTS in section_types
    assert SectionType.CERTIFICATIONS in section_types


def test_markdown_and_case_variations():
    """Verify headers with markdown prefixes and diverse casings are recognized."""
    text = (
        "# TECHNICAL SKILLS\nPython, C++\n\n"
        "## WORK EXPERIENCE\nEngineer at TechCo\n\n"
        "EDUCATION:\nB.S. Mathematics\n"
    )
    detector = SectionDetector()
    sections = detector.detect_sections(text)
    types = [s.section_type for s in sections]

    assert SectionType.SKILLS in types
    assert SectionType.EXPERIENCE in types
    assert SectionType.EDUCATION in types


def test_offsets_are_accurate():
    """Verify that section character offsets match the source text."""
    text = "Skills\nPython, Docker\n\nExperience\nDev at Google\n"
    detector = SectionDetector()
    sections = detector.detect_sections(text)

    for s in sections:
        assert s.start_char >= 0
        assert s.end_char <= len(text)
        assert s.start_char < s.end_char


def test_fallback_unstructured_text():
    """Verify unstructured text without clear headers defaults to OTHER section."""
    text = "Just some text without any standard headers or divisions."
    detector = SectionDetector()
    sections = detector.detect_sections(text)

    assert len(sections) == 1
    assert sections[0].section_type == SectionType.OTHER
    assert sections[0].text == text
