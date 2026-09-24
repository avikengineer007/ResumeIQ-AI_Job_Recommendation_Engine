"""Unit tests for ScoreCalibrator (Platt and Isotonic) and calibration metrics."""

from pathlib import Path

import numpy as np
import pytest

from src.recommendation.calibration import (
    ScoreCalibrator,
    brier_score,
    expected_calibration_error,
)


def test_platt_scaling_and_persistence(tmp_path: Path) -> None:
    # Synthetic validation data: higher scores correspond to positive labels
    scores = np.array([-2.5, -1.0, 0.2, 0.8, 1.5, 2.8, 3.5, 4.2])
    labels = np.array([0, 0, 0, 1, 1, 1, 1, 1])

    calibrator = ScoreCalibrator(method="platt")
    calibrator.fit(scores, labels)

    probs = calibrator.predict_proba(scores)
    assert len(probs) == len(scores)
    # Probabilities must be strictly bounded in [0, 1]
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
    # Monotonicity: higher raw scores should yield higher calibrated probability
    assert probs[-1] > probs[0]

    # Save and reload
    save_path = tmp_path / "platt_calibrator.json"
    calibrator.save(save_path)

    loaded = ScoreCalibrator.load(save_path)
    loaded_probs = loaded.predict_proba(scores)
    assert np.allclose(probs, loaded_probs)


def test_isotonic_scaling_and_persistence(tmp_path: Path) -> None:
    scores = np.array([0.1, 0.2, 0.4, 0.6, 0.7, 0.9])
    labels = np.array([0, 0, 0, 1, 1, 1])

    calibrator = ScoreCalibrator(method="isotonic")
    calibrator.fit(scores, labels)

    probs = calibrator.predict_proba(scores)
    assert len(probs) == len(scores)
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
    assert probs[-1] >= probs[0]

    # Save and reload
    save_path = tmp_path / "isotonic_calibrator.json"
    calibrator.save(save_path)

    loaded = ScoreCalibrator.load(save_path)
    loaded_probs = loaded.predict_proba(scores)
    assert np.allclose(probs, loaded_probs)


def test_calibration_metrics() -> None:
    y_true = [0, 0, 1, 1]
    # Perfect predictions
    perf_probs = [0.0, 0.0, 1.0, 1.0]
    assert brier_score(y_true, perf_probs) == pytest.approx(0.0)
    assert expected_calibration_error(y_true, perf_probs) == pytest.approx(0.0)

    # Imperfect predictions
    imperfect = [0.2, 0.4, 0.7, 0.8]
    bs = brier_score(y_true, imperfect)
    ece = expected_calibration_error(y_true, imperfect)
    assert bs > 0.0
    assert ece > 0.0


def test_unfitted_calibrator_error() -> None:
    calibrator = ScoreCalibrator(method="platt")
    with pytest.raises(RuntimeError, match="must be fit"):
        calibrator.predict_proba([0.5])
    with pytest.raises(RuntimeError, match="Cannot save"):
        calibrator.save("test.json")
