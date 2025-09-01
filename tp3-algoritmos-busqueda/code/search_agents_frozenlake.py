import random
import heapq
from enum import Enum
from typing import List, Tuple, Optional, Dict

# ============================================================
# Generación de mapa (tal cual tu función)
# ============================================================
def generate_random_map_custom(size: int, p_frozen: float) -> List[str]:
    # Generar posiciones aleatorias para S y G
    pos_S_row = random.randint(0, size - 1)
    pos_S_col = random.randint(0, size - 1)
    pos_G_row = random.randint(0, size - 1)
    pos_G_col = random.randint(0, size - 1)
    
    # Asegurar que S y G no estén en la misma posición
    while pos_S_row == pos_G_row and pos_S_col == pos_G_col:
        pos_G_row = random.randint(0, size - 1)
        pos_G_col = random.randint(0, size - 1)
    
    mapa = []
    for i in range(size):
        row = ""
        for j in range(size):
            if i == pos_S_row and j == pos_S_col:
                row += "S"
            elif i == pos_G_row and j == pos_G_col:
                row += "G"
            else:
                row += "F" if random.random() < p_frozen else "H"
        mapa.append(row)
    
    return mapa

# ============================================================
# Utilidades
# ============================================================
Coord = Tuple[int, int]

ACTIONS = {
    "U": (-1, 0),
    "D": ( 1, 0),
    "L": ( 0,-1),
    "R": ( 0, 1),
}
MAX_ACTIONS = 1000  # *** vida del agente: 100 acciones ***


def find_symbol(grid: List[str], symbol: str) -> Optional[Coord]:
    for i, row in enumerate(grid):
        j = row.find(symbol)
        if j != -1:
            return (i, j)
    return None

def in_bounds(grid: List[str], r: int, c: int) -> bool:
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])

def is_traversable(ch: str) -> bool:
    # Se puede pisar S, F y G. H (agujero) es obstáculo.
    return ch in ("S", "F", "G")

def neighbors(grid: List[str], s: Coord):
    r, c = s
    for a, (dr, dc) in ACTIONS.items():
        nr, nc = r + dr, c + dc
        if in_bounds(grid, nr, nc) and is_traversable(grid[nr][nc]):
            yield a, (nr, nc)

def reconstruct_path(came_from: Dict[Coord, Tuple[Coord, str]], start: Coord, goal: Coord):
    path: List[Coord] = [goal]
    actions: List[str] = []
    cur = goal
    while cur != start:
        parent, act = came_from[cur]
        path.append(parent)
        actions.append(act)
        cur = parent
    path.reverse()
    actions.reverse()
    return path, actions

def overlay_path(grid: List[str], path: List[Coord]) -> List[str]:
    g2 = [list(row) for row in grid]
    for (r, c) in path:
        if g2[r][c] not in ("S", "G"):
            g2[r][c] = "*"
    return ["".join(row) for row in g2]

def print_grid(grid: List[str]) -> None:
    for row in grid:
        print(row)

# ============================================================
# Escenarios de costo
# ============================================================
class Scenario(Enum):
    UNIFORM = 1       # costo 1 por acción
    HORIZ_CHEAP = 2   # L/R = 1, U/D = 10

def step_cost(scenario: Scenario, action: str) -> int:
    if scenario == Scenario.UNIFORM:
        return 1
    elif scenario == Scenario.HORIZ_CHEAP:
        return 1 if action in ("L","R") else 10
    else:
        raise ValueError("Escenario desconocido")

def heuristic(scenario: Scenario, a: Coord, b: Coord) -> int:
    # Heurística admisible/consistente (costo mínimo para llegar recto)
    (r1,c1),(r2,c2) = a,b
    dr, dc = abs(r1-r2), abs(c1-c2)
    if scenario == Scenario.UNIFORM:
        return dr + dc
    elif scenario == Scenario.HORIZ_CHEAP:
        return dr*10 + dc*1
    else:
        return 0

# ============================================================
# 1) Búsqueda aleatoria (expansión al azar) con poda por vida
# ============================================================
def random_search(grid: List[str], start: Coord, goal: Coord, scenario: Scenario,
                  max_expansions: int = 100000, seed: Optional[int] = None):
    if seed is not None:
        random.seed(seed)
    frontier: List[Tuple[Coord,int]] = [(start, 0)]  # (estado, pasos)
    came_from: Dict[Coord, Tuple[Coord, str]] = {}
    best_steps: Dict[Coord, int] = {start: 0}
    expansions = 0

    while frontier and expansions < max_expansions:
        idx = random.randrange(len(frontier))
        current, steps = frontier.pop(idx)
        expansions += 1

        if current == goal:
            path, actions = reconstruct_path(came_from, start, goal)
            if len(actions) <= MAX_ACTIONS:
                total_cost = sum(step_cost(scenario, a) for a in actions)
                return path, actions, total_cost, expansions
            # si supera vida, seguimos buscando

        nbrs = list(neighbors(grid, current))
        random.shuffle(nbrs)
        for act, ns in nbrs:
            next_steps = steps + 1
            if next_steps > MAX_ACTIONS:
                continue
            if ns not in best_steps or next_steps < best_steps[ns]:
                best_steps[ns] = next_steps
                came_from[ns] = (current, act)
                frontier.append((ns, next_steps))

    return None, None, None, expansions

# ============================================================
# 2) BFS (óptimo en pasos si costos uniformes) con poda por vida
# ============================================================
from collections import deque
def bfs(grid, start, goal, scenario):
    q = deque([(start, 0)])  # (estado, pasos)
    came_from = {}
    best_steps = {start: 0}
    expansions = 0

    while q:
        current, steps = q.popleft()
        expansions += 1

        if current == goal:
            path, actions = reconstruct_path(came_from, start, goal)
            if len(actions) <= MAX_ACTIONS:
                total_cost = sum(step_cost(scenario, a) for a in actions)
                return path, actions, total_cost, expansions

        for act, ns in neighbors(grid, current):
            next_steps = steps + 1
            if next_steps > MAX_ACTIONS:
                continue
            if ns not in best_steps:
                best_steps[ns] = next_steps
                came_from[ns] = (current, act)
                q.append((ns, next_steps))

    return None, None, None, expansions

# ============================================================
# 3) DFS con poda por vida (no óptimo)
# ============================================================
def dfs(grid: List[str], start: Coord, goal: Coord, scenario: Scenario,
        max_expansions: int = 200000):
    stack: List[Tuple[Coord,int]] = [(start, 0)]  # (estado, pasos)
    came_from: Dict[Coord, Tuple[Coord, str]] = {}
    best_steps: Dict[Coord, int] = {start: 0}
    expansions = 0

    while stack and expansions < max_expansions:
        current, steps = stack.pop()
        expansions += 1

        if current == goal:
            path, actions = reconstruct_path(came_from, start, goal)
            if len(actions) <= MAX_ACTIONS:
                total_cost = sum(step_cost(scenario, a) for a in actions)
                return path, actions, total_cost, expansions

        # Expandir (podés barajar para variar el orden)
        nbrs = list(neighbors(grid, current))
        # random.shuffle(nbrs)
        for act, ns in nbrs:
            next_steps = steps + 1
            if next_steps > MAX_ACTIONS:
                continue
            # Permitimos re-visitar si encontramos menos pasos que antes
            if ns not in best_steps or next_steps < best_steps[ns]:
                best_steps[ns] = next_steps
                came_from[ns] = (current, act)
                stack.append((ns, next_steps))

    return None, None, None, expansions

# ============================================================
# 4) DLS (Depth-Limited Search) respetando vida (limit ≤ MAX_ACTIONS)
# ============================================================
def dls(grid: List[str], start: Coord, goal: Coord, scenario: Scenario, limit: int):
    limit = min(limit, MAX_ACTIONS)
    stack = [(start, 0)]  # (state, depth)
    came_from: Dict[Coord, Tuple[Coord, str]] = {}
    best_depth: Dict[Coord, int] = {start: 0}
    expansions = 0

    while stack:
        current, depth = stack.pop()
        expansions += 1
        if current == goal:
            path, actions = reconstruct_path(came_from, start, goal)
            if len(actions) <= MAX_ACTIONS:
                total_cost = sum(step_cost(scenario, a) for a in actions)
                return path, actions, total_cost, expansions

        if depth < limit:
            for act, ns in neighbors(grid, current):
                nd = depth + 1
                if nd > MAX_ACTIONS:
                    continue
                if ns not in best_depth or nd < best_depth[ns]:
                    best_depth[ns] = nd
                    came_from[ns] = (current, act)
                    stack.append((ns, nd))

    return None, None, None, expansions

# ============================================================
# 5) UCS (Costo Uniforme / Dijkstra) - óptimo con costos positivos + vida
# ============================================================
def ucs(grid, start, goal, scenario):
    pq = []  # (g, tie, node)
    tie = 0
    g_cost = {start: 0}
    g_steps = {start: 0}   # *** pasos acumulados ***
    came_from = {}
    heapq.heappush(pq, (0, tie, start))
    closed = set()
    expansions = 0

    while pq:
        g, _, current = heapq.heappop(pq)
        if current in closed:
            continue
        closed.add(current)
        expansions += 1

        if current == goal:
            path, actions = reconstruct_path(came_from, start, goal)
            if len(actions) <= MAX_ACTIONS:           # *** vida ***
                return path, actions, g_cost[goal], expansions

        for act, ns in neighbors(grid, current):
            step_c = step_cost(scenario, act)
            ng = g_cost[current] + step_c
            ns_steps = g_steps[current] + 1
            if ns_steps > MAX_ACTIONS:                # *** poda por vida ***
                continue

            # Relajar por costo; rastreamos también mejor cantidad de pasos
            if ns not in g_cost or ng < g_cost[ns]:
                g_cost[ns] = ng
                g_steps[ns] = ns_steps
                came_from[ns] = (current, act)
                tie += 1
                heapq.heappush(pq, (ng, tie, ns))

    return None, None, None, expansions

# ============================================================
# 6) A* (óptimo con heurística admisible/consistente) + vida
# ============================================================
def astar(grid: List[str], start: Coord, goal: Coord, scenario: Scenario):
    pq: List[Tuple[int, int, Coord]] = []  # (f, tie, node)
    tie = 0
    g_cost: Dict[Coord, int] = {start: 0}
    g_steps: Dict[Coord, int] = {start: 0}  # *** pasos acumulados ***
    came_from: Dict[Coord, Tuple[Coord, str]] = {}
    f0 = heuristic(scenario, start, goal)
    heapq.heappush(pq, (f0, tie, start))
    closed = set()
    expansions = 0

    while pq:
        f, _, current = heapq.heappop(pq)
        if current in closed:
            continue
        closed.add(current)
        expansions += 1

        if current == goal:
            path, actions = reconstruct_path(came_from, start, goal)
            if len(actions) <= MAX_ACTIONS:           # *** vida ***
                return path, actions, g_cost[goal], expansions

        for act, ns in neighbors(grid, current):
            step_c = step_cost(scenario, act)
            ng = g_cost[current] + step_c
            ns_steps = g_steps[current] + 1
            if ns_steps > MAX_ACTIONS:                # *** poda por vida ***
                continue

            if ns not in g_cost or ng < g_cost[ns]:
                g_cost[ns] = ng
                g_steps[ns] = ns_steps
                came_from[ns] = (current, act)
                tie += 1
                fn = ng + heuristic(scenario, ns, goal)
                heapq.heappush(pq, (fn, tie, ns))

    return None, None, None, expansions

# ============================================================
# Runner / Demo (configurado a 100x100, p_frozen=0.92)
# ============================================================
def run_and_show(name: str, fn, grid, s, g, scenario, *args):
    print(f"\n=== {name} ===")
    path, actions, cost, expansions = fn(grid, s, g, scenario, *args)
    if path is None:
        print(f"Sin solución (<= {MAX_ACTIONS} acciones). Nodos expandidos: {expansions}")
    else:
        print(f"Acciones: {'-'.join(actions)}  | Longitud: {len(actions)}")
        print(f"Costo total: {cost} | Nodos expandidos: {expansions}")

if __name__ == "__main__":
    # Entorno pedido: 100x100, p_frozen=0.92
    random.seed(7)
    size = 100
    p_frozen = 0.92
    grid = generate_random_map_custom(size, p_frozen)

    s = find_symbol(grid, "S")
    g = find_symbol(grid, "G")
    if s is None or g is None:
        raise RuntimeError("El mapa no contiene S o G")

    print("Mapa 100x100 generado. (No se imprime completo para evitar spam)")
    print(f"Inicio: {s} | Meta: {g} | MAX_ACTIONS = {MAX_ACTIONS}")

    # Escenario de costos: elegí uno
    scenario = Scenario.UNIFORM   # o Scenario.HORIZ_CHEAP

    # 1) Búsqueda aleatoria
    run_and_show("Búsqueda Aleatoria", random_search, grid, s, g, scenario, 100000, 7)

    # 2) BFS
    run_and_show("BFS (Anchura)", bfs, grid, s, g, scenario)

    # 3) DFS
    run_and_show("DFS (Profundidad)", dfs, grid, s, g, scenario)

    # 4) DLS con varios límites (los límites se recortan a MAX_ACTIONS si hace falta)
    for L in (50, 75, 100):
        run_and_show(f"DLS (Límite={L})", dls, grid, s, g, scenario, L)

    # 5) Costo Uniforme
    run_and_show("UCS (Costo Uniforme)", ucs, grid, s, g, scenario)

    # 6) A* con heurística admisible/consistente
    run_and_show("A* (Heurística admisible)", astar, grid, s, g, scenario)
