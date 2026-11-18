"""
Collaborative Filtering Model (SB2/US3).
Uses cosine similarity over student feature vectors to discover similar peers
and recommend career paths based on peer outcomes.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from ml.data.sample_data import CAREER_LABELS, generate_career_training_data
from ml.features.pipeline import FeaturePipeline


class CollaborativeFilter:
    """
    User-User Collaborative Filtering Recommender.
    Matches student profile vectors against historical alumni/peer database.
    """

    def __init__(self, pipeline: Optional[FeaturePipeline] = None):
        self.pipeline = pipeline or FeaturePipeline()
        self.user_ids: List[str] = []
        self.user_vectors: Optional[np.ndarray] = None
        self.user_careers: List[str] = []
        self.user_metadata: List[Dict[str, Any]] = []
        self.is_fitted: bool = False

    def _generate_default_user_base(self, n_users: int = 150):
        """Generate synthetic peer cohort (SAMPLE DATA) if none provided."""
        df = generate_career_training_data(n_samples=n_users, random_state=42)
        profiles = []
        for i, row in df.iterrows():
            uid = f"peer_{i+1:03d}"
            prof = {
                "user_id": uid,
                "cgpa": row["cgpa"],
                "num_skills": row["num_skills"],
                "technical_skills_count": row["technical_skills_count"],
                "soft_skills_count": row["soft_skills_count"],
                "years_experience": row["years_experience"],
                "interest_technology": row["interest_technology"],
                "interest_business": row["interest_business"],
                "interest_healthcare": row["interest_healthcare"],
                "interest_design": row["interest_design"],
                "interest_science": row["interest_science"],
                "personality_openness": row["personality_openness"],
                "personality_conscientiousness": row["personality_conscientiousness"],
                "personality_extraversion": row["personality_extraversion"],
                "personality_agreeableness": row["personality_agreeableness"],
                "personality_neuroticism": row["personality_neuroticism"],
                "career_label": row["career_label"],
            }
            profiles.append(prof)
        return profiles

    def fit(self, user_profiles: Optional[List[Dict[str, Any]]] = None) -> "CollaborativeFilter":
        """
        Fit collaborative filter on a list of student profile dicts.
        Each profile dict should have feature fields or skills/interests + 'career_label'.
        """
        if not user_profiles:
            user_profiles = self._generate_default_user_base()

        self.user_ids = []
        self.user_careers = []
        self.user_metadata = []
        vectors = []

        for idx, p in enumerate(user_profiles):
            uid = str(p.get("user_id") or p.get("id") or f"peer_{idx+1:03d}")
            career = str(p.get("career_label") or p.get("career") or CAREER_LABELS[idx % len(CAREER_LABELS)])
            vec = self.pipeline.extract_features_from_profile(p)
            vectors.append(vec)
            self.user_ids.append(uid)
            self.user_careers.append(career)
            self.user_metadata.append({
                "user_id": uid,
                "career": career,
                "cgpa": p.get("cgpa", 7.0),
            })

        self.user_vectors = np.array(vectors, dtype=np.float32)
        self.is_fitted = True
        return self

    def get_similar_users(self, user_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find the top_k most similar peers for a known user_id."""
        if not self.is_fitted or self.user_vectors is None:
            self.fit()

        if user_id not in self.user_ids:
            return []

        idx = self.user_ids.index(user_id)
        target_vec = self.user_vectors[idx].reshape(1, -1)
        sims = cosine_similarity(target_vec, self.user_vectors)[0]

        # Exclude self
        sim_indices = np.argsort(sims)[::-1]
        results = []
        for i in sim_indices:
            if self.user_ids[i] == user_id:
                continue
            results.append({
                "user_id": self.user_ids[i],
                "similarity": round(float(sims[i]), 4),
                "career": self.user_careers[i],
                "metadata": self.user_metadata[i],
            })
            if len(results) >= top_k:
                break
        return results

    def recommend_careers(self, user_profile: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recommend careers based on weighted similarity to peer students.
        Returns: list of [{career: str, score: float, confidence: float, peer_count: int}]
        """
        if not self.is_fitted or self.user_vectors is None:
            self.fit()

        target_vec = self.pipeline.extract_features_from_profile(user_profile).reshape(1, -1)
        sims = cosine_similarity(target_vec, self.user_vectors)[0]

        career_scores = defaultdict(float)
        career_weights = defaultdict(float)
        career_peer_counts = defaultdict(int)

        for sim, career in zip(sims, self.user_careers):
            # Apply positive similarity threshold
            weight = max(0.0, float(sim))
            career_scores[career] += weight
            career_weights[career] += 1.0
            career_peer_counts[career] += 1

        # Normalize scores to 0.0 - 1.0
        recommendations = []
        max_score = max(career_scores.values()) if career_scores else 1.0

        for career in CAREER_LABELS:
            raw_s = career_scores.get(career, 0.0)
            norm_s = round(raw_s / (max_score + 1e-9), 4)
            recommendations.append({
                "career": career,
                "score": norm_s,
                "confidence": round(min(0.95, norm_s * 0.9 + 0.05), 4),
                "peer_count": career_peer_counts.get(career, 0),
            })

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:top_k]

    def save(self, filepath: Union[str, Path]) -> None:
        """Save model to disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "CollaborativeFilter":
        """Load model from disk."""
        path = Path(filepath)
        if not path.exists():
            instance = cls()
            instance.fit()
            return instance
        return joblib.load(path)
