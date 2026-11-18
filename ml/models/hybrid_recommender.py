"""
Hybrid Recommender Model (SB2/US5).
Combines XGBoost Classifier, Collaborative Filtering, and Content-Based Filtering
into a weighted ensemble with skill-gap feedback and human-interpretable explanations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib

from ml.data.sample_data import CAREER_LABELS
from ml.features.pipeline import FeaturePipeline
from ml.models.career_predictor import CareerPredictor
from ml.models.collaborative_filter import CollaborativeFilter
from ml.models.content_filter import ContentBasedFilter


class HybridRecommender:
    """Ensemble recommender integrating XGBoost, Collaborative, and Content-based models."""

    DEFAULT_WEIGHTS = {
        "xgboost": 0.50,
        "collaborative": 0.25,
        "content": 0.25,
    }

    def __init__(
        self,
        predictor: Optional[CareerPredictor] = None,
        collaborative: Optional[CollaborativeFilter] = None,
        content_filter: Optional[ContentBasedFilter] = None,
        feature_pipeline: Optional[FeaturePipeline] = None,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.predictor = predictor or CareerPredictor()
        self.collaborative = collaborative or CollaborativeFilter()
        self.content_filter = content_filter or ContentBasedFilter()
        self.feature_pipeline = feature_pipeline or FeaturePipeline()
        self.weights = weights or dict(self.DEFAULT_WEIGHTS)

    def recommend(self, user_profile: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Produce top_k career pathway recommendations with ensemble scores,
        skill gaps, and explanations.
        """
        # 1. Feature extraction for XGBoost
        feat_vec = self.feature_pipeline.extract_features_from_profile(user_profile)
        xgb_proba_list = self.predictor.predict_proba(feat_vec)
        xgb_scores = xgb_proba_list[0] if xgb_proba_list else {}

        # 2. Collaborative filtering scores
        collab_recs = self.collaborative.recommend_careers(user_profile, top_k=len(CAREER_LABELS))
        collab_scores = {r["career"]: r["score"] for r in collab_recs}

        # 3. Content-based filtering scores
        content_recs = self.content_filter.recommend(user_profile, top_k=len(CAREER_LABELS))
        content_scores = {r["career"]: r["score"] for r in content_recs}
        content_reasons = {r["career"]: r.get("reason", "") for r in content_recs}
        content_gaps = {r["career"]: r.get("skill_gaps", {}) for r in content_recs}

        w_xgb = self.weights.get("xgboost", 0.50)
        w_collab = self.weights.get("collaborative", 0.25)
        w_content = self.weights.get("content", 0.25)
        total_w = w_xgb + w_collab + w_content

        user_skills = user_profile.get("skills", [])

        ensemble_results = []
        for career in CAREER_LABELS:
            s_xgb = xgb_scores.get(career, 0.0)
            s_collab = collab_scores.get(career, 0.0)
            s_content = content_scores.get(career, 0.0)

            blended_score = (w_xgb * s_xgb + w_collab * s_collab + w_content * s_content) / total_w
            blended_score = round(float(blended_score), 4)

            # Skill gaps for this career
            gaps = content_gaps.get(career)
            if not gaps:
                gaps = self.content_filter.compute_skill_gap(user_skills, career)

            # Agreement metric across the 3 models for confidence estimation
            model_values = [s_xgb, s_collab, s_content]
            std_dev = float(np_std := (sum((v - sum(model_values) / 3) ** 2 for v in model_values) / 3) ** 0.5)
            agreement = max(0.1, 1.0 - std_dev)
            confidence = round(min(0.98, max(0.40, blended_score * 0.7 + agreement * 0.3)), 3)

            explanation = (
                f"Recommended with {int(blended_score * 100)}% fit based on predictive pathway alignment, "
                f"strong peer similarity, and {len(gaps.get('present_skills', []))} matching key skills."
            )

            ensemble_results.append({
                "career": career,
                "score": blended_score,
                "confidence": confidence,
                "reason": content_reasons.get(career, f"High synergy with your professional background in {career}."),
                "skill_gaps": gaps,
                "explanation": explanation,
                "component_scores": {
                    "xgboost": round(s_xgb, 4),
                    "collaborative": round(s_collab, 4),
                    "content": round(s_content, 4),
                },
            })

        ensemble_results.sort(key=lambda x: x["score"], reverse=True)
        return ensemble_results[:top_k]

    def save(self, filepath: Union[str, Path]) -> None:
        """Save hybrid recommender and all constituent sub-models."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "HybridRecommender":
        """Load hybrid recommender from disk."""
        path = Path(filepath)
        if not path.exists():
            return cls()
        return joblib.load(path)
