"""
Compatibility and Skill-Gap Scoring (SB2/US23).
Computes 0-100 career compatibility scores based on skill match, interest alignment,
and personality fit, as well as granular skill-gap breakdowns.
"""

from typing import Any, Dict, List, Union
from ml.models.content_filter import ContentBasedFilter


def compute_skill_gap_score(
    user_skills: List[Union[str, Dict[str, Any]]],
    required_skills: List[str],
) -> Dict[str, Any]:
    """
    Calculate granular skill gap between user acquired skills and role requirements.
    Returns: {gap_score, missing_skills, present_skills, gap_percentage}
    """
    clean_user = set()
    for s in user_skills:
        if isinstance(s, dict):
            clean_user.add(str(s.get("skill_name", "")).strip().lower())
        else:
            clean_user.add(str(s).strip().lower())

    clean_req = [r.strip().lower() for r in required_skills if r]
    if not clean_req:
        return {
            "gap_score": 0.0,
            "missing_skills": [],
            "present_skills": list(clean_user),
            "gap_percentage": 0.0,
        }

    present = []
    missing = []
    for req in clean_req:
        if any(req in u or u in req for u in clean_user):
            present.append(req)
        else:
            missing.append(req)

    gap_ratio = len(missing) / len(clean_req)
    return {
        "gap_score": round(gap_ratio, 3),
        "missing_skills": missing,
        "present_skills": present,
        "gap_percentage": round(gap_ratio * 100.0, 1),
    }


def compute_compatibility_score(user_profile: Dict[str, Any], career: str) -> float:
    """
    Calculate an overall 0-100 career compatibility score.
    Weights: 50% Skills Match, 30% Interest Alignment, 20% Personality Fit.
    """
    career_profile = ContentBasedFilter.CAREER_PROFILES.get(career)
    if not career_profile:
        return 50.0

    # 1. Skill Match Component (0 - 100)
    user_skills = user_profile.get("skills", [])
    gap_info = compute_skill_gap_score(user_skills, career_profile["required_skills"])
    skills_match_score = (1.0 - gap_info["gap_score"]) * 100.0

    # 2. Interest Alignment Component (0 - 100)
    user_interests = user_profile.get("interests", [])
    clean_interests = []
    for item in user_interests:
        if isinstance(item, dict):
            clean_interests.append(str(item.get("interest_name") or item.get("category") or "").lower())
        else:
            clean_interests.append(str(item).lower())

    pref_interests = [p.lower() for p in career_profile["preferred_interests"]]
    if pref_interests:
        matched_interests = sum(
            1 for p in pref_interests if any(p in u or u in p for u in clean_interests)
        )
        interest_score = min(100.0, (matched_interests / len(pref_interests)) * 100.0)
    else:
        interest_score = 60.0

    # 3. Personality Fit Component (0 - 100)
    ideal_personality = career_profile.get("personality_fit", {})
    user_traits = user_profile.get("personality_traits", {})

    diffs = []
    if ideal_personality:
        for trait, ideal_val in ideal_personality.items():
            actual_val = None
            if isinstance(user_traits, dict):
                actual_val = user_traits.get(trait) or user_traits.get(f"personality_{trait}")
            elif isinstance(user_traits, list):
                for t in user_traits:
                    if isinstance(t, dict) and t.get("trait_name") == trait:
                        actual_val = t.get("score")
                        break

            if actual_val is None:
                actual_val = user_profile.get(f"personality_{trait}", 6.0)

            actual_val = float(actual_val or 6.0)
            diffs.append(abs(ideal_val - actual_val))

        avg_diff = sum(diffs) / len(diffs) if diffs else 1.5
        # Scale difference: 0 diff = 100, 5 diff = 50, 10 diff = 0
        personality_score = max(0.0, 100.0 - (avg_diff * 10.0))
    else:
        personality_score = 75.0

    # Weighted blend
    overall_score = (0.50 * skills_match_score) + (0.30 * interest_score) + (0.20 * personality_score)
    return round(float(min(100.0, max(0.0, overall_score))), 2)
