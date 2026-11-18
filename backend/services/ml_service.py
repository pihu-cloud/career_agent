"""
SB2/US6, US8, US34 - Production ML Inference Service & Model Orchestrator
"""
import os
import json
from typing import Dict, Any, List
from backend.core.logging import logger
from backend.cache.redis_client import cache

# Import ML model classes
from ml.models.career_predictor import CareerPredictor
from ml.models.collaborative_filter import CollaborativeFilter
from ml.models.content_filter import ContentBasedFilter
from ml.models.hybrid_recommender import HybridRecommender
from ml.models.growth_trajectory import GrowthTrajectoryModel
from ml.models.demand_forecast import DemandForecastModel
from ml.nlp.skill_extractor import SkillExtractor
from ml.explainability.shap_explainer import RecommendationExplainer
from ml.fallback.rule_based import RuleBasedRecommender
from ml.features.pipeline import FeaturePipeline

class MLService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._models_dir = os.path.abspath("./ml/models/saved")
        self.hybrid_model = None
        self.skill_extractor = SkillExtractor()
        self.growth_model = GrowthTrajectoryModel()
        self.demand_model = DemandForecastModel()
        self.explainer = RecommendationExplainer()
        self.fallback = RuleBasedRecommender()
        self.load_models()
        self._initialized = True

    def load_models(self):
        try:
            logger.info("Loading pre-trained AI/ML models...")
            hybrid_path = os.path.join(self._models_dir, "hybrid_recommender.joblib")
            if os.path.exists(hybrid_path):
                self.hybrid_model = HybridRecommender.load(hybrid_path)
                logger.info("Hybrid Recommender model successfully loaded from disk.")
            else:
                logger.warning("Saved model not found. Initializing inline training...")
                from ml.training.train_career_model import train_and_save_all_models
                train_and_save_all_models()
                self.hybrid_model = HybridRecommender.load(hybrid_path)
        except Exception as e:
            logger.error(f"Error loading ML models: {e}. Falling back to Rule-Based Recommender.")
            self.hybrid_model = None

    def generate_recommendations(self, profile_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Check cache
        user_id = profile_dict.get("user_id", "guest")
        cache_key = f"rec_{user_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        results = []
        try:
            if self.hybrid_model:
                recs = self.hybrid_model.recommend(profile_dict, top_k=5)
                for r in recs:
                    career = r["career"]
                    expl = self.explainer.explain(profile_dict, career)
                    r["explanation"] = expl["summary"]
                    results.append(r)
            else:
                results = self.fallback.recommend(profile_dict, top_k=5)
        except Exception as e:
            logger.error(f"ML inference error: {e}. Utilizing fallback engine.")
            results = self.fallback.recommend(profile_dict, top_k=5)

        # Cache predictions for 15 minutes
        cache.set(cache_key, results, ttl=900)
        return results

    def extract_skills_from_file(self, file_path: str) -> Dict[str, Any]:
        return self.skill_extractor.extract_from_resume_file(file_path)

    def get_skill_gaps(self, user_skills: List[str], career_title: str) -> Dict[str, Any]:
        from ml.scoring.compatibility import compute_skill_gap_score
        target_skills = ContentBasedFilter.CAREER_PROFILES.get(career_title, {}).get("required_skills", [
            "Python", "Data Analysis", "Communication", "Problem Solving"
        ])
        return compute_skill_gap_score(user_skills, target_skills)

    def get_growth_trajectory(self, career_title: str, user_skills: List[str], cgpa: float) -> Dict[str, Any]:
        return self.growth_model.predict_trajectory(career_title, user_skills, cgpa)

    def get_market_insights(self) -> Dict[str, Any]:
        return self.demand_model.get_market_insights()

ml_service = MLService()
