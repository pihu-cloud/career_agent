"""
Historical Cohort and Alumni Pattern Analytics (SB2/US13, US28).
Analyzes historical student career pathways and extracts top-performer benchmarks
to inform personalized student guidance.
"""

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional
import numpy as np


def analyze_career_patterns(profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze student cohort data to discover historical career distribution patterns,
    average academic metrics, and skill clusters.
    """
    if not profiles:
        return {
            "total_profiles_analyzed": 0,
            "career_distribution": {},
            "average_cgpa_by_career": {},
            "top_skills_by_career": {},
        }

    career_counts = Counter()
    career_cgpas = defaultdict(list)
    career_skills = defaultdict(Counter)

    for p in profiles:
        career = str(p.get("career_label") or p.get("career") or "Unassigned")
        career_counts[career] += 1

        if "cgpa" in p and p["cgpa"] is not None:
            try:
                career_cgpas[career].append(float(p["cgpa"]))
            except (ValueError, TypeError):
                pass

        raw_skills = p.get("skills", [])
        for s in raw_skills:
            if isinstance(s, dict):
                sname = str(s.get("skill_name", "")).strip().lower()
            else:
                sname = str(s).strip().lower()
            if sname:
                career_skills[career][sname] += 1

    total = len(profiles)
    distribution = {
        career: {
            "count": count,
            "percentage": round((count / total) * 100.0, 1),
        }
        for career, count in career_counts.most_common()
    }

    avg_cgpas = {
        career: round(float(np.mean(cgpa_list)), 2) if cgpa_list else 7.0
        for career, cgpa_list in career_cgpas.items()
    }

    top_skills = {
        career: [s for s, _ in skill_counter.most_common(5)]
        for career, skill_counter in career_skills.items()
    }

    return {
        "total_profiles_analyzed": total,
        "career_distribution": distribution,
        "average_cgpa_by_career": avg_cgpas,
        "top_skills_by_career": top_skills,
    }


def analyze_top_performers(profiles: List[Dict[str, Any]], career: str) -> Dict[str, Any]:
    """
    Extract benchmark skills, academic standards, and traits of top performers in a target career.
    """
    cohort = [
        p for p in profiles
        if str(p.get("career_label") or p.get("career") or "").lower() == career.lower()
    ]

    if not cohort:
        return {
            "career": career,
            "top_performers_count": 0,
            "benchmark_cgpa": 8.0,
            "essential_skills": [],
            "message": f"No historical cohort records found for '{career}'. Using industry baseline.",
        }

    # Filter top quartile by CGPA or skill count
    cgpas = [float(p.get("cgpa", 7.0) or 7.0) for p in cohort]
    threshold_cgpa = float(np.percentile(cgpas, 60)) if cgpas else 7.5

    top_performers = [p for p in cohort if float(p.get("cgpa", 7.0) or 7.0) >= threshold_cgpa]
    if not top_performers:
        top_performers = cohort

    skill_counter = Counter()
    for p in top_performers:
        for s in p.get("skills", []):
            if isinstance(s, dict):
                sname = str(s.get("skill_name", "")).strip().lower()
            else:
                sname = str(s).strip().lower()
            if sname:
                skill_counter[sname] += 1

    essential_skills = [
        {"skill": s, "frequency": count, "prevalence_percentage": round((count / len(top_performers)) * 100.0, 1)}
        for s, count in skill_counter.most_common(6)
    ]

    avg_top_cgpa = float(np.mean([float(p.get("cgpa", 7.0) or 7.0) for p in top_performers]))

    return {
        "career": career,
        "total_cohort_count": len(cohort),
        "top_performers_count": len(top_performers),
        "benchmark_cgpa": round(avg_top_cgpa, 2),
        "essential_skills": essential_skills,
        "key_differentiators": [item["skill"] for item in essential_skills[:3]],
    }
