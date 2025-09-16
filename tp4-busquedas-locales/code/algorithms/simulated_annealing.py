from __future__ import annotations
import time, math
from typing import Dict, Any, List
from .utils import H, random_board, random_neighbor, rng_from_seed, result_dict

def solve(n: int, max_evals: int, seed: int | None = None, env_n: int = 0, record_history: bool = False,
          T0: float | None = None, alpha: float = 0.995, Tmin: float = 1e-3) -> Dict[str, Any]:
    rng = rng_from_seed(seed)
    start = time.perf_counter()

    board = random_board(n, rng)
    h = H(board)
    states = 1
    history: List[int] = [h] if record_history else []

    T = T0 if T0 is not None else max(1.0, 0.5 * n)  # simple schedule baseline
    while states < max_evals and h > 0 and T > Tmin:
        nb = random_neighbor(board, rng)
        nb_h = H(nb)
        delta = nb_h - h
        if delta < 0 or rng.random() < math.exp(-delta / T):
            board, h = nb, nb_h
            if record_history:
                history.append(h)
        T *= alpha
        states += 1

    elapsed = time.perf_counter() - start
    return result_dict("SA", n, env_n, board, h, states, elapsed, history if record_history else None)
