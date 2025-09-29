"""Analiza los resultados de los experimentos de N-reinas y genera estadísticas."""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analizar resultados de N-reinas")
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Archivos CSV generados por run_experiments.py",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directorio donde guardar los CSV con el resumen (opcional)",
    )
    return parser.parse_args(argv)


def read_results(path: Path) -> List[Dict[str, object]]:
    with path.open("r", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: List[Dict[str, object]] = []
        for row in reader:
            rows.append(
                {
                    "algorithm": row["algorithm"],
                    "n": int(row["n"]),
                    "seed": int(row["seed"]),
                    "found": int(row["found"]),
                    "runtime_seconds": float(row["runtime_seconds"]),
                    "nodes_expanded": int(row["nodes_expanded"]),
                }
            )
    return rows


def compute_statistics(rows: Sequence[Dict[str, object]]) -> Dict[int, Dict[str, float]]:
    grouped: Dict[int, List[Dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(row["n"], []).append(row)

    stats: Dict[int, Dict[str, float]] = {}
    for n, items in grouped.items():
        total = len(items)
        successes = [item for item in items if item["found"]]
        success_count = len(successes)
        success_rate = (success_count / total) * 100 if total else 0.0

        runtime_mean = runtime_std = nodes_mean = nodes_std = None
        if success_count:
            runtimes = [item["runtime_seconds"] for item in successes]
            nodes = [item["nodes_expanded"] for item in successes]
            runtime_mean = statistics.mean(runtimes)
            nodes_mean = statistics.mean(nodes)
            runtime_std = statistics.stdev(runtimes) if len(runtimes) > 1 else 0.0
            nodes_std = statistics.stdev(nodes) if len(nodes) > 1 else 0.0

        stats[n] = {
            "total_runs": total,
            "success_count": success_count,
            "success_rate": success_rate,
            "runtime_mean": runtime_mean,
            "runtime_std": runtime_std,
            "nodes_mean": nodes_mean,
            "nodes_std": nodes_std,
        }
    return stats


def format_value(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.6f}"


def write_summary(path: Path, algorithm: str, stats: Dict[int, Dict[str, float]]) -> None:
    header = [
        "algorithm",
        "n",
        "total_runs",
        "success_count",
        "success_rate",
        "runtime_mean",
        "runtime_std",
        "nodes_mean",
        "nodes_std",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for n in sorted(stats.keys()):
            values = stats[n]
            writer.writerow(
                [
                    algorithm,
                    n,
                    values["total_runs"],
                    values["success_count"],
                    f"{values['success_rate']:.2f}",
                    format_value(values["runtime_mean"]),
                    format_value(values["runtime_std"]),
                    format_value(values["nodes_mean"]),
                    format_value(values["nodes_std"]),
                ]
            )


def print_summary(algorithm: str, stats: Dict[int, Dict[str, float]]) -> None:
    print(f"Resumen para {algorithm}:")
    for n in sorted(stats.keys()):
        values = stats[n]
        success_rate = f"{values['success_rate']:.2f}%"
        runtime_mean = format_value(values["runtime_mean"]) or "-"
        runtime_std = format_value(values["runtime_std"]) or "-"
        nodes_mean = format_value(values["nodes_mean"]) or "-"
        nodes_std = format_value(values["nodes_std"]) or "-"
        print(
            f"  n={n}: éxito={values['success_count']}/{values['total_runs']} ({success_rate}), "
            f"tiempo medio={runtime_mean}s (σ={runtime_std}), "
            f"nodos medios={nodes_mean} (σ={nodes_std})"
        )


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    for file_path in args.files:
        rows = read_results(file_path)
        if not rows:
            print(f"Archivo vacío: {file_path}")
            continue
        algorithm = rows[0]["algorithm"]
        stats = compute_statistics(rows)
        print_summary(algorithm, stats)

        if args.output_dir is not None:
            output_dir = args.output_dir
        else:
            output_dir = file_path.parent
        summary_path = output_dir / f"{algorithm}_summary.csv"
        write_summary(summary_path, algorithm, stats)
        print(f"  Resumen guardado en {summary_path}\n")


if __name__ == "__main__":
    main()
