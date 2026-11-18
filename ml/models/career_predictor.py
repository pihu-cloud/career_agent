"""
Career Predictor Model (SB2/US1).
Uses XGBoost Classifier to predict optimal career pathways based on user profile features.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

from ml.data.sample_data import CAREER_LABELS
from ml.features.pipeline import FeaturePipeline


class CareerPredictor:
    """XGBoost-based Career Path Classifier."""

    def __init__(self, **kwargs):
        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "objective": "multi:softprob",
            "eval_metric": "mlogloss",
            "random_state": 42,
            "n_jobs": -1,
        }
        params.update(kwargs)
        self.model = XGBClassifier(**params)
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(CAREER_LABELS)
        self.feature_names = FeaturePipeline.FEATURE_NAMES
        self.is_trained = False

    def train(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series, List[str]],
    ) -> Dict[str, float]:
        """
        Train XGBoost classifier and return training metrics.
        """
        if isinstance(X, pd.DataFrame):
            X_mat = X[self.feature_names].values
        else:
            X_mat = np.asarray(X)

        if isinstance(y, (pd.Series, list)):
            y_arr = np.asarray(y)
        else:
            y_arr = y

        # Encode labels if string
        if isinstance(y_arr[0], str):
            # Ensure all classes are represented in encoder
            unique_y = list(set(list(y_arr) + CAREER_LABELS))
            self.label_encoder.fit(unique_y)
            y_encoded = self.label_encoder.transform(y_arr)
        else:
            y_encoded = y_arr

        self.model.fit(X_mat, y_encoded)
        self.is_trained = True

        preds = self.model.predict(X_mat)
        metrics = {
            "accuracy": float(accuracy_score(y_encoded, preds)),
            "f1_weighted": float(f1_score(y_encoded, preds, average="weighted", zero_division=0)),
            "precision_weighted": float(precision_score(y_encoded, preds, average="weighted", zero_division=0)),
            "recall_weighted": float(recall_score(y_encoded, preds, average="weighted", zero_division=0)),
        }
        return metrics

    def predict(self, X: Union[np.ndarray, pd.DataFrame]) -> List[str]:
        """Predict top career label for each sample."""
        if not self.is_trained:
            # Fallback if not trained yet
            return [CAREER_LABELS[0]] * (len(X) if hasattr(X, "__len__") else 1)

        if isinstance(X, pd.DataFrame):
            X_mat = X[self.feature_names].values
        else:
            X_mat = np.asarray(X)
            if X_mat.ndim == 1:
                X_mat = X_mat.reshape(1, -1)

        preds_encoded = self.model.predict(X_mat)
        return list(self.label_encoder.inverse_transform(preds_encoded))

    def predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> List[Dict[str, float]]:
        """
        Predict probability distribution across all career labels.
        Returns list of dicts mapping career name to probability.
        """
        if isinstance(X, pd.DataFrame):
            X_mat = X[self.feature_names].values
        else:
            X_mat = np.asarray(X)
            if X_mat.ndim == 1:
                X_mat = X_mat.reshape(1, -1)

        if not self.is_trained:
            # Uniform fallback
            uniform_prob = 1.0 / len(CAREER_LABELS)
            return [{c: uniform_prob for c in CAREER_LABELS} for _ in range(len(X_mat))]

        probs = self.model.predict_proba(X_mat)
        classes = self.label_encoder.classes_

        results = []
        for prob_row in probs:
            row_dict = {str(cls_name): round(float(p), 4) for cls_name, p in zip(classes, prob_row)}
            # Ensure all career labels are present
            for c in CAREER_LABELS:
                if c not in row_dict:
                    row_dict[c] = 0.0
            results.append(row_dict)
        return results

    def evaluate(
        self,
        X_test: Union[np.ndarray, pd.DataFrame],
        y_test: Union[np.ndarray, pd.Series, List[str]],
    ) -> Dict[str, float]:
        """Evaluate model performance on test set."""
        if isinstance(X_test, pd.DataFrame):
            X_mat = X_test[self.feature_names].values
        else:
            X_mat = np.asarray(X_test)

        if isinstance(y_test, (pd.Series, list)):
            y_arr = np.asarray(y_test)
        else:
            y_arr = y_test

        if isinstance(y_arr[0], str):
            y_encoded = self.label_encoder.transform(y_arr)
        else:
            y_encoded = y_arr

        preds = self.model.predict(X_mat)
        return {
            "accuracy": float(accuracy_score(y_encoded, preds)),
            "f1_weighted": float(f1_score(y_encoded, preds, average="weighted", zero_division=0)),
            "precision_weighted": float(precision_score(y_encoded, preds, average="weighted", zero_division=0)),
            "recall_weighted": float(recall_score(y_encoded, preds, average="weighted", zero_division=0)),
        }

    def get_feature_importance(self) -> Dict[str, float]:
        """Return dict of feature importances."""
        if not self.is_trained or not hasattr(self.model, "feature_importances_"):
            return {f: 1.0 / len(self.feature_names) for f in self.feature_names}

        importances = self.model.feature_importances_
        return {
            feat: round(float(imp), 4)
            for feat, imp in zip(self.feature_names, importances)
        }

    def save(self, filepath: Union[str, Path]) -> None:
        """Save model checkpoint."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "CareerPredictor":
        """Load model checkpoint."""
        path = Path(filepath)
        if not path.exists():
            return cls()
        return joblib.load(path)
