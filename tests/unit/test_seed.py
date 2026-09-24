"""Unit tests for deterministic seed utilities."""

import random
import numpy as np
from src.common.seed import set_seed, temporary_seed

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


def test_seed_python_random():
    """Verify python random generator is reproducible with set_seed."""
    set_seed(123)
    val1 = [random.random() for _ in range(5)]

    set_seed(123)
    val2 = [random.random() for _ in range(5)]

    assert val1 == val2


def test_seed_numpy_random():
    """Verify numpy random generator is reproducible with set_seed."""
    set_seed(456)
    arr1 = np.random.randn(5)

    set_seed(456)
    arr2 = np.random.randn(5)

    np.testing.assert_allclose(arr1, arr2)


def test_seed_torch_deterministic():
    """Verify PyTorch RNG reproducibility if installed."""
    if not HAS_TORCH:
        return

    set_seed(789)
    t1 = torch.randn(3, 3)

    set_seed(789)
    t2 = torch.randn(3, 3)

    assert torch.equal(t1, t2)


def test_temporary_seed_context():
    """Verify temporary_seed restores the previous RNG state on exit."""
    set_seed(42)
    _ = random.random()
    state_before = random.getstate()

    with temporary_seed(9999):
        _ = random.random()
        _ = np.random.randn(3)

    state_after = random.getstate()
    assert state_before == state_after
