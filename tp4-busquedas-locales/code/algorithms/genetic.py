from __future__ import annotations
import time, math
from typing import List, Tuple, Dict, Any
from .utils import H, rng_from_seed, result_dict

def _random_individual(n: int, rng) -> List[int]:
    # values 0..n-1 allowed in every column (index)
    return [rng.randrange(n) for _ in range(n)]

def _fitness(ind: List[int]) -> int:
    # Higher is better: use negative H
    return -H(ind)

def _tournament(pop: List[List[int]], k: int, rng) -> List[int]:
    # pick best fitness among k random
    best = None
    best_f = -10**9
    for _ in range(k):
        cand = rng.choice(pop)
        f = _fitness(cand)
        if f > best_f:
            best_f, best = f, cand
    return best[:]

def _crossover_uniform(p1: List[int], p2: List[int], rng) -> Tuple[List[int], List[int]]:
    # Uniform crossover: per gene choose parent randomly
    n = len(p1)
    c1 = p1[:]
    c2 = p2[:]
    for i in range(n):
        if rng.random() < 0.5:
            c1[i] = p2[i]
            c2[i] = p1[i]
    return c1, c2

def _mutate(ind: List[int], rng, pm: float) -> None:
    n = len(ind)
    for i in range(n):
        if rng.random() < pm:
            ind[i] = rng.randrange(n)

def solve(n: int, max_evals: int, seed: int | None = None, env_n: int = 0,
          record_history: bool = False,
          pop_size: int | None = None, tournament_k: int = 3, pm: float = 0.1,
          elite_frac: float = 0.05) -> Dict[str, Any]:

    rng = rng_from_seed(seed)
    start = time.perf_counter()

    pop_size = pop_size or max(50, 10 * n)  # baseline
    # initialize population
    population = [_random_individual(n, rng) for _ in range(pop_size)]
    evals = 0

    def eval_and_best(pop):
        nonlocal evals
        best = pop[0]
        best_f = _fitness(best); evals += 1
        for ind in pop[1:]:
            f = _fitness(ind); evals += 1
            if f > best_f:
                best, best_f = ind, f
        return best, best_f

    best, best_f = eval_and_best(population)
    history = [-best_f] if record_history else []  # store H
    # main GA loop
    elite_n = max(1, int(elite_frac * pop_size))

    while evals < max_evals and -best_f > 0:  # stop if H == 0
        # Elitism: keep copies of top elite_n
        ranked = sorted(population, key=lambda ind: _fitness(ind), reverse=True)
        elites = [ind[:] for ind in ranked[:elite_n]]

        # produce children
        children: List[List[int]] = []
        while len(children) + elite_n < pop_size:
            p1 = _tournament(population, tournament_k, rng)
            p2 = _tournament(population, tournament_k, rng)
            c1, c2 = _crossover_uniform(p1, p2, rng)
            _mutate(c1, rng, pm)
            _mutate(c2, rng, pm)
            children.append(c1)
            if len(children) + elite_n < pop_size:
                children.append(c2)

        population = elites + children
        # evaluate new population
        b, bf = eval_and_best(population)
        if bf > best_f:
            best, best_f = b, bf
        if record_history:
            history.append(-best_f)

    elapsed = time.perf_counter() - start
    # states: use number of evaluations as proxy for explored states
    return result_dict("GA", n, env_n, best, -best_f, evals, elapsed, history if record_history else None)
