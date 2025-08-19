import subprocess
import os
import json
import itertools
import statistics
from glob import glob
import csv
import time
import shutil

agent_path = "student_agents/my_random_agent.py"
sizes = [2, 4, 8, 16, 32, 64, 128]
dirt_rates = [0.1, 0.2, 0.4, 0.8]
repetitions = 10

results_json_dir = "resultados_experimentos_random_agent"
os.makedirs(results_json_dir, exist_ok=True)

results_dir = "experiment_results_random_agent"
os.makedirs(results_dir, exist_ok=True)

summary_file = os.path.join(results_dir, "summary_results.json")
csv_file = os.path.join(results_dir, "results.csv")

summary_data = []

def get_latest_json():
    """Busca el archivo JSON más reciente en game_data."""
    json_files = glob("game_data/*.json")
    return max(json_files, key=os.path.getctime) if json_files else None

for size, dirt in itertools.product(sizes, dirt_rates):
    print(f"\n=== Ejecutando tamaño={size}, suciedad={dirt} ===")
    run_results = []

    for rep in range(repetitions):
        print(f"  Repetición {rep+1}/{repetitions}...")

        subprocess.run([
            "python3", "run_agent.py",
            "--agent-file", agent_path,
            "--record",
            "--size", str(size),
            "--dirt-rate", str(dirt),
            "--seed", "12345"
        ], check=True)

        time.sleep(0.5)

        latest_file = get_latest_json()

        if latest_file is None:
            print("  ⚠ No se generó archivo JSON (posiblemente sin suciedad).")
            run_results.append({
                "repetition": rep + 1,
                "cleaned_cells": 0,
                "actions_taken": 0
            })
            continue

        dest_path = os.path.join(results_json_dir, os.path.basename(latest_file))
        shutil.move(latest_file, dest_path)

        with open(dest_path, "r") as f:
            data = json.load(f)

        cleaned_cells = data.get("cleaned_cells", 0)
        actions_taken = data.get("time_steps", len(data.get("actions", [])))

        run_results.append({
            "repetition": rep + 1,
            "cleaned_cells": cleaned_cells,
            "actions_taken": actions_taken
        })

    avg_cleaned = statistics.mean(r["cleaned_cells"] for r in run_results)
    avg_actions = statistics.mean(r["actions_taken"] for r in run_results)

    summary_data.append({
        "size": size,
        "dirt_rate": dirt,
        "average_cleaned_cells": avg_cleaned,
        "average_actions_taken": avg_actions,
        "runs": run_results
    })

with open(summary_file, "w") as f:
    json.dump(summary_data, f, indent=4)

with open(csv_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["size", "dirt_rate", "repetition", "cleaned_cells", "actions_taken"])
    for entry in summary_data:
        for run in entry["runs"]:
            writer.writerow([
                entry["size"],
                entry["dirt_rate"],
                run["repetition"],
                run["cleaned_cells"],
                run["actions_taken"]
            ])

print(f"\n✅ Experimentos completados.")
print(f"📄 Resumen JSON: {summary_file}")
print(f"📄 Datos CSV: {csv_file}")
print(f"📂 Archivos individuales en: {results_json_dir}")