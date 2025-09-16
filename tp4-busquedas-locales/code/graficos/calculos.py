from __future__ import annotations
import argparse, os, csv, json, math, statistics as stats
from collections import defaultdict
from typing import Dict, List, Tuple

def load_rows(path: str) -> List[Dict]:
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

def summarize(rows: List[Dict]):
    # group by (algorithm_name, size)
    groups: Dict[Tuple[str,int], List[Dict]] = defaultdict(list)
    for row in rows:
        groups[(row["algorithm_name"], row["size"])].append(row)

    summary = []
    for (alg, size), rs in sorted(groups.items()):
        successes = [r for r in rs if r["H"] == 0]
        success_rate = 100.0 * len(successes) / len(rs) if rs else 0.0

        H_values = [r["H"] for r in rs]
        H_mean = stats.mean(H_values) if H_values else math.nan
        H_std = stats.pstdev(H_values) if len(H_values) > 1 else 0.0

        # Time and states: for solutions only (as requested)
        times = [r["time"] for r in successes]
        states = [r["states"] for r in successes]
        time_mean = stats.mean(times) if times else math.nan
        time_std = stats.pstdev(times) if len(times) > 1 else 0.0
        states_mean = stats.mean(states) if states else math.nan
        states_std = stats.pstdev(states) if len(states) > 1 else 0.0

        summary.append({
            "algorithm_name": alg,
            "size": size,
            "runs": len(rs),
            "success_rate_%": round(success_rate, 2),
            "H_mean": round(H_mean, 3) if H_values else "",
            "H_std": round(H_std, 3) if H_values else "",
            "time_mean_s_success": round(time_mean, 6) if times else "",
            "time_std_s_success": round(time_std, 6) if times else "",
            "states_mean_success": round(states_mean, 2) if states else "",
            "states_std_success": round(states_std, 2) if states else "",
        })
    return summary

def save_summary(summary, out_path: str):
    fields = ["algorithm_name","size","runs","success_rate_%","H_mean","H_std","time_mean_s_success","time_std_s_success","states_mean_success","states_std_success"]
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in summary:
            w.writerow(row)
    print(f"[OK] Saved metrics to: {out_path}")

def main():
    ap = argparse.ArgumentParser(description="Compute metrics for TP4 point 5b")
    ap.add_argument("--csv", type=str, default=os.path.join(os.path.dirname(__file__), "data", "tp4-Nreinas.csv"))
    ap.add_argument("--out", type=str, default=os.path.join(os.path.dirname(__file__), "data", "metrics_summary.csv"))
    args = ap.parse_args()

    rows = load_rows(args.csv)
    summary = summarize(rows)
    save_summary(summary, args.out)

if __name__ == "__main__":
    main()
