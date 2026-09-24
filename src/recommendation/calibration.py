"""Score probability calibration module for recommendation scores.

PROTOCOL RULES & LEAKAGE PREVENTION:
1. Calibration models (Platt scaling and Isotonic regression) must be fit
   EXCLUSIVELY on the validation split.
2. Never fit calibrators on the test split.
3. Once fit on validation data, serialize the calibrator and load it for inference.
"""

import pickle
from collections.abc import Sequence
from pathlib import Path

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


def brier_score(
    y_true: Sequence[int] | np.ndarray, y_prob: Sequence[float] | np.ndarray
) -> float:
    """Compute Brier score: mean squared difference between predicted probability and actual outcome."""
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_prob, dtype=np.float64)
    return float(np.mean((yp - yt) ** 2))


def expected_calibration_error(
    y_true: Sequence[int] | np.ndarray,
    y_prob: Sequence[float] | np.ndarray,
    n_bins: int = 10,
) -> float:
    """Compute Expected Calibration Error (ECE) across binned confidence intervals."""
    yt = np.asarray(y_true, dtype=np.float64)
    yp = np.asarray(y_prob, dtype=np.float64)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_indices = np.digitize(yp, bins) - 1

    ece = 0.0
    total_samples = len(yt)

    for i in range(n_bins):
        bin_mask = bin_indices == i
        bin_count = np.sum(bin_mask)
        if bin_count > 0:
            avg_prob = np.mean(yp[bin_mask])
            avg_true = np.mean(yt[bin_mask])
            ece += (bin_count / total_samples) * abs(avg_prob - avg_true)

    return float(ece)


class ScoreCalibrator:
    """Calibrates raw ranking scores into true empirical probabilities using Platt or Isotonic scaling.

    NOTE: Must be fit strictly on validation split data and serialized before test-set evaluation.
    """

    def __init__(self, method: str = "platt") -> None:
        if method not in ("platt", "isotonic"):
            raise ValueError(f"Method must be 'platt' or 'isotonic', got {method}")
        self.method = method
        self.is_fit = False

        if self.method == "platt":
            self.model: LogisticRegression | IsotonicRegression = LogisticRegression(
                solver="lbfgs"
            )
        else:
            self.model = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)

    def fit(
        self,
        raw_scores: Sequence[float] | np.ndarray,
        labels: Sequence[int] | np.ndarray,
    ) -> "ScoreCalibrator":
        """Fit calibration model on validation scores and binary relevance labels.

        Args:
            raw_scores: Raw model scores from cross-encoder or hybrid search
            labels: Binary relevance indicators (1 for relevant/applied, 0 otherwise)
        """
        x = np.asarray(raw_scores, dtype=np.float64).reshape(-1, 1)
        y = np.asarray(labels, dtype=np.int32)

        if self.method == "platt":
            self.model.fit(x, y)
        else:
            self.model.fit(x.ravel(), y)

        self.is_fit = True
        return self

    def predict_proba(self, raw_scores: Sequence[float] | np.ndarray) -> np.ndarray:
        """Transform raw scores into calibrated probabilities in [0.0, 1.0]."""
        if not self.is_fit:
            raise RuntimeError(
                "ScoreCalibrator must be fit on validation data before predicting."
            )

        x = np.asarray(raw_scores, dtype=np.float64)
        if self.method == "platt":
            x_2d = x.reshape(-1, 1)
            probs = self.model.predict_proba(x_2d)[:, 1]
        else:
            probs = self.model.predict(x.ravel())

        return np.clip(probs, 0.0, 1.0).astype(np.float64)

    def save(self, output_path: str | Path) -> None:
        """Persist calibrator state to file using pickle."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        if not self.is_fit:
            raise RuntimeError("Cannot save unfitted ScoreCalibrator.")

        state = {
            "method": self.method,
            "is_fit": self.is_fit,
            "model": self.model,
        }

        with open(p, "wb") as f:
            pickle.dump(state, f)

    @classmethod
    def load(cls, input_path: str | Path) -> "ScoreCalibrator":
        """Load calibrator state from file."""
        with open(input_path, "rb") as f:
            state = pickle.load(f)

        calibrator = cls(method=state["method"])
        calibrator.is_fit = state["is_fit"]
        calibrator.model = state["model"]

        return calibrator
