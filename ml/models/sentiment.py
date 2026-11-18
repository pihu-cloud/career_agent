"""
Sentiment Analysis Engine (SB2/US17).
Analyzes student feedback, reviews, and mentor notes using transformer models
with a lightweight built-in lexicon fallback.
"""

import re
from typing import Any, Dict, Optional


class SentimentAnalyzer:
    """
    Sentiment Analyzer with Transformer, TextBlob, and Lexical Fallback.
    """

    POSITIVE_WORDS = {
        "good", "great", "excellent", "amazing", "wonderful", "helpful", "perfect",
        "love", "liked", "like", "awesome", "clear", "insightful", "valuable",
        "inspiring", "encouraging", "relevant", "structured", "thorough", "best",
        "satisfied", "happy", "beneficial", "positive", "strong", "effective"
    }

    NEGATIVE_WORDS = {
        "bad", "terrible", "horrible", "awful", "poor", "useless", "unhelpful",
        "hate", "disliked", "dislike", "confusing", "vague", "misleading",
        "irrelevant", "broken", "slow", "frustrating", "annoying", "waste",
        "worst", "unhappy", "difficult", "negative", "weak", "ineffective"
    }

    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment"):
        self.model_name = model_name
        self.pipeline = None
        self._init_model()

    def _init_model(self):
        """Attempt to load transformer pipeline or textblob only if local cache exists."""
        import os
        from pathlib import Path
        
        hf_home = os.environ.get("HF_HOME") or str(Path.home() / ".cache" / "huggingface" / "hub")
        model_cache_name = f"models--{self.model_name.replace('/', '--')}"
        has_local_cache = (Path(hf_home) / model_cache_name).exists()

        if has_local_cache:
            try:
                from transformers import pipeline
                self.pipeline = pipeline("sentiment-analysis", model=self.model_name, local_files_only=True)
            except Exception:
                self.pipeline = None
        else:
            self.pipeline = None

    def _lexical_analyze(self, text: str) -> Dict[str, Any]:
        """Built-in sentiment lexicon fallback."""
        tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        if not tokens:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.60}

        pos_count = sum(1 for t in tokens if t in self.POSITIVE_WORDS)
        neg_count = sum(1 for t in tokens if t in self.NEGATIVE_WORDS)

        total_sentiment_words = pos_count + neg_count
        if total_sentiment_words == 0:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.65}

        # Raw score from -1.0 to 1.0
        score = (pos_count - neg_count) / max(1, total_sentiment_words)

        if score > 0.15:
            sentiment = "positive"
            conf = min(0.95, 0.65 + (pos_count * 0.08))
        elif score < -0.15:
            sentiment = "negative"
            conf = min(0.95, 0.65 + (neg_count * 0.08))
        else:
            sentiment = "neutral"
            conf = 0.70

        return {
            "sentiment": sentiment,
            "score": round(float(score), 3),
            "confidence": round(float(conf), 3),
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of arbitrary text.
        Returns: {sentiment: str, score: float, confidence: float}
        """
        if not text or not text.strip():
            return {"sentiment": "neutral", "score": 0.0, "confidence": 0.50}

        # Check TextBlob if installed and initialized
        try:
            import textblob
            blob = textblob.TextBlob(text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                sent = "positive"
            elif polarity < -0.1:
                sent = "negative"
            else:
                sent = "neutral"
            return {
                "sentiment": sent,
                "score": round(float(polarity), 3),
                "confidence": round(min(0.95, 0.70 + abs(polarity) * 0.25), 3),
            }
        except (ImportError, Exception):
            pass

        # Try Hugging Face pipeline if loaded
        if self.pipeline is not None:
            try:
                res = self.pipeline(text[:512])[0]
                label = res.get("label", "").lower()
                conf = float(res.get("score", 0.8))
                score = conf if "pos" in label else (-conf if "neg" in label else 0.0)
                sent = "positive" if "pos" in label else ("negative" if "neg" in label else "neutral")
                return {
                    "sentiment": sent,
                    "score": round(score, 3),
                    "confidence": round(conf, 3),
                }
            except Exception:
                pass

        # Robust lexical fallback
        return self._lexical_analyze(text)

    def analyze_feedback(self, feedback_text: str) -> Dict[str, Any]:
        """
        Analyze student pathway feedback with actionable summary metrics.
        """
        base = self.analyze(feedback_text)
        sentiment = base["sentiment"]
        score = base["score"]

        if sentiment == "positive":
            satisfaction = "Satisfied"
            actionable_insight = "Student finds the career recommendations aligned and helpful."
        elif sentiment == "negative":
            satisfaction = "Unsatisfied"
            actionable_insight = "Student indicates divergence between their expectations and recommendations."
        else:
            satisfaction = "Neutral"
            actionable_insight = "Student had neutral feedback. Consider gathering more specific skill preferences."

        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": base["confidence"],
            "satisfaction_level": satisfaction,
            "actionable_insight": actionable_insight,
            "feedback_snippet": feedback_text[:200],
        }
