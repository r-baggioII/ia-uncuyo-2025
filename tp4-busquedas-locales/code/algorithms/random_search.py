from __future__ import annotations
import time, math
from typing import Dict, Any, List
from .utils import H, random_board, rng_from_seed, result_dict

def solve(n: int, max_evals: int, seed: int | None = None, env_n: int = 0, record_history: bool = False) -> Dict[str, Any]:
    rng = rng_from_seed(seed)
    start = time.perf_counter()

    best_board = None
    best_h = math.inf
    history: List[int] = []

    for states in range(1, max_evals + 1):
        b = random_board(n, rng)
        h = H(b)
        if record_history:
            history.append(h)
        if h < best_h:
            best_h = h
            best_board = b
        if h == 0:
            break

    elapsed = time.perf_counter() - start
    if best_board is None:
        best_board = random_board(n, rng)
        best_h = H(best_board)
    return result_dict("random", n, env_n, best_board, best_h, states, elapsed, history if record_history else None)
