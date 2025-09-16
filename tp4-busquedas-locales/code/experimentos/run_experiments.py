from __future__ import annotations
import argparse, csv, json, os, time, importlib
from typing import List, Dict, Any

# Local imports via package-style path
from ..algorithms import hill_climbing as HC
from ..algorithms import simulated_annealing as SA
from ..algorithms import genetic as GA
from ..algorithms import random_search as RS

def run_once(alg_name: str, n: int, max_evals: int, seed: int, env_n: int) -> Dict[str, Any]:
    if alg_name == "HC":
        return HC.solve(n=n, max_evals=max_evals, seed=seed, env_n=env_n, record_history=False)
    if alg_name == "SA":
        return SA.solve(n=n, max_evals=max_evals, seed=seed, env_n=env_n, record_history=False)
    if alg_name == "GA":
        # modest defaults; GA uses evaluations as budget
        return GA.solve(n=n, max_evals=max_evals, seed=seed, env_n=env_n, record_history=False)
    if alg_name == "random":
        return RS.solve(n=n, max_evals=max_evals, seed=seed, env_n=env_n, record_history=False)
    raise ValueError(f"Unknown algorithm: {alg_name}")

def ensure_dirs(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Run N-Queens local-search experiments")
    parser.add_argument("--sizes", type=int, nargs="+", default=[4, 8, 10], help="Board sizes")
    parser.add_argument("--seeds", type=int, default=30, help="Number of seeds (env_n)")
    parser.add_argument("--max-evals", type=int, default=10000, help="Max states/evaluations per run (same for all algs)")
    parser.add_argument("--out", type=str, default=os.path.join(os.path.dirname(__file__), "..", "graficos", "data", "tp4-Nreinas.csv"),
                        help="Output CSV path (aggregated)")
    args = parser.parse_args()

    out_csv = os.path.abspath(args.out)
    ensure_dirs(out_csv)

    fieldnames = ["algorithm_name", "env_n", "size", "best_solution", "H", "states", "time"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for n in args.sizes:
            for env_n in range(1, args.seeds + 1):
                for alg in ["random", "HC", "SA", "GA"]:
                    seed = 10_000 * n + 100 * env_n + (0 if alg == "random" else len(alg))  # deterministic, unique-ish
                    res = run_once(alg, n, args.max_evals, seed=seed, env_n=env_n)
                    # Cast best_solution to JSON string for CSV
                    row = {
                        "algorithm_name": res["algorithm_name"],
                        "env_n": res["env_n"],
                        "size": res["size"],
                        "best_solution": json.dumps(res["best_solution"], ensure_ascii=False),
                        "H": res["H"],
                        "states": res["states"],
                        "time": f"{res['time']:.6f}",
                    }
                    w.writerow(row)
                    # Optional: also split per-size/alg files (commented by default)
                    # per_path = out_csv.replace("tp4-Nreinas.csv", f"results_{alg}_N{n}.csv")
                    # ensure_dirs(per_path)
                    # with open(per_path, "a", newline="", encoding="utf-8") as pf:
                    #     pw = csv.DictWriter(pf, fieldnames=fieldnames)
                    #     if pf.tell() == 0:
                    #         pw.writeheader()
                    #     pw.writerow(row)

    print(f"[OK] Saved aggregated results to: {out_csv}")

if __name__ == "__main__":
    main()
