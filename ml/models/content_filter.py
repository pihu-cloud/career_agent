"""
Content-Based Filtering Model (SB2/US4).
Uses TF-IDF and cosine similarity to map student skills, interests, and traits
against formal industry career profiles with adaptive skill-gap analysis.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ContentBasedFilter:
    """Recommends career paths by comparing student attributes to rich career domain profiles."""

    CAREER_PROFILES = {
        "Software Engineer": {
            "required_skills": ["python", "java", "c++", "javascript", "sql", "git", "docker", "rest api"],
            "preferred_interests": ["technology", "coding", "software", "development", "architecture"],
            "personality_fit": {"openness": 7.0, "conscientiousness": 8.0, "extraversion": 5.0},
            "description": "Designs, develops, tests, and maintains scalable software applications, backend services, and APIs.",
        },
        "Data Scientist": {
            "required_skills": ["python", "sql", "machine learning", "pandas", "numpy", "statistics", "data analysis"],
            "preferred_interests": ["science", "technology", "analytics", "statistics", "mathematics"],
            "personality_fit": {"openness": 9.0, "conscientiousness": 8.0, "extraversion": 4.0},
            "description": "Applies statistical modeling, machine learning, and predictive analytics to solve complex business problems.",
        },
        "Product Manager": {
            "required_skills": ["product strategy", "agile", "communication", "leadership", "user research", "roadmap"],
            "preferred_interests": ["business", "technology", "design", "management", "innovation"],
            "personality_fit": {"openness": 8.0, "conscientiousness": 9.0, "extraversion": 9.0},
            "description": "Guides the lifecycle of products by balancing user needs, technical feasibility, and business viability.",
        },
        "UX Designer": {
            "required_skills": ["figma", "wireframing", "prototyping", "user research", "design thinking", "ui design"],
            "preferred_interests": ["design", "technology", "psychology", "art", "creative"],
            "personality_fit": {"openness": 9.0, "conscientiousness": 7.0, "extraversion": 7.0},
            "description": "Creates intuitive, accessible, and delightful digital user experiences and interactive interfaces.",
        },
        "Business Analyst": {
            "required_skills": ["business analysis", "sql", "excel", "requirements gathering", "communication", "process mapping"],
            "preferred_interests": ["business", "analytics", "consulting", "operations", "finance"],
            "personality_fit": {"openness": 7.0, "conscientiousness": 9.0, "extraversion": 7.0},
            "description": "Bridges business stakeholders and technical teams by analyzing workflows, data, and system requirements.",
        },
        "Cybersecurity Analyst": {
            "required_skills": ["network security", "penetration testing", "siem", "wireshark", "linux", "cryptography"],
            "preferred_interests": ["technology", "security", "defense", "networking", "investigation"],
            "personality_fit": {"openness": 7.0, "conscientiousness": 9.0, "extraversion": 4.0},
            "description": "Protects organizational infrastructure, networks, and data assets from cyber threats and unauthorized access.",
        },
        "DevOps Engineer": {
            "required_skills": ["docker", "kubernetes", "ci/cd", "aws", "terraform", "linux", "jenkins", "git"],
            "preferred_interests": ["technology", "automation", "cloud", "infrastructure", "systems"],
            "personality_fit": {"openness": 7.0, "conscientiousness": 8.0, "extraversion": 5.0},
            "description": "Automates software delivery pipelines, manages cloud infrastructure, and ensures system reliability and scalability.",
        },
        "AI/ML Engineer": {
            "required_skills": ["python", "deep learning", "pytorch", "tensorflow", "nlp", "mlops", "docker"],
            "preferred_interests": ["technology", "science", "artificial intelligence", "research", "algorithms"],
            "personality_fit": {"openness": 9.0, "conscientiousness": 9.0, "extraversion": 4.0},
            "description": "Builds and deploys scalable artificial intelligence, deep learning, and transformer models to production.",
        },
        "Financial Analyst": {
            "required_skills": ["financial modeling", "excel", "accounting", "data analysis", "valuation", "python"],
            "preferred_interests": ["business", "finance", "markets", "investing", "economics"],
            "personality_fit": {"openness": 6.0, "conscientiousness": 9.0, "extraversion": 6.0},
            "description": "Evaluates financial performance, builds forecast models, and prepares investment theses for executive decision makers.",
        },
        "Healthcare Informatics": {
            "required_skills": ["healthcare informatics", "sql", "python", "ehr systems", "data analysis", "hipaa compliance"],
            "preferred_interests": ["healthcare", "science", "technology", "medicine", "biostatistics"],
            "personality_fit": {"openness": 8.0, "conscientiousness": 9.0, "extraversion": 6.0},
            "description": "Analyzes clinical and medical data to optimize healthcare workflows, patient outcomes, and regulatory compliance.",
        },
    }

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.career_names = list(self.CAREER_PROFILES.keys())
        self.career_matrix = None
        self.is_fitted = False
        self.fit()

    def fit(self) -> "ContentBasedFilter":
        """Build TF-IDF representations of all career profiles."""
        corpus = []
        for career in self.career_names:
            prof = self.CAREER_PROFILES[career]
            text = (
                " ".join(prof["required_skills"])
                + " "
                + " ".join(prof["preferred_interests"])
                + " "
                + prof["description"]
            )
            corpus.append(text)

        self.career_matrix = self.vectorizer.fit_transform(corpus)
        self.is_fitted = True
        return self

    def _format_user_text(self, user_profile: Dict[str, Any]) -> str:
        """Combine user skills, interests, and background into query text."""
        parts = []

        # Skills
        raw_skills = user_profile.get("skills", [])
        for s in raw_skills:
            if isinstance(s, dict):
                parts.append(str(s.get("skill_name", "")))
            else:
                parts.append(str(s))

        # Interests
        raw_interests = user_profile.get("interests", [])
        for item in raw_interests:
            if isinstance(item, dict):
                parts.append(str(item.get("interest_name") or item.get("category") or ""))
            else:
                parts.append(str(item))

        # Resume text if present
        if "resume_text" in user_profile:
            parts.append(str(user_profile["resume_text"]))

        # Field of study
        if "field_of_study" in user_profile:
            parts.append(str(user_profile["field_of_study"]))

        return " ".join(parts).lower()

    def compute_skill_gap(self, user_skills: List[Union[str, Dict[str, Any]]], career: str) -> Dict[str, Any]:
        """
        Compute missing vs acquired skills for a specific career target.
        Returns: {gap_score, missing_skills, present_skills, gap_percentage}
        """
        clean_user_skills = set()
        for s in user_skills:
            if isinstance(s, dict):
                clean_user_skills.add(str(s.get("skill_name", "")).strip().lower())
            else:
                clean_user_skills.add(str(s).strip().lower())

        career_data = self.CAREER_PROFILES.get(career, {
            "required_skills": [],
            "preferred_interests": [],
            "personality_fit": {},
            "description": "",
        })
        required = [s.lower() for s in career_data.get("required_skills", [])]

        if not required:
            return {
                "gap_score": 0.0,
                "missing_skills": [],
                "present_skills": list(clean_user_skills),
                "gap_percentage": 0.0,
            }

        present = []
        missing = []

        for req in required:
            # Substring or exact match
            matched = any(req in u or u in req for u in clean_user_skills)
            if matched:
                present.append(req)
            else:
                missing.append(req)

        gap_pct = round((len(missing) / len(required)) * 100.0, 1)
        # Gap score: higher means bigger gap (0.0 means perfect match, 1.0 means no skills)
        gap_score = round(len(missing) / len(required), 3)

        return {
            "gap_score": gap_score,
            "missing_skills": missing,
            "present_skills": present,
            "gap_percentage": gap_pct,
        }

    def recommend(self, user_profile: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Recommend top careers based on content similarity and skill-gap evaluation.
        Returns: [{career, score, reason, skill_gaps}]
        """
        if not self.is_fitted or self.career_matrix is None:
            self.fit()

        user_text = self._format_user_text(user_profile)
        user_skills = user_profile.get("skills", [])

        if not user_text.strip():
            # Fallback if profile is completely empty
            user_text = "technology software general engineering"

        user_vec = self.vectorizer.transform([user_text])
        sims = cosine_similarity(user_vec, self.career_matrix)[0]

        results = []
        for idx, career in enumerate(self.career_names):
            cos_score = float(sims[idx])
            gaps = self.compute_skill_gap(user_skills, career)
            skill_match_ratio = 1.0 - gaps["gap_score"]

            # Blended content score: 50% TF-IDF cosine, 50% explicit skill match
            combined_score = round(0.5 * cos_score + 0.5 * skill_match_ratio, 4)

            reason = (
                f"Matches {len(gaps['present_skills'])} of {len(gaps['present_skills']) + len(gaps['missing_skills'])} "
                f"core competencies with strong alignment to your stated technical profile."
            )

            results.append({
                "career": career,
                "score": combined_score,
                "reason": reason,
                "skill_gaps": gaps,
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def save(self, filepath: Union[str, Path]) -> None:
        """Save model checkpoint to disk."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "ContentBasedFilter":
        """Load model checkpoint from disk."""
        path = Path(filepath)
        if not path.exists():
            instance = cls()
            return instance
        return joblib.load(path)
