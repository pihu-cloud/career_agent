"""
Rule-Based Fallback Recommender (SB2/US39).
Provides deterministic heuristic recommendations when ML models encounter cold-start,
missing dependencies, or runtime exceptions.
"""

from typing import Any, Dict, List
from ml.data.sample_data import CAREER_LABELS
from ml.models.content_filter import ContentBasedFilter


class RuleBasedRecommender:
    """Heuristic rule-based engine ensuring uninterrupted career guidance."""

    def __init__(self):
        self.content_filter = ContentBasedFilter()

    def recommend(self, user_profile: Dict[str, Any], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Produce at least 3 career recommendations using deterministic domain rules.
        """
        # Collect raw skills and interests
        raw_skills = user_profile.get("skills", [])
        clean_skills = set()
        for s in raw_skills:
            if isinstance(s, dict):
                clean_skills.add(str(s.get("skill_name", "")).lower())
            else:
                clean_skills.add(str(s).lower())

        raw_interests = user_profile.get("interests", [])
        clean_interests = set()
        for item in raw_interests:
            if isinstance(item, dict):
                clean_interests.add(str(item.get("interest_name") or item.get("category") or "").lower())
            else:
                clean_interests.add(str(item).lower())

        career_scores = {c: 10.0 for c in CAREER_LABELS}

        # Rule 1: Technical & Software Engineering
        tech_indicators = {"python", "java", "c++", "javascript", "sql", "git", "coding", "software"}
        if clean_skills.intersection(tech_indicators) or any("tech" in i for i in clean_interests):
            career_scores["Software Engineer"] += 40.0
            career_scores["DevOps Engineer"] += 30.0

        # Rule 2: Data Science & AI/ML
        data_indicators = {"data", "machine learning", "pandas", "numpy", "statistics", "analytics", "ai"}
        if clean_skills.intersection(data_indicators) or any("science" in i or "data" in i for i in clean_interests):
            career_scores["Data Scientist"] += 45.0
            career_scores["AI/ML Engineer"] += 40.0

        # Rule 3: Design & UX
        design_indicators = {"figma", "ui", "ux", "design", "wireframing", "prototyping", "creative"}
        if clean_skills.intersection(design_indicators) or any("design" in i or "art" in i for i in clean_interests):
            career_scores["UX Designer"] += 50.0

        # Rule 4: Business & Product Management
        biz_indicators = {"management", "business", "leadership", "agile", "strategy", "communication"}
        if clean_skills.intersection(biz_indicators) or any("business" in i or "finance" in i for i in clean_interests):
            career_scores["Product Manager"] += 35.0
            career_scores["Business Analyst"] += 35.0

        # Rule 5: Cybersecurity
        sec_indicators = {"security", "network", "linux", "penetration", "cyber", "firewall"}
        if clean_skills.intersection(sec_indicators) or any("security" in i for i in clean_interests):
            career_scores["Cybersecurity Analyst"] += 50.0

        # Rule 6: Finance
        fin_indicators = {"finance", "accounting", "excel", "economics", "investment", "valuation"}
        if clean_skills.intersection(fin_indicators) or any("finance" in i or "market" in i for i in clean_interests):
            career_scores["Financial Analyst"] += 50.0

        # Rule 7: Healthcare
        health_indicators = {"health", "medical", "clinical", "biology", "informatics", "hipaa"}
        if clean_skills.intersection(health_indicators) or any("health" in i for i in clean_interests):
            career_scores["Healthcare Informatics"] += 50.0

        # Sort careers descending
        ranked = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        max_possible = max([s for _, s in ranked]) or 1.0

        for career, score in ranked[:max(3, top_k)]:
            norm_score = round(min(0.95, score / (max_possible + 10.0)), 3)
            gaps = self.content_filter.compute_skill_gap(raw_skills, career)

            results.append({
                "career": career,
                "score": norm_score,
                "confidence": 0.70,
                "reason": f"Selected via rule-based heuristics mapping your verified skills and background to {career}.",
                "skill_gaps": gaps,
                "explanation": f"Rule-based match identifying alignment with {career} based on core interest and competence markers.",
                "fallback_active": True,
            })

        return results
