"""
Training Orchestrator for Career Models (SB2/US1, US7, US11).
Generates training data, fits feature pipelines, trains XGBoost classifier,
collaborative filtering, content-based recommender, and builds the hybrid ensemble.
Saves all artifacts to ml/models/saved/.
"""

import os
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Union
import numpy as np
from sklearn.model_selection import train_test_split

# Ensure project root is in path
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.data.sample_data import generate_career_training_data, save_sample_data
from ml.features.pipeline import FeaturePipeline
from ml.models.career_predictor import CareerPredictor
from ml.models.collaborative_filter import CollaborativeFilter
from ml.models.content_filter import ContentBasedFilter
from ml.models.hybrid_recommender import HybridRecommender


def train_and_save_all_models(
    n_samples: int = 1500,
    save_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """
    Train and persist all ML pipeline models.
    """
    if save_dir is None:
        save_path = PROJECT_ROOT / "ml" / "models" / "saved"
    else:
        save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    print("==================================================")
    print("🚀 STARTING CAREER ML TRAINING PIPELINE (SPRINT 2)")
    print("==================================================")

    # 1. Generate/Load Training Data (SAMPLE DATA per Issue #1)
    print(f"[1/8] Generating {n_samples} synthetic training samples...")
    data_csv_path = PROJECT_ROOT / "ml" / "data" / "career_training_data.csv"
    df = generate_career_training_data(n_samples=n_samples, random_state=42)
    df.to_csv(data_csv_path, index=False)
    print(f"      Saved sample training dataset to {data_csv_path}")

    # 2. Feature Engineering Pipeline
    print("[2/8] Fitting Feature Engineering Pipeline...")
    feature_pipeline = FeaturePipeline(scale_features=True)
    X_raw = df[FeaturePipeline.FEATURE_NAMES].to_numpy(dtype=np.float32)
    y_raw = df["career_label"].to_numpy()

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y_raw, test_size=0.20, random_state=42, stratify=y_raw
    )

    X_train_scaled = feature_pipeline.fit_transform(X_train_raw)
    X_test_scaled = feature_pipeline.transform(X_test_raw)

    # 3. Train XGBoost Career Predictor
    print("[3/8] Training XGBoost Career Predictor...")
    predictor = CareerPredictor(n_estimators=120, max_depth=5, learning_rate=0.08)
    train_metrics = predictor.train(X_train_scaled, y_train)
    print(f"      Train Accuracy: {train_metrics['accuracy']:.4f}, F1: {train_metrics['f1_weighted']:.4f}")

    # 4. Train Collaborative Filter
    print("[4/8] Training Collaborative Filtering User Base...")
    # Convert subset of training data to user profiles
    peer_profiles = []
    for idx, row in df.head(300).iterrows():
        peer_profiles.append({
            "user_id": f"student_{idx+1:04d}",
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
        })
    collab_filter = CollaborativeFilter(pipeline=feature_pipeline)
    collab_filter.fit(peer_profiles)
    print(f"      Collaborative filter indexed {len(peer_profiles)} peer trajectories.")

    # 5. Train Content-Based Filter
    print("[5/8] Vectorizing Content-Based Career Knowledge Profiles...")
    content_filter = ContentBasedFilter()
    content_filter.fit()
    print(f"      Content filter indexed {len(content_filter.career_names)} career domain profiles.")

    # 6. Build Hybrid Recommender
    print("[6/8] Assembling Hybrid Recommender Ensemble...")
    hybrid_recommender = HybridRecommender(
        predictor=predictor,
        collaborative=collab_filter,
        content_filter=content_filter,
        feature_pipeline=feature_pipeline,
        weights={"xgboost": 0.50, "collaborative": 0.25, "content": 0.25},
    )

    # 7. Evaluate All Models
    print("[7/8] Evaluating Models on Held-Out Test Set...")
    eval_metrics = predictor.evaluate(X_test_scaled, y_test)
    print("      ----------------------------------------")
    print(f"      Test Accuracy : {eval_metrics['accuracy'] * 100:.2f}%")
    print(f"      Test F1 Score : {eval_metrics['f1_weighted']:.4f}")
    print(f"      Precision     : {eval_metrics['precision_weighted']:.4f}")
    print(f"      Recall        : {eval_metrics['recall_weighted']:.4f}")
    print("      ----------------------------------------")

    # 8. Save All Models
    print(f"[8/8] Persisting trained artifacts to {save_path}...")
    pipeline_file = save_path / "feature_pipeline.joblib"
    predictor_file = save_path / "career_predictor.joblib"
    collab_file = save_path / "collaborative_filter.joblib"
    content_file = save_path / "content_filter.joblib"
    hybrid_file = save_path / "hybrid_recommender.joblib"

    feature_pipeline.save(pipeline_file)
    predictor.save(predictor_file)
    collab_filter.save(collab_file)
    content_filter.save(content_file)
    hybrid_recommender.save(hybrid_file)

    print("✅ All models trained and saved successfully!")
    print(f"   - {pipeline_file.name}")
    print(f"   - {predictor_file.name}")
    print(f"   - {collab_file.name}")
    print(f"   - {content_file.name}")
    print(f"   - {hybrid_file.name}")

    return {
        "status": "success",
        "eval_metrics": eval_metrics,
        "train_metrics": train_metrics,
        "saved_paths": {
            "pipeline": str(pipeline_file),
            "predictor": str(predictor_file),
            "collab": str(collab_file),
            "content": str(content_file),
            "hybrid": str(hybrid_file),
        },
    }


if __name__ == "__main__":
    train_and_save_all_models()
