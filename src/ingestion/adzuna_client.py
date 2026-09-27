"""Adzuna API Client for Live Job Ingestion in ResumeIQ.

Fetches real-time job openings from Adzuna global job index and maps them
into ResumeIQ's standard schema with skill extraction and salary normalization.
"""

import json
import logging
import os
import re
import urllib.parse
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "0fbb95bd")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "8cb3e65d9ccbea1d311d8b2c20b73bea")
ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "in")

# Common skill keywords to tag extracted jobs
CORE_TECH_SKILLS = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "React", "Node.js",
    "SQL", "PostgreSQL", "MongoDB", "FastAPI", "Django", "Docker", "Kubernetes",
    "AWS", "Azure", "GCP", "Machine Learning", "Deep Learning", "PyTorch",
    "TensorFlow", "Scikit-Learn", "Data Analysis", "Power BI", "Tableau",
    "DSA", "System Design", "Problem Solving", "NLP", "Computer Vision"
]


def extract_skills_from_text(text: str) -> list[str]:
    """Find matching tech skills in job description."""
    matched = []
    text_lower = text.lower()
    for skill in CORE_TECH_SKILLS:
        # Match as whole word
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            matched.append(skill)
    return matched[:6] or ["Software Development", "Problem Solving"]


def format_salary(salary_min: float | None, salary_max: float | None) -> str | None:
    """Format salary min/max into readable INR LPA or monthly stipend."""
    if not salary_min and not salary_max:
        return "Competitive Compensation"
    
    val = salary_max or salary_min
    if val:
        # If value is in INR lakhs
        if val >= 100000:
            lpa_min = round(salary_min / 100000, 1) if salary_min else round(val / 100000, 1)
            lpa_max = round(salary_max / 100000, 1) if salary_max else lpa_min
            if lpa_min == lpa_max:
                return f"₹ {lpa_min} LPA"
            return f"₹ {lpa_min}–{lpa_max} LPA"
        else:
            return f"₹ {int(val):,}"
    return None


def fetch_adzuna_jobs(
    query: str = "Software Engineer",
    location: str | None = "Bangalore",
    results_per_page: int = 15,
    page: int = 1
) -> list[dict[str, Any]]:
    """Fetch live job postings from Adzuna API.
    
    Args:
        query: Target job title or skill keywords
        location: City or region filter (e.g. Bangalore, Hyderabad)
        results_per_page: Number of postings to fetch (max 50)
        page: Page number
        
    Returns:
        List of normalized job dictionaries ready for frontend / database.
    """
    app_id = os.getenv("ADZUNA_APP_ID", ADZUNA_APP_ID)
    app_key = os.getenv("ADZUNA_APP_KEY", ADZUNA_APP_KEY)
    country = os.getenv("ADZUNA_COUNTRY", ADZUNA_COUNTRY)

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": min(results_per_page, 50),
        "what": query,
        "content-type": "application/json"
    }
    if location and location.lower() != "all" and location.lower() != "any":
        params["where"] = location

    encoded_params = urllib.parse.urlencode(params)
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}?{encoded_params}"

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ResumeIQ-Career-Engine/1.0",
                "Accept": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            raw_results = data.get("results", [])

            normalized_jobs = []
            for item in raw_results:
                title = item.get("title", "").replace("<strong>", "").replace("</strong>", "").strip()
                company_name = item.get("company", {}).get("display_name", "Leading Tech Enterprise")
                location_display = item.get("location", {}).get("display_name", location or "India")
                description = item.get("description", "").replace("<strong>", "").replace("</strong>", "").strip()
                
                salary_min = item.get("salary_min")
                salary_max = item.get("salary_max")
                salary_formatted = format_salary(salary_min, salary_max)
                
                skills = extract_skills_from_text(f"{title} {description}")

                normalized_jobs.append({
                    "id": f"adzuna-{item.get('id')}",
                    "title": title,
                    "company": company_name,
                    "location": location_display,
                    "jobType": "Full-time" if "intern" not in title.lower() else "Internship",
                    "experience": "0–2 yrs" if "intern" in title.lower() or "junior" in title.lower() else "1–3 yrs",
                    "salary": salary_formatted,
                    "matchScore": 90,  # Baseline high match
                    "tags": skills,
                    "description": description[:300] + ("..." if len(description) > 300 else ""),
                    "redirect_url": item.get("redirect_url", "#"),
                    "source": "Adzuna Live Feed"
                })

            return normalized_jobs

    except Exception as exc:
        logger.warning(f"Adzuna API call failed: {exc}. Returning empty list.")
        return []
