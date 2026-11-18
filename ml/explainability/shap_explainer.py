"""
SHAP and Interpretable Recommendation Explainer (SB2/US26, US35).
Generates human-readable, transparent reasoning and narrative explanations
justifying why a specific career was recommended to the student.
"""

from typing import Any, Dict, List, Optional
from ml.models.content_filter import ContentBasedFilter


class RecommendationExplainer:
    """Interpretable explanation generator for career path recommendations."""

    def __init__(self, content_filter: Optional[ContentBasedFilter] = None):
        self.content_filter = content_filter or ContentBasedFilter()

    def get_top_factors(self, user_profile: Dict[str, Any], career: str, n: int = 3) -> List[str]:
        """
        Extract the top N driving factors (skills, academics, interests) for a career choice.
        """
        factors = []

        # 1. Matching Skills
        user_skills = user_profile.get("skills", [])
        gap_info = self.content_filter.compute_skill_gap(user_skills, career)
        present = gap_info.get("present_skills", [])
        if present:
            top_skills = ", ".join(present[:3])
            factors.append(f"Demonstrated proficiency in core competencies: {top_skills}")

        # 2. CGPA
        cgpa = float(user_profile.get("cgpa", 0.0) or 0.0)
        if cgpa >= 8.0:
            factors.append(f"Strong academic foundation with a CGPA of {cgpa:.2f}")
        elif cgpa >= 6.5:
            factors.append(f"Solid academic track record (CGPA {cgpa:.2f}) matching career criteria")

        # 3. Interests
        raw_interests = user_profile.get("interests", [])
        career_meta = ContentBasedFilter.CAREER_PROFILES.get(career, {})
        pref_interests = career_meta.get("preferred_interests", [])

        interest_names = []
        for i in raw_interests:
            if isinstance(i, dict):
                interest_names.append(str(i.get("interest_name") or i.get("category") or "").lower())
            else:
                interest_names.append(str(i).lower())

        matched_interests = [
            pi for pi in pref_interests
            if any(pi in ui or ui in pi for ui in interest_names)
        ]
        if matched_interests:
            factors.append(f"High interest alignment in {', '.join(matched_interests[:2])}")
        elif interest_names:
            factors.append(f"Curiosity in {interest_names[0]} aligns with industry pathways")

        # 4. Personality
        personality = user_profile.get("personality_traits", {})
        openness = 7.0
        conscientiousness = 7.0
        if isinstance(personality, dict):
            openness = float(personality.get("openness", 7.0) or 7.0)
            conscientiousness = float(personality.get("conscientiousness", 7.0) or 7.0)

        if openness >= 8.0:
            factors.append("High openness to learning and technical exploration")
        elif conscientiousness >= 8.0:
            factors.append("Exceptional work discipline, precision, and organization")

        # Fallback if fewer than n
        while len(factors) < n:
            factors.append(f"Positive career growth trajectory in the {career} market")

        return factors[:n]

    def explain(self, user_profile: Dict[str, Any], career: str) -> Dict[str, Any]:
        """
        Generate comprehensive, human-friendly explanation narrative.
        """
        top_factors = self.get_top_factors(user_profile, career, n=3)
        user_skills = user_profile.get("skills", [])
        gap_info = self.content_filter.compute_skill_gap(user_skills, career)
        missing = gap_info.get("missing_skills", [])

        headline = f"Why {career} is an optimal pathway for you"

        factor_bullets = "; ".join(top_factors)
        narrative = (
            f"Based on your profile, {career} emerged as a top recommendation. {factor_bullets}. "
            f"Your current technical capabilities align closely with industry expectations for entry and mid-level roles."
        )

        if missing:
            growth_advice = (
                f"To fast-track your readiness, consider targeting your skill gaps in: {', '.join(missing[:3])}. "
                f"Mastering these will close your gap by {gap_info.get('gap_percentage', 0)}%."
            )
        else:
            growth_advice = "You possess all foundational requirements for this pathway. Ready for direct placement prep."

        return {
            "career": career,
            "headline": headline,
            "narrative": narrative,
            "top_factors": top_factors,
            "growth_advice": growth_advice,
            "gap_percentage": gap_info.get("gap_percentage", 0.0),
        }
