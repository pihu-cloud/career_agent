"""
Adaptive Personalization Engine (SB2/US25).
Adjusts career pathway scoring over time based on student interaction feedback,
implicit preference history, and explicit like/dislike ratings.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json


class PersonalizationEngine:
    """Dynamically personalizes career recommendations based on student feedback history."""

    def __init__(self, persistence_path: Optional[Union[str, Path]] = None):
        self.persistence_path = Path(persistence_path) if persistence_path else None
        # Maps user_id -> {career -> score_delta}
        self.user_feedback: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._load_state()

    def _load_state(self):
        if self.persistence_path and self.persistence_path.exists():
            try:
                data = json.loads(self.persistence_path.read_text(encoding="utf-8"))
                for uid, career_map in data.items():
                    for career, delta in career_map.items():
                        self.user_feedback[uid][career] = float(delta)
            except Exception:
                pass

    def _save_state(self):
        if self.persistence_path:
            try:
                self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
                data = {uid: dict(c_map) for uid, c_map in self.user_feedback.items()}
                self.persistence_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except Exception:
                pass

    def update_from_feedback(self, user_id: str, career: str, liked: bool) -> float:
        """
        Record explicit user rating for a career recommendation.
        Increments preference weight (+0.15 for like, -0.20 for dislike).
        """
        delta = 0.15 if liked else -0.20
        current = self.user_feedback[user_id][career]
        new_val = max(-0.5, min(0.5, current + delta))
        self.user_feedback[user_id][career] = round(new_val, 3)
        self._save_state()
        return new_val

    def compute_personalization_score(
        self,
        user_history: Union[List[Dict[str, Any]], str],
        career: str,
    ) -> float:
        """
        Calculate personalization weight / boost for a career (between 0.0 and 1.0).
        Baseline is 0.50 (neutral).
        
        user_history can be either a user_id string or a list of historical action dicts:
        [{'action': 'bookmark'|'click'|'like'|'dislike', 'career': '...'}]
        """
        score = 0.50

        # Case 1: user_history is user_id string
        if isinstance(user_history, str):
            user_id = user_history
            feedback_delta = self.user_feedback[user_id].get(career, 0.0)
            return float(np_clip := max(0.0, min(1.0, score + feedback_delta)))

        # Case 2: user_history is list of event dicts
        if isinstance(user_history, list):
            for event in user_history:
                ev_career = event.get("career") or event.get("target")
                if ev_career != career:
                    continue
                action = event.get("action", "").lower()
                if action in ("like", "upvote", "enroll", "bookmark"):
                    score += 0.10
                elif action in ("click", "view"):
                    score += 0.03
                elif action in ("dislike", "downvote", "dismiss"):
                    score -= 0.15

        return round(float(max(0.0, min(1.0, score))), 3)
