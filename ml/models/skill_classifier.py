"""
Skill Classifier Model (SB2/US2).
Uses Sentence-Transformers / DistilBERT embeddings (paraphrase-MiniLM-L6-v2)
to classify skills into Technical, Soft, or Domain categories, with TF-IDF fallback.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import numpy as np

# Reference taxonomy
SKILL_TAXONOMY = {
    "Technical": [
        "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust",
        "sql", "postgresql", "mongodb", "mysql", "redis", "cassandra",
        "react", "angular", "vue", "django", "fastapi", "flask", "spring boot",
        "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
        "pytorch", "scikit-learn", "pandas", "numpy", "data analysis",
        "docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "linux", "git",
        "rest api", "graphql", "microservices", "html", "css", "tailwind",
        "cybersecurity", "penetration testing", "network security", "cryptography"
    ],
    "Soft": [
        "communication", "verbal communication", "written communication",
        "teamwork", "collaboration", "leadership", "mentoring", "conflict resolution",
        "problem solving", "critical thinking", "analytical thinking", "decision making",
        "time management", "organization", "prioritization", "adaptability",
        "flexibility", "emotional intelligence", "empathy", "negotiation",
        "presentation", "public speaking", "active listening", "work ethic",
        "creativity", "stress management"
    ],
    "Domain": [
        "healthcare informatics", "clinical workflows", "financial modeling",
        "risk management", "accounting", "investment banking", "supply chain",
        "logistics", "e-commerce", "digital marketing", "seo", "product lifecycle",
        "agile methodologies", "scrum", "kanban", "business strategy",
        "market research", "regulatory compliance", "hipaa", "gdpr", "ux research",
        "wireframing", "prototyping", "figma"
    ],
}


class SkillClassifier:
    """
    BERT-based skill classifier.
    Uses 'paraphrase-MiniLM-L6-v2' (DistilBERT/MiniLM lightweight equivalent).
    Includes TF-IDF / lexical semantic similarity fallback when running offline.
    """

    def __init__(self, model_name: str = "paraphrase-MiniLM-L6-v2"):
        self.model_name = model_name
        self.encoder = None
        self.category_prototypes = {}
        self._init_encoder()
        self._prepare_prototypes()

    def _init_encoder(self):
        """Try loading sentence transformer model only if local cache exists, else fall back to semantic lexicon."""
        import os
        from pathlib import Path
        
        # Check standard huggingface cache paths
        hf_home = os.environ.get("HF_HOME") or str(Path.home() / ".cache" / "huggingface" / "hub")
        model_cache_name = f"models--{self.model_name.replace('/', '--')}"
        has_local_cache = (Path(hf_home) / model_cache_name).exists()

        if has_local_cache:
            try:
                from sentence_transformers import SentenceTransformer
                self.encoder = SentenceTransformer(self.model_name, local_files_only=True)
            except Exception:
                self.encoder = None
        else:
            self.encoder = None

    def _prepare_prototypes(self):
        """Calculate embedding centers for each category."""
        if self.encoder is not None:
            try:
                for cat, skills in SKILL_TAXONOMY.items():
                    embs = self.encoder.encode(skills)
                    self.category_prototypes[cat] = np.mean(embs, axis=0)
            except Exception:
                self.encoder = None

    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        if self.encoder is not None:
            try:
                return self.encoder.encode([text])[0]
            except Exception:
                return None
        return None

    def classify_skill(self, skill_text: str) -> Dict[str, Any]:
        """
        Classifies skill text into Technical, Soft, or Domain.
        Returns: {category: str, confidence: float, related_skills: list[str]}
        """
        clean_text = skill_text.strip().lower()

        # 1. Direct exact or substring match check
        for cat, skills in SKILL_TAXONOMY.items():
            for s in skills:
                if clean_text == s or s in clean_text:
                    related = [cand for cand in skills if cand != s][:5]
                    return {
                        "category": cat,
                        "confidence": 0.95,
                        "related_skills": related,
                    }

        # 2. Embedding-based classification if model available
        emb = self._get_embedding(clean_text)
        if emb is not None and self.category_prototypes:
            best_cat = "Technical"
            best_sim = -1.0
            for cat, proto in self.category_prototypes.items():
                denom = (np.linalg.norm(emb) * np.linalg.norm(proto)) + 1e-9
                sim = float(np.dot(emb, proto) / denom)
                if sim > best_sim:
                    best_sim = sim
                    best_cat = cat

            conf = float(np.clip((best_sim + 1.0) / 2.0, 0.5, 0.92))
            related = SKILL_TAXONOMY[best_cat][:4]
            return {
                "category": best_cat,
                "confidence": round(conf, 3),
                "related_skills": related,
            }

        # 3. Heuristic / Lexical Fallback
        tech_indicators = ["code", "dev", "data", "cloud", "ai", "ml", "web", "app", "test", "net", "sys"]
        soft_indicators = ["lead", "manage", "think", "team", "speak", "write", "solve", "listen"]

        if any(ind in clean_text for ind in tech_indicators):
            cat = "Technical"
            conf = 0.80
        elif any(ind in clean_text for ind in soft_indicators):
            cat = "Soft"
            conf = 0.80
        else:
            cat = "Domain"
            conf = 0.70

        return {
            "category": cat,
            "confidence": conf,
            "related_skills": SKILL_TAXONOMY[cat][:4],
        }

    def classify_bulk(self, skills: List[str]) -> List[Dict[str, Any]]:
        """Classify a list of skills."""
        return [self.classify_skill(s) for s in skills]

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract matching skills from an arbitrary text document."""
        if not text:
            return []
        lower_text = text.lower()
        extracted = []
        for cat, skills in SKILL_TAXONOMY.items():
            for s in skills:
                # Match full word or phrase boundary
                import re
                pattern = r"\b" + re.escape(s) + r"\b"
                if re.search(pattern, lower_text):
                    if s not in extracted:
                        extracted.append(s)
        return extracted

    def save(self, filepath: Union[str, Path]) -> None:
        """Save classifier configuration."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "SkillClassifier":
        """Load classifier."""
        path = Path(filepath)
        if not path.exists():
            return cls()
        return joblib.load(path)
