# run_experiments.py
import os
import json
import time
import random
import sys
from pathlib import Path
from statistics import mean
from typing import List, Dict, Any, Tuple

# ==== Gym / Gymnasium (para crear el entorno determinista) ====
try:
    import gymnasium as gym
except ImportError:
    import gym  # fallback si usás gym clásico

# Importa tu implementación (punto a)
from search_agents_frozenlake import (
    generate_random_map_custom,
    find_symbol,
    Scenario,
    random_search,
    bfs,
    dfs,
    dls,
    ucs,
    astar,
)

# -------------------------------------------------------------------
# Configuración de experimentos
# -------------------------------------------------------------------
N_ENVIRONMENTS = 30      # 30 corridas por combinación
SIZE = 100               # *** tamaño 100x100 ***
P_FROZEN = 0.92          # *** prob. de F = 0.92 (H = 0.08) ***

# Qué escenarios correr: ["UNIFORM"], ["HORIZ_CHEAP"] o ambos
SCENARIOS_TO_RUN = ["UNIFORM", "HORIZ_CHEAP"]

# Algoritmos a evaluar
ALGORITHMS = [
    "Random",
    "BFS",
    "DFS",
    "DLS(50)",
    "DLS(75)",
    "DLS(100)",
    "UCS",
    "A*",
]

# Semilla base para reproducibilidad de entornos
BASE_SEED = 12345

# Carpeta raíz de resultados (se crea si no existe)
RESULTS_ROOT = Path("resultados_experimentos")

# (Flag) Crear una instancia Gym por cada mapa para asegurar is_slippery=False
CREATE_GYM_ENV_FOR_MAPS = True  # no imprime nada; crea y cierra el env silenciosamente


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def scenario_from_name(name: str) -> Scenario:
    return Scenario.UNIFORM if name == "UNIFORM" else Scenario.HORIZ_CHEAP

def safe_dirname(text: str) -> str:
    # Reemplaza caracteres no alfanuméricos por "_"
    return "".join(ch if ch.isalnum() else "_" for ch in text)

def make_frozenlake_env_from_desc(desc, render: bool = False):
    """Crea un FrozenLake-v1 determinista (is_slippery=False) desde una lista de strings."""
    return gym.make(
        "FrozenLake-v1",
        desc=desc,
        is_slippery=False,                 # *** forzado a determinista ***
        render_mode="human" if render else None
    )

def run_once(
    algo_name: str,
    grid: List[str],
    s: Tuple[int, int],
    g: Tuple[int, int],
    scenario: Scenario,
    env_index: int
) -> Dict[str, Any]:
    start_t = time.perf_counter()
    if algo_name == "Random":
        path, actions, cost, expansions = random_search(grid, s, g, scenario, max_expansions=100000, seed=env_index)
    elif algo_name == "BFS":
        path, actions, cost, expansions = bfs(grid, s, g, scenario)
    elif algo_name == "DFS":
        path, actions, cost, expansions = dfs(grid, s, g, scenario)
    elif algo_name == "DLS(50)":
        path, actions, cost, expansions = dls(grid, s, g, scenario, 50)
    elif algo_name == "DLS(75)":
        path, actions, cost, expansions = dls(grid, s, g, scenario, 75)
    elif algo_name == "DLS(100)":
        path, actions, cost, expansions = dls(grid, s, g, scenario, 100)
    elif algo_name == "UCS":
        path, actions, cost, expansions = ucs(grid, s, g, scenario)
    elif algo_name == "A*":
        path, actions, cost, expansions = astar(grid, s, g, scenario)
    else:
        raise ValueError(f"Algoritmo desconocido: {algo_name}")
    elapsed = time.perf_counter() - start_t

    # Estructura esencial para guardar como JSON (sin prints en consola)
    result: Dict[str, Any] = {
        "algorithm": algo_name,
        "scenario": scenario.name,
        "env_index": env_index,
        "size": len(grid),
        "p_frozen": P_FROZEN,
        "grid": grid,               # lista de strings
        "start": list(s) if s else None,
        "goal": list(g) if g else None,
        "success": path is not None,
        "path": [list(x) for x in path] if path is not None else None,  # [[r,c],...]
        "actions": actions if path is not None else None,                # ["U","R",...]
        "path_len": len(path) if path is not None else None,
        "cost": cost if path is not None else None,
        "expansions": expansions,
        "time_sec": elapsed,
        # info Gym (documental): el entorno equivalente sería is_slippery=False
        "gym_is_slippery": False,
    }
    return result

def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    successes = [r for r in results if r["success"]]
    return {
        "runs": len(results),
        "success_rate": len(successes) / len(results) if results else 0.0,
        "avg_cost_success": mean(r["cost"] for r in successes) if successes else None,
        "avg_path_len_success": mean(r["path_len"] for r in successes) if successes else None,
        "avg_expansions": mean(r["expansions"] for r in results) if results else None,
        "avg_time_sec": mean(r["time_sec"] for r in results) if results else None,
    }

# -------- Barra de progreso simple (sin dependencias) --------
def progress_bar(current: int, total: int, prefix: str = "", width: int = 40):
    pct = 0.0 if total == 0 else current / total
    filled = int(width * pct)
    bar = "█" * filled + "·" * (width - filled)
    msg = f"\r{prefix} [{bar}] {current}/{total} ({pct*100:5.1f}%)"
    sys.stdout.write(msg)
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
if __name__ == "__main__":
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)

    # 1) Generar N entornos aleatorios una vez y reutilizarlos
    rng = random.Random(BASE_SEED)
    environments: List[List[str]] = []
    env_seeds: List[int] = []
    for i in range(N_ENVIRONMENTS):
        local_seed = rng.randint(0, 10**9)
        env_seeds.append(local_seed)
        random.seed(local_seed)
        grid = generate_random_map_custom(SIZE, P_FROZEN)
        environments.append(grid)

        # Crear un env Gym equivalente determinista (is_slippery=False) y cerrarlo
        if CREATE_GYM_ENV_FOR_MAPS:
            env = make_frozenlake_env_from_desc(grid, render=False)
            try:
                env.reset()
            finally:
                env.close()

    # Guardar metadata de entornos (trazabilidad)
    meta_path = RESULTS_ROOT / "metadata_entornos.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "n_environments": N_ENVIRONMENTS,
                "size": SIZE,
                "p_frozen": P_FROZEN,
                "base_seed": BASE_SEED,
                "environment_seeds": env_seeds,
                "gym_is_slippery": False,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    # 2) Ejecutar por escenario y algoritmo con barra de progreso
    total_combos = len(SCENARIOS_TO_RUN) * len(ALGORITHMS)
    total_runs = total_combos * N_ENVIRONMENTS
    run_count = 0

    for s_idx, scenario_name in enumerate(SCENARIOS_TO_RUN, start=1):
        scenario = scenario_from_name(scenario_name)

        for a_idx, algo_name in enumerate(ALGORITHMS, start=1):
            combo_dir = RESULTS_ROOT / f"{safe_dirname(scenario_name)}__{safe_dirname(algo_name)}"
            combo_dir.mkdir(parents=True, exist_ok=True)

            combo_results: List[Dict[str, Any]] = []

            # Prefijo de la barra para esta combinación
            combo_label = f"{scenario_name}__{algo_name}"
            prefix = f"Ejecutando {combo_label:<22} env"

            for env_idx, grid in enumerate(environments, start=1):
                # Barra de progreso por ejecución global
                run_count += 1
                progress_bar(run_count, total_runs, prefix=f"{prefix} {env_idx:02d}/{N_ENVIRONMENTS:02d}")

                s = find_symbol(grid, "S")
                g = find_symbol(grid, "G")
                if s is None or g is None:
                    # Mapa inválido: todavía guardamos algo para mantener la cuenta
                    result = {
                        "algorithm": algo_name,
                        "scenario": scenario.name,
                        "env_index": env_idx,
                        "env_seed": env_seeds[env_idx - 1],   # <<< semilla del entorno
                        "size": len(grid),
                        "p_frozen": P_FROZEN,
                        "grid": grid,
                        "start": None,
                        "goal": None,
                        "success": False,
                        "path": None,
                        "actions": None,
                        "path_len": None,
                        "cost": None,
                        "expansions": 0,
                        "time_sec": 0.0,
                        "note": "Mapa invalido: falta S o G",
                        "gym_is_slippery": False,
                    }
                else:
                    result = run_once(algo_name, grid, s, g, scenario, env_idx)
                    # <<< añadir semilla utilizada para ese entorno
                    result["env_seed"] = env_seeds[env_idx - 1]

                combo_results.append(result)

                # Guardar JSON de esta corrida: run_001.json, ..., run_030.json
                run_json_path = combo_dir / f"run_{env_idx:03d}.json"
                with run_json_path.open("w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

            # Resumen por combinación
            summary = summarize(combo_results)
            summary_path = combo_dir / "summary.json"
            with summary_path.open("w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Listo. JSONs guardados en: {RESULTS_ROOT.resolve()}")
