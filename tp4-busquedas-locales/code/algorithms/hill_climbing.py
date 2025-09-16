from __future__ import annotations
import time
from typing import Dict, Any, List, Tuple
from .utils import H, best_neighbor, random_board, rng_from_seed, result_dict

def solve(n: int, max_evals: int, seed: int | None = None, env_n: int = 0, record_history: bool = False) -> Dict[str, Any]:
    rng = rng_from_seed(seed)
    start = time.perf_counter()
    board = random_board(n, rng)
    current_h = H(board)
    states = 1
    history: List[int] = [current_h] if record_history else []

    while states < max_evals and current_h > 0:
        nb, nb_h = best_neighbor(board, rng)
        # Canonical steepest-ascent: move only if strictly improves H
        if nb_h < current_h:
            board, current_h = nb, nb_h
            if record_history:
                history.append(current_h)
        else:
            break
        states += 1

    elapsed = time.perf_counter() - start
    return result_dict("HC", n, env_n, board, current_h, states, elapsed, history if record_history else None)
