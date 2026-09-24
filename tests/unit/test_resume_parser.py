"""Unit tests for structured resume parsing, date edge cases, and tenure deduplication."""

from src.preprocessing.resume_parser import ResumeParser


def test_resume_parser_end_to_end():
    """Verify parsing experience, education, total years, and source span presence."""
    resume_text = (
        "Alice Walker\n"
        "Machine Learning Engineer\n\n"
        "Experience\n"
        "Senior ML Engineer at TechCorp\n"
        "2021 - 2024\n"
        "Designed and shipped vector search and ranking pipelines.\n\n"
        "Data Scientist at AlphaLabs\n"
        "2019 - 2021\n"
        "Trained PyTorch transformer models.\n\n"
        "Education\n"
        "B.Tech in Computer Science and Engineering, 2019\n\n"
        "Projects\n"
        "Recommendation Engine: Scalable BM25 and neural reranking system.\n\n"
        "Certifications\n"
        "TensorFlow Developer Certificate\n"
    )

    parser = ResumeParser()
    parsed = parser.parse(resume_text)

    # 1. Experience check
    assert len(parsed.experience) == 2
    assert "TechCorp" in (parsed.experience[0].org or "")
    assert parsed.experience[0].start_year == 2021
    assert parsed.experience[0].end_year == 2024
    assert parsed.experience[0].source_span.section == "Experience"
    assert parsed.experience[0].source_span.start_char >= 0

    # 2. Total years calculated across non-overlapping tenures (2019-2021: 2 yrs + 2021-2024: 3 yrs = 5 yrs)
    assert parsed.total_years == 5.0

    # 3. Education check
    assert len(parsed.education) >= 1
    assert "B.Tech" in parsed.education[0].degree
    assert "Computer Science" in (parsed.education[0].field or "")
    assert parsed.education[0].year == 2019
    assert parsed.education[0].source_span.section == "Education"

    # 4. Projects check
    assert len(parsed.projects) == 1
    assert "Recommendation Engine" in parsed.projects[0].name
    assert parsed.projects[0].source_span.section == "Projects"

    # 5. Certifications check
    assert len(parsed.certifications) == 1
    assert "TensorFlow Developer Certificate" in parsed.certifications[0].name
    assert parsed.certifications[0].source_span.section == "Certifications"


def test_overlapping_tenure_calculation():
    """Verify overlapping tenures are deduplicated when computing total_years."""
    resume_text = (
        "Experience\n"
        "Consultant at BetaInc\n"
        "2020 - 2023\n"
        "Full time role\n\n"
        "Part-time Lecturer at University\n"
        "2021 - 2022\n"  # Entirely within 2020 - 2023
        "Teaching ML fundamentals\n"
    )
    parser = ResumeParser()
    parsed = parser.parse(resume_text)

    assert len(parsed.experience) == 2
    # Combined span is 2020 to 2023 = 3 years (not 3 + 1 = 4)
    assert parsed.total_years == 3.0


def test_concurrent_and_promotion_tenure_dedup():
    """Verify concurrent roles and promotions within the same company are not double counted."""
    resume_text = (
        "Experience\n"
        "Staff Software Engineer at MetaCorp\n"
        "2021 - 2024\n"
        "Technical leadership and architectural design.\n\n"
        "Senior Software Engineer at MetaCorp\n"
        "2019 - 2021\n"
        "Continuous internal promotion: 2019 to 2024 continuous.\n\n"
        "Technical Advisor at StartupInc\n"
        "2022 - 2023\n"  # Concurrent role during 2021-2024 tenure
        "Advising on ML search backend.\n"
    )
    parser = ResumeParser()
    parsed = parser.parse(resume_text)

    assert len(parsed.experience) == 3
    # 2019 to 2024 span is 5.0 years; concurrent 2022-2023 role must not add to 5.0
    assert parsed.total_years == 5.0


def test_international_and_slash_date_formats():
    """Verify parsing non-US dates (MM/YYYY), dot dates (YYYY.MM), and Present/Current keywords."""
    resume_text = (
        "Experience\n"
        "Senior Data Engineer at GlobalBank\n"
        "06/2020 - 08/2023\n"
        "Built ETL lakehouse.\n\n"
        "Data Analyst at InfoSys\n"
        "2018.01 - 2020.05\n"
        "SQL queries and dashboarding.\n"
    )
    parser = ResumeParser()
    parsed = parser.parse(resume_text)

    assert len(parsed.experience) == 2
    assert parsed.experience[0].start_year == 2020
    assert parsed.experience[0].end_year == 2023
    assert parsed.experience[1].start_year == 2018
    assert parsed.experience[1].end_year == 2020


def test_single_year_experience_entry():
    """Verify single-year entries (e.g., 'Research Fellow (2021)') are parsed properly."""
    resume_text = (
        "Experience\n"
        "Research Fellow at Oxford (2021)\n"
        "Published NLP benchmark paper.\n"
    )
    parser = ResumeParser()
    parsed = parser.parse(resume_text)

    assert len(parsed.experience) == 1
    assert parsed.experience[0].start_year == 2021
    assert parsed.experience[0].end_year == 2021
    assert parsed.total_years == 1.0


def test_source_spans_are_valid_substrings():
    """Verify all source spans index valid slices of the original resume text."""
    resume_text = (
        "Education\n"
        "Bachelor of Science in Mathematics, 2018\n\n"
        "Certifications\n"
        "Certified Kubernetes Administrator\n"
    )
    parser = ResumeParser()
    parsed = parser.parse(resume_text)

    for edu in parsed.education:
        span_text = resume_text[edu.source_span.start_char : edu.source_span.end_char]
        assert edu.degree in span_text

    for cert in parsed.certifications:
        span_text = resume_text[cert.source_span.start_char : cert.source_span.end_char]
        assert cert.name in span_text
