"""Genera boxplots de tiempos y nodos explorados para los resultados de N-reinas."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt

MetricData = Dict[Tuple[str, int], Dict[str, List[float]]]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crear boxplots a partir de CSVs de experimentos")
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Archivos CSV producidos por run_experiments.py",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "graficos",
        help="Directorio donde guardar las imágenes generadas",
    )
    return parser.parse_args(argv)


def load_data(paths: Iterable[Path]) -> MetricData:
    data: MetricData = {}
    for path in paths:
        with path.open("r", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                algorithm = row["algorithm"]
                n = int(row["n"])
                key = (algorithm, n)
                metrics = data.setdefault(key, {"runtime_seconds": [], "nodes_expanded": []})
                metrics["runtime_seconds"].append(float(row["runtime_seconds"]))
                metrics["nodes_expanded"].append(float(row["nodes_expanded"]))
    return data


def build_series(data: MetricData, metric: str) -> Tuple[List[str], List[List[float]]]:
    labels: List[str] = []
    series: List[List[float]] = []
    keys = sorted(data.keys(), key=lambda item: (item[0], item[1]))
    for algorithm, n in keys:
        values = data[(algorithm, n)][metric]
        if not values:
            continue
        labels.append(f"{algorithm}\nn={n}")
        series.append(values)
    return labels, series


def save_boxplot(labels: List[str], series: List[List[float]], ylabel: str, title: str, path: Path) -> None:
    if not series:
        print(f"No hay datos para {title}, se omite la figura")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    width = max(6, len(labels) * 1.8)
    plt.figure(figsize=(width, 6))
    plt.boxplot(series, labels=labels, vert=True)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Gráfico guardado en {path}")


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    metric_data = load_data(args.files)
    labels_rt, series_rt = build_series(metric_data, "runtime_seconds")
    labels_nd, series_nd = build_series(metric_data, "nodes_expanded")

    save_boxplot(labels_rt, series_rt, "Tiempo de ejecución (s)", "Distribución de tiempos", args.output_dir / "tiempos_boxplot.png")
    save_boxplot(labels_nd, series_nd, "Nodos explorados", "Distribución de nodos explorados", args.output_dir / "nodos_boxplot.png")


if __name__ == "__main__":
    main()
