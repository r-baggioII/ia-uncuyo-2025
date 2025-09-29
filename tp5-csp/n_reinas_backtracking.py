"""Resolver el problema de las N-reinas usando backtracking clásico sin heurísticas.

Cada fila del tablero se modela como una variable con dominio en las columnas
[0, n). Las restricciones aseguran que:
- No haya dos reinas en la misma columna.
- No haya dos reinas en la misma diagonal (principal o secundaria).

El algoritmo aplica backtracking puro: recorre las filas en orden y prueba
colocar una reina en cada columna válida sin aplicar heurísticas adicionales
ni técnicas de poda como forward checking.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, List, Optional, Sequence, Tuple

Assignment = Dict[int, int]
Domain = Dict[int, List[int]]


@dataclass(frozen=True)
class CspProblem:
    """Representación simple de un CSP para N-reinas."""

    size: int
    variables: Sequence[int]
    domains: Domain


def build_problem(n: int) -> CspProblem:
    if n <= 0:
        raise ValueError("El número de reinas debe ser positivo")
    variables = list(range(n))  # Cada fila representa una variable
    domains = {var: list(range(n)) for var in variables}
    return CspProblem(size=n, variables=variables, domains=domains)


def is_consistent(row: int, col: int, assignment: Assignment) -> bool:
    for other_row, other_col in assignment.items():
        if col == other_col:
            return False  # Misma columna
        if abs(other_row - row) == abs(other_col - col):
            return False  # Misma diagonal
    return True


def backtrack(
    problem: CspProblem,
    row: int,
    assignment: Assignment,
    metrics: Dict[str, int],
) -> Optional[Assignment]:
    metrics["nodes_expanded"] += 1
    if row == problem.size:
        return dict(assignment)

    for value in problem.domains[row]:
        if not is_consistent(row, value, assignment):
            continue
        assignment[row] = value
        result = backtrack(problem, row + 1, assignment, metrics)
        if result is not None:
            return result
        assignment.pop(row)

    return None


def solve_n_queens(n: int) -> Optional[List[int]]:
    solution, _ = solve_n_queens_with_metrics(n)
    return solution


def solve_n_queens_with_metrics(
    n: int,
    *,
    seed: Optional[int] = None,
    shuffle_domains: bool = False,
) -> Tuple[Optional[List[int]], Dict[str, int]]:
    problem = build_problem(n)
    rng: Optional[Random] = Random(seed) if seed is not None else None
    if shuffle_domains:
        if rng is None:
            rng = Random()
        for values in problem.domains.values():
            rng.shuffle(values)

    metrics = {"nodes_expanded": 0}
    raw_solution = backtrack(problem, row=0, assignment={}, metrics=metrics)
    if raw_solution is None:
        return None, metrics

    solution = [raw_solution[row] for row in sorted(raw_solution.keys())]
    return solution, metrics


def board_to_string(solution: Sequence[int]) -> str:
    lines: List[str] = []
    size = len(solution)
    for row in range(size):
        line = ''.join('Q' if col == solution[row] else '.' for col in range(size))
        lines.append(line)
    return '\n'.join(lines)


def main(argv: Optional[Sequence[str]] = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Resolver N-reinas con backtracking clásico")
    parser.add_argument("n", type=int, help="Tamaño del tablero y número de reinas")
    parser.add_argument(
        "--show-board",
        action="store_true",
        help="Imprimir la solución como un tablero",
    )
    args = parser.parse_args(argv)

    solution = solve_n_queens(args.n)
    if solution is None:
        print(f"No existe solución para n={args.n}")
        return

    print(solution)
    if args.show_board:
        print('\n' + board_to_string(solution))


if __name__ == "__main__":
    main()
