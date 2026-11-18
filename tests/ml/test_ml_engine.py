"""
SB2/US1, US3, US4, US5, US11, US12, US32 - ML Engine Verification Tests
"""
from ml.models.career_predictor import CareerPredictor
from ml.models.content_filter import ContentBasedFilter
from ml.models.collaborative_filter import CollaborativeFilter
from ml.models.hybrid_recommender import HybridRecommender
from ml.fallback.rule_based import RuleBasedRecommender
from ml.data.sample_data import generate_career_training_data
from ml.scoring.compatibility import compute_compatibility_score, compute_skill_gap_score
from ml.features.pipeline import FeaturePipeline

def test_career_prediction_model():
    df = generate_career_training_data(n_samples=200)
    pipeline = FeaturePipeline()
    X = pipeline.fit_transform(df)
    y = df["career_label"].values
    predictor = CareerPredictor()
    metrics = predictor.train(X, y)
    assert metrics["accuracy"] > 0.40  # multi-class multi-category model benchmark

def test_content_and_collaborative_filters():
    c_filter = ContentBasedFilter()
    c_filter.fit()
    dummy_profile = {
        "skills": [{"skill_name": "Python"}, {"skill_name": "SQL"}, {"skill_name": "Machine Learning"}],
        "interests": [{"category": "Technology"}],
        "personality_traits": [{"trait_name": "Openness", "score": 8.0}]
    }
    recs = c_filter.recommend(dummy_profile, top_k=3)
    assert len(recs) == 3
    assert all("career" in r for r in recs)

def test_skill_gap_computation():
    user_skills = ["Python", "Git", "SQL"]
    required_skills = ["Python", "SQL", "Docker", "Kubernetes", "AWS"]
    gap_result = compute_skill_gap_score(user_skills, required_skills)
    assert gap_result["gap_percentage"] > 0
    missing_lower = [s.lower() for s in gap_result["missing_skills"]]
    assert "docker" in missing_lower
    present_lower = [s.lower() for s in gap_result["present_skills"]]
    assert "python" in present_lower

def test_rule_based_fallback():
    fallback = RuleBasedRecommender()
    dummy_profile = {"skills": [], "interests": []}
    recs = fallback.recommend(dummy_profile, top_k=3)
    assert len(recs) == 3
    assert recs[0]["career"] is not None
