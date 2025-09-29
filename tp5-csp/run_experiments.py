"""Ejecuta múltiples corridas de N-reinas con backtracking clásico y forward checking.

Genera archivos CSV con los resultados obtenidos para cada algoritmo.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from n_reinas_backtracking import solve_n_queens_with_metrics as solve_backtracking
from n_reinas_forward_checking import solve_n_queens_with_metrics as solve_forward

Solver = Callable[[int], Tuple[Optional[List[int]], Dict[str, int]]]


def build_solver(shuffle_domains: bool, base_solver: Solver) -> Callable[[int, int], Tuple[Optional[List[int]], Dict[str, int]]]:
    def _run(n: int, seed: int) -> Tuple[Optional[List[int]], Dict[str, int]]:
        return base_solver(n, seed=seed, shuffle_domains=shuffle_domains)

    return _run


def generate_seeds(count: int, start: int = 0) -> Sequence[int]:
    return list(range(start, start + count))


def write_results_csv(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def run_experiments(
    solver_name: str,
    solver: Callable[[int, int], Tuple[Optional[List[int]], Dict[str, int]]],
    sizes: Sequence[int],
    seeds: Sequence[int],
) -> List[Sequence[object]]:
    results: List[Sequence[object]] = []
    for n in sizes:
        for seed in seeds:
            start = time.time()
            solution, metrics = solver(n, seed)
            elapsed = time.time() - start
            success = solution is not None
            nodes = metrics.get("nodes_expanded", 0)
            solution_repr = "" if solution is None else " ".join(str(col) for col in solution)
            results.append((solver_name, n, seed, int(success), elapsed, nodes, solution_repr))
    return results


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Correr experimentos de N-reinas")
    parser.add_argument(
        "--n-values",
        nargs="*",
        type=int,
        default=[4, 8, 10],
        help="Tamaños de tablero a evaluar (por defecto: 4 8 10)",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        default=30,
        help="Cantidad de semillas a utilizar",
    )
    parser.add_argument(
        "--seed-offset",
        type=int,
        default=0,
        help="Semilla inicial para generar la secuencia",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=CURRENT_DIR / "results",
        help="Directorio donde guardar los CSV",
    )
    parser.add_argument(
        "--no-shuffle",
        dest="shuffle_domains",
        action="store_false",
        help="No barajar los dominios antes de resolver",
    )
    parser.set_defaults(shuffle_domains=True)
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    seeds = generate_seeds(args.seeds, start=args.seed_offset)

    solvers: Dict[str, Callable[[int, int], Tuple[Optional[List[int]], Dict[str, int]]]] = {
        "backtracking": build_solver(args.shuffle_domains, solve_backtracking),
        "forward_checking": build_solver(args.shuffle_domains, solve_forward),
    }

    header = [
        "algorithm",
        "n",
        "seed",
        "found",
        "runtime_seconds",
        "nodes_expanded",
        "solution",
    ]

    for name, solver in solvers.items():
        rows = run_experiments(name, solver, args.n_values, seeds)
        output_file = args.output_dir / f"{name}_results.csv"
        write_results_csv(output_file, header, rows)
        print(f"Resultados guardados en {output_file}")


if __name__ == "__main__":
    main()
