"""
Ensemble Recommender Wrapper (SB2/US30).
Performs multi-model voting, variance analysis, and statistical confidence intervals
for robust career pathway recommendations.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np

from ml.data.sample_data import CAREER_LABELS
from ml.models.hybrid_recommender import HybridRecommender


class EnsembleRecommender:
    """Multi-model ensemble voting wrapper with confidence interval calculations."""

    def __init__(self, hybrid_recommender: Optional[HybridRecommender] = None):
        self.hybrid = hybrid_recommender or HybridRecommender()

    def predict_with_confidence(self, user_profile: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Executes ensemble voting across models, returning confidence intervals
        and model agreement metrics.
        """
        # Get raw recommendations from hybrid recommender
        recs = self.hybrid.recommend(user_profile, top_k=len(CAREER_LABELS))

        results = []
        for r in recs:
            career = r["career"]
            comp = r.get("component_scores", {})
            s_xgb = comp.get("xgboost", 0.0)
            s_collab = comp.get("collaborative", 0.0)
            s_content = comp.get("content", 0.0)

            scores_arr = np.array([s_xgb, s_collab, s_content], dtype=np.float32)
            mean_score = float(np.mean(scores_arr))
            std_err = float(np.std(scores_arr) / np.sqrt(len(scores_arr)))

            # 95% confidence interval (approx 1.96 * SE)
            margin = 1.96 * std_err
            ci_lower = max(0.0, round(mean_score - margin, 4))
            ci_upper = min(1.0, round(mean_score + margin, 4))

            # Agreement metric: inverse of standard deviation
            agreement = max(0.0, 1.0 - float(np.std(scores_arr)))

            results.append({
                "career": career,
                "score": r["score"],
                "mean_score": round(mean_score, 4),
                "confidence": r["confidence"],
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "agreement": round(agreement, 3),
                "model_votes": {
                    "xgboost": s_xgb,
                    "collaborative": s_collab,
                    "content": s_content,
                },
                "skill_gaps": r.get("skill_gaps", {}),
                "reason": r.get("reason", ""),
                "explanation": r.get("explanation", ""),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
