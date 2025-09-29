"""Resolver el problema de las N-reinas empleando backtracking con forward checking.

Cada fila del tablero se modela como una variable cuyo dominio contiene todas las
columnas posibles. Las restricciones garantizan que dos reinas no compartan
columna ni diagonales. El forward checking elimina valores incompatibles del
resto de los dominios tras cada asignación, reduciendo el espacio de búsqueda.

Se utiliza además la heurística de la mínima cantidad de valores restantes (MRV)
para seleccionar la siguiente variable a asignar.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

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
    variables = list(range(n))
    domains = {var: list(range(n)) for var in variables}
    return CspProblem(size=n, variables=variables, domains=domains)


def is_consistent(row: int, col: int, assignment: Assignment) -> bool:
    for other_row, other_col in assignment.items():
        if col == other_col:
            return False
        if abs(other_row - row) == abs(other_col - col):
            return False
    return True


def select_unassigned_variable(problem: CspProblem, assignment: Assignment, domains: Domain) -> int:
    remaining: Iterable[int] = (v for v in problem.variables if v not in assignment)
    return min(remaining, key=lambda var: len(domains[var]))


def forward_check(row: int, col: int, domains: Domain, assignment: Assignment) -> Optional[Domain]:
    new_domains: Domain = {}
    for var, values in domains.items():
        if var == row:
            new_domains[var] = [col]
            continue
        if var in assignment:
            new_domains[var] = [assignment[var]]
            continue
        filtered = [value for value in values if value != col and abs(var - row) != abs(value - col)]
        if not filtered:
            return None
        new_domains[var] = filtered
    return new_domains


def backtrack(
    problem: CspProblem,
    assignment: Assignment,
    domains: Domain,
    metrics: Dict[str, int],
) -> Optional[Assignment]:
    metrics["nodes_expanded"] += 1
    if len(assignment) == problem.size:
        return dict(assignment)

    var = select_unassigned_variable(problem, assignment, domains)
    for value in domains[var]:
        if not is_consistent(var, value, assignment):
            continue
        assignment[var] = value
        updated_domains = forward_check(var, value, domains, assignment)
        if updated_domains is not None:
            result = backtrack(problem, assignment, updated_domains, metrics)
            if result is not None:
                return result
        assignment.pop(var)

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
    raw_solution = backtrack(problem, assignment={}, domains=problem.domains, metrics=metrics)
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

    parser = argparse.ArgumentParser(description="Resolver N-reinas con forward checking")
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
