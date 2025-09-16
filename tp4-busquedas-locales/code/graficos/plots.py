from __future__ import annotations
import argparse, os, csv, json
import matplotlib.pyplot as plt
from collections import defaultdict

def load_rows(path: str):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            row["env_n"] = int(row["env_n"])
            row["size"] = int(row["size"])
            row["H"] = int(row["H"])
            row["states"] = int(row["states"])
            row["time"] = float(row["time"])
            row["best_solution"] = json.loads(row["best_solution"])
            rows.append(row)
    return rows

def boxplot_metric(rows, metric_key: str, title: str, out_path: str, success_only: bool = False):
    by_size_alg = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if success_only and r["H"] != 0:
            continue
        by_size_alg[r["size"]][r["algorithm_name"]].append(r[metric_key])

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    for size, algs in sorted(by_size_alg.items()):
        labels = sorted(algs.keys())
        data = [algs[k] for k in labels]
        plt.figure()
        plt.boxplot(data, labels=labels)
        plt.title(f"{title} (N={size})")
        plt.xlabel("Algorithm")
        plt.ylabel(metric_key)
        plt.tight_layout()
        base, ext = os.path.splitext(out_path)
        path = f"{base}_N{size}{ext}"
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"[OK] Saved: {path}")

def main():
    ap = argparse.ArgumentParser(description="Generate boxplots from experiment CSV")
    ap.add_argument("--csv", type=str, default=os.path.join(os.path.dirname(__file__), "data", "tp4-Nreinas.csv"))
    ap.add_argument("--outdir", type=str, default=os.path.join(os.path.dirname(__file__), "img"))
    args = ap.parse_args()

    rows = load_rows(args.csv)

    boxplot_metric(rows, "H", "Distribución de H", os.path.join(args.outdir, "box_H.png"), success_only=False)
    boxplot_metric(rows, "time", "Tiempo (éxitos)", os.path.join(args.outdir, "box_time_success.png"), success_only=True)
    boxplot_metric(rows, "states", "Estados (éxitos)", os.path.join(args.outdir, "box_states_success.png"), success_only=True)

if __name__ == "__main__":
    main()
