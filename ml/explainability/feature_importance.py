"""
Feature Importance Explainer (SB2/US40).
Computes global and local feature contributions driving career recommendations.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np


def get_feature_importance(model: Any, feature_names: List[str]) -> Dict[str, float]:
    """
    Extract normalized global feature importance scores from a model.
    """
    if hasattr(model, "feature_importances_"):
        raw_imp = model.feature_importances_
    elif hasattr(model, "model") and hasattr(model.model, "feature_importances_"):
        raw_imp = model.model.feature_importances_
    elif hasattr(model, "coef_"):
        raw_imp = np.abs(model.coef_).mean(axis=0)
    else:
        # Equal importance default
        return {f: round(1.0 / len(feature_names), 4) for f in feature_names}

    total = float(np.sum(raw_imp)) or 1.0
    return {
        feat: round(float(imp / total), 4)
        for feat, imp in zip(feature_names, raw_imp)
    }


def explain_prediction(
    model: Any,
    X: Union[np.ndarray, List[float]],
    feature_names: List[str],
) -> Dict[str, Any]:
    """
    Compute sample-level explanation highlighting the top 5 factors driving the prediction.
    Returns:
    {
        "top_factors": [{"feature": str, "value": float, "importance": float, "impact": str}],
        "summary": str
    }
    """
    vec = np.asarray(X).flatten()
    global_importances = get_feature_importance(model, feature_names)

    # Local contribution = normalized feature value * global importance weight
    contributions = []
    for idx, name in enumerate(feature_names):
        val = float(vec[idx]) if idx < len(vec) else 0.0
        imp = global_importances.get(name, 0.0)
        local_score = val * imp
        impact = "positive" if val > 0 else "neutral"

        contributions.append({
            "feature": name,
            "value": round(val, 2),
            "importance": imp,
            "local_contribution": round(local_score, 4),
            "impact": impact,
        })

    # Sort descending by local contribution
    contributions.sort(key=lambda item: item["local_contribution"], reverse=True)
    top_5 = contributions[:5]

    top_names = [f["feature"].replace("_", " ") for f in top_5 if f["value"] > 0]
    if top_names:
        summary = f"Top drivers for this pathway include strong alignment in {', '.join(top_names[:3])}."
    else:
        summary = "Recommendation based on balanced evaluation across all academic and skill criteria."

    return {
        "top_factors": top_5,
        "all_contributions": contributions,
        "summary": summary,
    }
