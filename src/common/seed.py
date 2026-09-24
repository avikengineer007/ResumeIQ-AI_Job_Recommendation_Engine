"""Deterministic random seed utility for full reproducibility.

Ensures that all stochastic operations across standard Python, NumPy,
and PyTorch use identical random states.
"""

import os
import random
from collections.abc import Generator
from contextlib import contextmanager

import numpy as np

try:
    import torch

    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


def set_seed(seed: int = 42) -> int:
    """Set random seed across all libraries to guarantee deterministic behavior.

    Args:
        seed: The integer seed value.

    Returns:
        The seed value that was set.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

    if HAS_TORCH:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

    return seed


@contextmanager
def temporary_seed(seed: int) -> Generator[None, None, None]:
    """Temporarily enter a scoped deterministic seed block and restore previous state."""
    py_state = random.getstate()
    np_state = np.random.get_state()
    torch_state = torch.get_rng_state() if HAS_TORCH else None
    torch_cuda_state = (
        torch.cuda.get_rng_state_all()
        if (HAS_TORCH and torch.cuda.is_available())
        else None
    )

    try:
        set_seed(seed)
        yield
    finally:
        random.setstate(py_state)
        np.random.set_state(np_state)
        if HAS_TORCH and torch_state is not None:
            torch.set_rng_state(torch_state)
        if HAS_TORCH and torch_cuda_state is not None and torch.cuda.is_available():
            torch.cuda.set_rng_state_all(torch_cuda_state)
