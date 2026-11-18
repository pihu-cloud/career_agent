"""
Confidence Scoring (SB2/US45).
Evaluates prediction stability, model consensus, and recommendation reliability.
"""

from typing import Any, Dict, List, Union
import numpy as np


def compute_recommendation_confidence(scores: Dict[str, Union[float, int]]) -> Dict[str, Any]:
    """
    Computes overall confidence, cross-model consensus agreement, and reliability level.
    
    Args:
        scores: Dict mapping model names to predicted probabilities / scores.
                Example: {"xgboost": 0.85, "collaborative": 0.78, "content": 0.82}
    
    Returns:
        {
            "overall_confidence": float (0.0 - 1.0),
            "model_agreement": float (0.0 - 1.0),
            "reliability": str ("High" | "Moderate" | "Low"),
            "variance": float,
            "mean_score": float
        }
    """
    if not scores:
        return {
            "overall_confidence": 0.50,
            "model_agreement": 0.50,
            "reliability": "Moderate",
            "variance": 0.0,
            "mean_score": 0.50,
        }

    values = [float(v) for v in scores.values() if v is not None]
    if not values:
        return {
            "overall_confidence": 0.50,
            "model_agreement": 0.50,
            "reliability": "Moderate",
            "variance": 0.0,
            "mean_score": 0.50,
        }

    mean_val = float(np.mean(values))
    std_val = float(np.std(values))
    var_val = float(np.var(values))

    # Agreement is higher when model spread (standard deviation) is lower
    model_agreement = max(0.0, min(1.0, 1.0 - (std_val * 2.0)))

    # Overall confidence is a function of mean prediction strength and agreement
    overall_conf = max(0.0, min(1.0, (mean_val * 0.6) + (model_agreement * 0.4)))

    if overall_conf >= 0.75 and model_agreement >= 0.70:
        reliability = "High"
    elif overall_conf >= 0.50:
        reliability = "Moderate"
    else:
        reliability = "Low"

    return {
        "overall_confidence": round(overall_conf, 3),
        "model_agreement": round(model_agreement, 3),
        "reliability": reliability,
        "variance": round(var_val, 4),
        "mean_score": round(mean_val, 3),
    }
