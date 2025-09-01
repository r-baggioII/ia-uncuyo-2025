# analyze_all_split.py
# ----------------------------------------------------
# Lee 16 CSV (2 escenarios x 8 algoritmos),
# calcula estadísticas (media, desvío estándar) SOLO sobre corridas con solución,
# y genera box-plots separados por escenario (UNIFORM y HORIZ_CHEAP)
# para cada métrica.
# Salidas: plots_out/*.png, summary_metrics.csv, per_run_solutions.csv
# ----------------------------------------------------

import os
import glob
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Configuración
# ----------------------------
CSV_DIR = Path("csv")  # carpeta con los 16 CSV (p.ej. csv/1.csv ... csv/16.csv)
OUTPUT_DIR = Path("plots_out")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALGO_ORDER = ["Random", "BFS", "DFS", "DLS-50", "DLS-75", "DLS-100", "UCS", "A*"]
SCENARIO_ORDER = ["UNIFORM", "HORIZ_CHEAP"]

# Métricas a resumir/plotear
METRICS_TO_SUMMARIZE = [
    ("states_n", "Estados explorados"),
    ("actions_count", "Acciones tomadas"),
    ("native_cost", "Costo (native_cost)"),
    ("actions_cost", "Costo (actions_cost)"),
    ("time", "Tiempo (s)")
]

# ----------------------------
# Utilidades
# ----------------------------
def find_csv_files(csv_dir: Path):
    """
    Busca CSVs con múltiples patrones:
      - csv/1.csv ... csv/16.csv
      - csv/1/results.csv ... csv/16/results.csv
      - csv/*.csv
      - csv/*/results.csv
    Devuelve hasta 16 rutas.
    """
    patterns = [
        str(csv_dir / "*.csv"),
        str(csv_dir / "*/*.csv"),
        str(csv_dir / "*/results.csv"),
    ]
    files = set()
    for pat in patterns:
        files.update(glob.glob(pat))

    # Heurística: priorizar numerados 1..16
    numbered = {}
    for f in files:
        p = Path(f)
        name = p.name.lower()
        num = None
        if name.endswith(".csv") and name[:-4].isdigit():
            num = int(name[:-4])
        elif p.parent.name.isdigit():
            num = int(p.parent.name)
        if num is not None and 1 <= num <= 16:
            numbered[num] = f

    if numbered:
        return [numbered[i] for i in sorted(numbered)]

    # Fallback: tomar los primeros 16
    files = sorted(list(files))[:16]
    return files

def coerce_bool(x):
    return str(x).strip().lower() in {"true", "1", "yes", "y"}

def clean_and_cast(df: pd.DataFrame) -> pd.DataFrame:
    # Ignorar filas de resumen
    df = df[~df["algorithm_name"].astype(str).str.startswith("SUMMARY_")].copy()

    # Tipos numéricos
    for col in ["states_n", "actions_count", "actions_cost", "native_cost", "time"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Bool solución
    if "solution_found" in df.columns:
        df["solution_found"] = df["solution_found"].apply(coerce_bool)
    else:
        df["solution_found"] = True

    # Normalizar strings
    df["scenario"] = df["scenario"].astype(str)
    df["algorithm_name"] = df["algorithm_name"].astype(str)
    return df

def agg_pop_std(x):
    """Desvío estándar poblacional (ddof=0)."""
    arr = x.to_numpy(dtype=float)
    return np.std(arr, ddof=0)

def sort_algorithms(labels):
    def keyfun(a):
        return ALGO_ORDER.index(a) if a in ALGO_ORDER else 999
    return sorted(labels, key=keyfun)

def sort_scenarios(labels):
    def keyfun(s):
        return SCENARIO_ORDER.index(s) if s in SCENARIO_ORDER else 999
    return sorted(labels, key=keyfun)

# ----------------------------
# Carga de datos
# ----------------------------
csv_files = find_csv_files(CSV_DIR)
if not csv_files:
    raise FileNotFoundError(
        f"No se encontraron CSVs en {CSV_DIR}. "
        f"Colocá tus 16 archivos en 'csv/' como '1.csv'..'16.csv' o '*/results.csv'."
    )

dfs = []
for fp in csv_files:
    df = pd.read_csv(fp)
    df = clean_and_cast(df)
    dfs.append(df)

raw_all = pd.concat(dfs, ignore_index=True)

# ----------------------------
# Filtrar SOLO corridas con solución
# ----------------------------
solutions = raw_all[raw_all["solution_found"] == True].copy()
solutions.to_csv(OUTPUT_DIR / "per_run_solutions.csv", index=False)

# ----------------------------
# Resumen (media, std poblacional, count) por escenario x algoritmo
# ----------------------------
grouped = solutions.groupby(["scenario", "algorithm_name"], dropna=False)
summary = (
    grouped[["states_n", "actions_count", "native_cost", "actions_cost", "time"]]
    .agg(["mean", agg_pop_std, "count"])
    .reset_index()
)

# Renombrar columnas
summary.columns = [
    "scenario", "algorithm_name",
    "states_n_mean", "states_n_std", "states_n_count",
    "actions_count_mean", "actions_count_std", "actions_count_count",
    "native_cost_mean", "native_cost_std", "native_cost_count",
    "actions_cost_mean", "actions_cost_std", "actions_cost_count",
    "time_mean", "time_std", "time_count",
]

# Ordenar por escenario y algoritmo
summary["scenario_order"] = summary["scenario"].apply(lambda s: SCENARIO_ORDER.index(s) if s in SCENARIO_ORDER else 999)
summary["algo_order"] = summary["algorithm_name"].apply(lambda a: ALGO_ORDER.index(a) if a in ALGO_ORDER else 999)
summary.sort_values(by=["scenario_order", "algo_order"], inplace=True)
summary.drop(columns=["scenario_order", "algo_order"], inplace=True)

summary.to_csv(OUTPUT_DIR / "summary_metrics.csv", index=False)

# ----------------------------
# Box-plots separados por escenario
# ----------------------------
scenarios_present = sort_scenarios(solutions["scenario"].dropna().unique().tolist())

def make_boxplot_by_scenario(metric: str, ylabel: str):
    for scen in scenarios_present:
        sub = solutions[solutions["scenario"] == scen]
        if sub.empty:
            print(f"[WARN] Sin datos para escenario {scen} en métrica {metric}")
            continue

        # Agrupar por algoritmo y ordenar
        by_algo = {algo: g[metric].dropna().values
                   for algo, g in sub.groupby("algorithm_name")}
        algo_labels = [a for a in sort_algorithms(list(by_algo.keys())) if len(by_algo[a]) > 0]
        data = [by_algo[a] for a in algo_labels]

        if not data:
            print(f"[WARN] Sin datos para boxplot {metric} en escenario {scen}")
            continue

        plt.figure(figsize=(12, 6))
        plt.boxplot(data, labels=algo_labels, showfliers=True)
        plt.title(f"Box plot de {ylabel} — Escenario: {scen} (solo soluciones)")
        plt.xlabel("Algoritmo")
        plt.ylabel(ylabel)
        plt.tight_layout()
        out_path = OUTPUT_DIR / f"boxplot_{metric}_{scen}.png"
        plt.savefig(out_path, dpi=150)
        print(f"Guardado: {out_path}")
        plt.close()

# Generar 2 gráficos por cada métrica (uno por escenario)
for metric, ylabel in METRICS_TO_SUMMARIZE:
    make_boxplot_by_scenario(metric, ylabel)

print("\nListo.")
print(f"- Resumen: {OUTPUT_DIR/'summary_metrics.csv'}")
print(f"- Corridas (solo soluciones): {OUTPUT_DIR/'per_run_solutions.csv'}")
print(f"- Box-plots: {OUTPUT_DIR.resolve()} (archivos 'boxplot_<metric>_<escenario>.png')\n")
