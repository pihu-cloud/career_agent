"""
ML Input and Output Validators (SB2/US37).
Validates payload integrity for student profiles before inference and checks
model recommendation output schemas for reliability and security.
"""

from typing import Any, Dict, List, Tuple
from ml.data.sample_data import CAREER_LABELS


def validate_prediction_input(profile: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that student profile payload contains valid types and acceptable ranges.
    Returns: (is_valid: bool, error_message: str)
    """
    if not isinstance(profile, dict):
        return False, "Profile input must be a JSON/dict object."

    # Validate CGPA if present
    if "cgpa" in profile and profile["cgpa"] is not None:
        try:
            cgpa = float(profile["cgpa"])
            if cgpa < 0.0 or cgpa > 10.0:
                return False, f"CGPA must be between 0.0 and 10.0; received {cgpa}."
        except (ValueError, TypeError):
            return False, "CGPA must be a valid numerical value."

    # Validate skills if present
    if "skills" in profile and profile["skills"] is not None:
        if not isinstance(profile["skills"], list):
            return False, "Skills field must be a list of skill objects or strings."

    # Validate interests if present
    if "interests" in profile and profile["interests"] is not None:
        if not isinstance(profile["interests"], list):
            return False, "Interests field must be a list of interest items."

    # Validate personality if present
    if "personality_traits" in profile and profile["personality_traits"] is not None:
        if not isinstance(profile["personality_traits"], (dict, list)):
            return False, "Personality traits must be a dictionary or list."

    # Check that at least some informative data exists
    has_skills = bool(profile.get("skills"))
    has_interests = bool(profile.get("interests"))
    has_cgpa = profile.get("cgpa") is not None
    has_resume = bool(profile.get("resume_text"))

    if not (has_skills or has_interests or has_cgpa or has_resume):
        return False, "Profile must contain at least one of: skills, interests, CGPA, or resume text."

    return True, ""


def validate_model_output(output: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Validate that model recommendation results adhere to standard schema.
    Returns: (is_valid: bool, error_message: str)
    """
    if not isinstance(output, list):
        return False, "Model output must be a list of recommendation objects."

    if len(output) == 0:
        return False, "Model output list cannot be empty."

    for idx, item in enumerate(output):
        if not isinstance(item, dict):
            return False, f"Recommendation item at index {idx} must be a dict."

        if "career" not in item:
            return False, f"Recommendation at index {idx} is missing 'career' field."

        if item["career"] not in CAREER_LABELS:
            return False, f"Unknown career '{item['career']}' at index {idx}."

        if "score" not in item:
            return False, f"Recommendation at index {idx} is missing 'score' field."

        try:
            score = float(item["score"])
            if score < 0.0 or score > 1.0:
                return False, f"Score at index {idx} out of range [0.0, 1.0]: {score}."
        except (ValueError, TypeError):
            return False, f"Score at index {idx} must be numeric."

    return True, ""
