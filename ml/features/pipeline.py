"""
Feature Engineering Pipeline (SB2/US18).
Extracts and normalizes features from student profiles for career prediction models.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class FeaturePipeline:
    """
    Feature pipeline for student profile transformation.
    Extracts numerical and categorical attributes into a normalized feature vector.
    """

    FEATURE_NAMES = [
        "cgpa",
        "num_skills",
        "technical_skills_count",
        "soft_skills_count",
        "years_experience",
        "interest_technology",
        "interest_business",
        "interest_healthcare",
        "interest_design",
        "interest_science",
        "personality_openness",
        "personality_conscientiousness",
        "personality_extraversion",
        "personality_agreeableness",
        "personality_neuroticism",
    ]

    TECH_KEYWORDS = {
        "python", "java", "c++", "c#", "javascript", "typescript", "react", "node",
        "sql", "nosql", "aws", "docker", "kubernetes", "git", "machine learning",
        "deep learning", "linux", "cloud", "html", "css", "django", "fastapi"
    }

    SOFT_KEYWORDS = {
        "communication", "teamwork", "leadership", "problem solving", "adaptability",
        "time management", "critical thinking", "negotiation", "presentation", "empathy"
    }

    def __init__(self, scale_features: bool = True):
        self.scale_features = scale_features
        self.scaler = StandardScaler() if scale_features else None
        self.is_fitted = False

    def get_feature_names(self) -> List[str]:
        """Return ordered list of feature names."""
        return list(self.FEATURE_NAMES)

    def extract_features_from_profile(self, profile: Dict[str, Any]) -> np.ndarray:
        """
        Convert a user profile dictionary into a 1D feature vector.

        Accepted profile structure:
        - cgpa: float (default 7.0)
        - skills: list of dicts [{'skill_name', 'skill_type', 'years_experience'}] or strings
        - interests: list of dicts [{'category' or 'interest_name', 'strength'}] or strings
        - personality_traits: list of dicts [{'trait_name', 'score'}] or dict {trait: score}
        - years_experience: float (optional top-level)
        - num_academics: int (optional)
        """
        # 1. CGPA
        cgpa = float(profile.get("cgpa", 7.0) or 7.0)
        cgpa = max(1.0, min(10.0, cgpa))

        # 2. Skills
        raw_skills = profile.get("skills", [])
        tech_count = 0
        soft_count = 0
        max_exp = float(profile.get("years_experience", 0.0) or 0.0)

        for s in raw_skills:
            if isinstance(s, dict):
                name = str(s.get("skill_name", "")).lower()
                stype = str(s.get("skill_type", "")).lower()
                exp = float(s.get("years_experience", 0.0) or 0.0)
                if exp > max_exp:
                    max_exp = exp

                if "tech" in stype:
                    tech_count += 1
                elif "soft" in stype:
                    soft_count += 1
                else:
                    if any(k in name for k in self.TECH_KEYWORDS):
                        tech_count += 1
                    elif any(k in name for k in self.SOFT_KEYWORDS):
                        soft_count += 1
                    else:
                        tech_count += 1
            elif isinstance(s, str):
                s_lower = s.lower()
                if any(k in s_lower for k in self.TECH_KEYWORDS):
                    tech_count += 1
                elif any(k in s_lower for k in self.SOFT_KEYWORDS):
                    soft_count += 1
                else:
                    tech_count += 1

        num_skills = max(len(raw_skills), tech_count + soft_count)
        if num_skills == 0:
            num_skills = int(profile.get("num_skills", 0) or 0)
        if tech_count == 0 and "technical_skills_count" in profile:
            tech_count = int(profile.get("technical_skills_count", 0))
        if soft_count == 0 and "soft_skills_count" in profile:
            soft_count = int(profile.get("soft_skills_count", 0))

        # 3. Interests
        interests_dict = {
            "technology": float(profile.get("interest_technology", 0.0) or 0.0),
            "business": float(profile.get("interest_business", 0.0) or 0.0),
            "healthcare": float(profile.get("interest_healthcare", 0.0) or 0.0),
            "design": float(profile.get("interest_design", 0.0) or 0.0),
            "science": float(profile.get("interest_science", 0.0) or 0.0),
        }

        raw_interests = profile.get("interests", [])
        for item in raw_interests:
            if isinstance(item, dict):
                iname = str(item.get("interest_name") or item.get("category") or "").lower()
                strength = float(item.get("strength", 1.0) or 1.0)
                norm_strength = 1.0 if strength >= 1.0 else strength
            else:
                iname = str(item).lower()
                norm_strength = 1.0

            for cat in interests_dict:
                if cat in iname:
                    interests_dict[cat] = max(interests_dict[cat], norm_strength)

        # 4. Personality
        personality_dict = {
            "openness": 7.0,
            "conscientiousness": 7.0,
            "extraversion": 6.0,
            "agreeableness": 7.0,
            "neuroticism": 4.0,
        }

        # Check top-level personality keys
        for key in personality_dict:
            full_key = f"personality_{key}"
            if full_key in profile and profile[full_key] is not None:
                personality_dict[key] = float(profile[full_key])

        # Check personality_traits list/dict
        raw_traits = profile.get("personality_traits", [])
        if isinstance(raw_traits, dict):
            for k, v in raw_traits.items():
                k_clean = k.lower().replace("personality_", "")
                if k_clean in personality_dict and v is not None:
                    personality_dict[k_clean] = float(v)
        elif isinstance(raw_traits, list):
            for item in raw_traits:
                if isinstance(item, dict):
                    tname = str(item.get("trait_name", "")).lower().replace("personality_", "")
                    score = float(item.get("score", 7.0) or 7.0)
                    if tname in personality_dict:
                        personality_dict[tname] = score

        vector = [
            cgpa,
            float(num_skills),
            float(tech_count),
            float(soft_count),
            float(min(10.0, max_exp)),
            float(interests_dict["technology"]),
            float(interests_dict["business"]),
            float(interests_dict["healthcare"]),
            float(interests_dict["design"]),
            float(interests_dict["science"]),
            float(personality_dict["openness"]),
            float(personality_dict["conscientiousness"]),
            float(personality_dict["extraversion"]),
            float(personality_dict["agreeableness"]),
            float(personality_dict["neuroticism"]),
        ]

        return np.array(vector, dtype=np.float32)

    def fit(self, X: Union[np.ndarray, pd.DataFrame]) -> "FeaturePipeline":
        """Fit scaler on feature matrix."""
        if isinstance(X, pd.DataFrame):
            X_mat = X[self.FEATURE_NAMES].values
        else:
            X_mat = np.asarray(X)

        if self.scale_features and self.scaler is not None:
            self.scaler.fit(X_mat)
        self.is_fitted = True
        return self

    def transform(self, X: Union[np.ndarray, pd.DataFrame, Dict[str, Any]]) -> np.ndarray:
        """Transform feature vector or matrix."""
        if isinstance(X, dict):
            vec = self.extract_features_from_profile(X)
            mat = vec.reshape(1, -1)
        elif isinstance(X, pd.DataFrame):
            mat = X[self.FEATURE_NAMES].values
        else:
            mat = np.asarray(X)
            if mat.ndim == 1:
                mat = mat.reshape(1, -1)

        if self.scale_features and self.scaler is not None and self.is_fitted:
            return self.scaler.transform(mat)
        return mat

    def fit_transform(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """Fit scaler and transform in one step."""
        return self.fit(X).transform(X)

    def save(self, filepath: Union[str, Path]) -> None:
        """Serialize pipeline to disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "FeaturePipeline":
        """Load serialized pipeline from disk."""
        path = Path(filepath)
        if not path.exists():
            return cls()
        return joblib.load(path)
