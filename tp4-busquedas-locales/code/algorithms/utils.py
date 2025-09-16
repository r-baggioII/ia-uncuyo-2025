from __future__ import annotations
import random
import math
from typing import List, Tuple, Dict, Any

Board = List[int]

def rng_from_seed(seed: int | None) -> random.Random:
    rng = random.Random()
    if seed is not None:
        rng.seed(seed)
    return rng

def random_board(n: int, rng: random.Random) -> Board:
    # Each index is a column, value is the row [0..n-1]
    return [rng.randrange(n) for _ in range(n)]

def H(board: Board) -> int:
    # Count number of attacking pairs (same row or same diagonal)
    n = len(board)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                conflicts += 1
    return conflicts

def best_neighbor(board: Board, rng: random.Random) -> Tuple[Board, int]:
    # Generate all neighbors by moving one queen in a column to another row
    n = len(board)
    best_h = math.inf
    bests: List[Board] = []
    current_h = H(board)
    for c in range(n):
        current_row = board[c]
        for r in range(n):
            if r == current_row:
                continue
            nb = board.copy()
            nb[c] = r
            h = H(nb)
            if h < best_h:
                best_h = h
                bests = [nb]
            elif h == best_h:
                bests.append(nb)
    if not bests:
        return board, current_h
    return rng.choice(bests), best_h

def random_neighbor(board: Board, rng: random.Random) -> Board:
    n = len(board)
    c = rng.randrange(n)
    r = rng.randrange(n)
    while r == board[c]:
        r = rng.randrange(n)
    nb = board.copy()
    nb[c] = r
    return nb

def result_dict(algorithm_name: str, size: int, env_n: int, board: Board, h: int, states: int, elapsed: float, history: list[int] | None = None) -> Dict[str, Any]:
    return {
        "algorithm_name": algorithm_name,
        "env_n": env_n,
        "size": size,
        "best_solution": board,
        "H": h,
        "states": states,
        "time": elapsed,
        **({"history": history} if history is not None else {}),
    }
