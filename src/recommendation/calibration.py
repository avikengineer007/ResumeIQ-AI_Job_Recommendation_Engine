"""Score probability calibration module for recommendation scores.

PROTOCOL RULES & LEAKAGE PREVENTION:
1. Calibration models (Platt scaling and Isotonic regression) must be fit
   EXCLUSIVELY on the validation split.
2. Never fit calibrators on the test split.
3. Once fit on validation data, serialize the calibrator parameters to safe JSON
   and load it for test-set inference or serving.
"""

import json
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

    Uses safe JSON serialization for fitted parameters (coefficients for Platt, thresholds for Isotonic)
    to eliminate any untrusted pickle deserialization risks.
    NOTE: Must be fit strictly on validation split data.
    """

    def __init__(self, method: str = "platt") -> None:
        if method not in ("platt", "isotonic"):
            raise ValueError(f"Method must be 'platt' or 'isotonic', got {method}")
        self.method = method
        self.is_fit = False

        # Platt parameters
        self.platt_a: float = 1.0
        self.platt_b: float = 0.0

        # Isotonic parameters
        self.iso_x: list[float] = []
        self.iso_y: list[float] = []

    def fit(
        self,
        raw_scores: Sequence[float] | np.ndarray,
        labels: Sequence[int] | np.ndarray,
    ) -> "ScoreCalibrator":
        """Fit calibration model on validation scores and binary relevance labels."""
        x = np.asarray(raw_scores, dtype=np.float64).reshape(-1, 1)
        y = np.asarray(labels, dtype=np.int32)

        if self.method == "platt":
            lr = LogisticRegression(solver="lbfgs")
            lr.fit(x, y)
            self.platt_a = float(lr.coef_[0][0])
            self.platt_b = float(lr.intercept_[0])
        else:
            iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            iso.fit(x.ravel(), y)
            self.iso_x = [float(v) for v in iso.X_thresholds_]
            self.iso_y = [float(v) for v in iso.y_thresholds_]

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
            logits = self.platt_a * x + self.platt_b
            # Numerically stable sigmoid
            probs = np.where(
                logits >= 0,
                1.0 / (1.0 + np.exp(-logits)),
                np.exp(logits) / (1.0 + np.exp(logits)),
            )
        else:
            probs = np.interp(
                x,
                self.iso_x,
                self.iso_y,
                left=self.iso_y[0] if self.iso_y else 0.0,
                right=self.iso_y[-1] if self.iso_y else 1.0,
            )

        return np.clip(probs, 0.0, 1.0).astype(np.float64)

    def save(self, output_path: str | Path) -> None:
        """Persist calibrator state to plain, safe JSON file."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        if not self.is_fit:
            raise RuntimeError("Cannot save unfitted ScoreCalibrator.")

        state = {
            "method": self.method,
            "is_fit": self.is_fit,
            "platt_a": self.platt_a,
            "platt_b": self.platt_b,
            "iso_x": self.iso_x,
            "iso_y": self.iso_y,
        }

        with open(p, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    @classmethod
    def load(cls, input_path: str | Path) -> "ScoreCalibrator":
        """Load calibrator state from plain JSON file."""
        with open(input_path, encoding="utf-8") as f:
            state = json.load(f)

        calibrator = cls(method=state["method"])
        calibrator.is_fit = state["is_fit"]
        calibrator.platt_a = state.get("platt_a", 1.0)
        calibrator.platt_b = state.get("platt_b", 0.0)
        calibrator.iso_x = state.get("iso_x", [])
        calibrator.iso_y = state.get("iso_y", [])

        return calibrator
