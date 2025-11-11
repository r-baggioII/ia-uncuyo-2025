#!/usr/bin/env python3
"""
Script para generar gráficas de evolución de H(t) para cada algoritmo.
Ejecuta una corrida representativa de cada algoritmo con record_history=True
y grafica la trayectoria de H a lo largo de las iteraciones/evaluaciones.
"""

import sys
import os
import matplotlib.pyplot as plt

# Agregar el path del código para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from algorithms import hill_climbing as HC
from algorithms import simulated_annealing as SA
from algorithms import genetic as GA
from algorithms import random_search as RS


def plot_evolution(n=8, max_evals=10000, seed=42):
    """
    Genera y guarda gráficas de evolución de H para cada algoritmo.
    
    Args:
        n: Tamaño del tablero (N-reinas)
        max_evals: Presupuesto máximo de evaluaciones
        seed: Semilla para reproducibilidad
    """
    # Configuración común
    env_n = 1
    
    # Ejecutar cada algoritmo con historial
    print(f"Ejecutando algoritmos para N={n} con historial activado...")
    
    print("  - Hill Climbing...")
    hc_result = HC.solve(n=n, max_evals=max_evals, seed=seed, env_n=env_n, record_history=True)
    
    print("  - Simulated Annealing...")
    sa_result = SA.solve(n=n, max_evals=max_evals, seed=seed+1, env_n=env_n, record_history=True)
    
    print("  - Genetic Algorithm...")
    ga_result = GA.solve(n=n, max_evals=max_evals, seed=seed+2, env_n=env_n, record_history=True)
    
    print("  - Random Search...")
    rs_result = RS.solve(n=n, max_evals=max_evals, seed=seed+3, env_n=env_n, record_history=True)
    
    # Crear directorio de salida
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "images")
    os.makedirs(output_dir, exist_ok=True)
    
    # Configurar el estilo de las gráficas
    plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
    
    # Crear figura con 4 subplots (2x2)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Evolución de H(t) - N-Reinas (N={n})', fontsize=16, fontweight='bold')
    
    # 1. Hill Climbing
    ax = axes[0, 0]
    if hc_result.get('history'):
        ax.plot(hc_result['history'], linewidth=2, color='#2E86AB', marker='o', markersize=3, markevery=max(1, len(hc_result['history'])//20))
        ax.set_title(f"Hill Climbing (steepest-ascent)\nH final={hc_result['H']}, Estados={hc_result['states']}", fontsize=12, fontweight='bold')
        ax.set_xlabel('Iteración (movimientos aceptados)', fontsize=10)
        ax.set_ylabel('H (pares en conflicto)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='green', linestyle='--', alpha=0.7, label='H=0 (solución)')
        ax.legend(loc='best')
    
    # 2. Simulated Annealing
    ax = axes[0, 1]
    if sa_result.get('history'):
        ax.plot(sa_result['history'], linewidth=2, color='#A23B72', marker='s', markersize=3, markevery=max(1, len(sa_result['history'])//20))
        ax.set_title(f"Simulated Annealing\nH final={sa_result['H']}, Pasos={sa_result['states']}", fontsize=12, fontweight='bold')
        ax.set_xlabel('Iteración (pasos)', fontsize=10)
        ax.set_ylabel('H (pares en conflicto)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='green', linestyle='--', alpha=0.7, label='H=0 (solución)')
        ax.legend(loc='best')
    
    # 3. Genetic Algorithm
    ax = axes[1, 0]
    if ga_result.get('history'):
        ax.plot(ga_result['history'], linewidth=2, color='#F18F01', marker='^', markersize=3, markevery=max(1, len(ga_result['history'])//20))
        ax.set_title(f"Genetic Algorithm\nH final={ga_result['H']}, Generaciones={len(ga_result['history'])}", fontsize=12, fontweight='bold')
        ax.set_xlabel('Generación', fontsize=10)
        ax.set_ylabel('H (pares en conflicto)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='green', linestyle='--', alpha=0.7, label='H=0 (solución)')
        ax.legend(loc='best')
    
    # 4. Random Search
    ax = axes[1, 1]
    if rs_result.get('history'):
        # Para random, graficar solo cada K puntos para que sea legible
        history_sample = rs_result['history'][::max(1, len(rs_result['history'])//100)]
        x_sample = list(range(0, len(rs_result['history']), max(1, len(rs_result['history'])//100)))
        ax.plot(x_sample, history_sample, linewidth=1.5, color='#C73E1D', alpha=0.7)
        ax.set_title(f"Random Search\nH final={rs_result['H']}, Muestras={rs_result['states']}", fontsize=12, fontweight='bold')
        ax.set_xlabel('Muestra (cada ~100)', fontsize=10)
        ax.set_ylabel('H (pares en conflicto)', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='green', linestyle='--', alpha=0.7, label='H=0 (solución)')
        ax.legend(loc='best')
    
    plt.tight_layout()
    
    # Guardar figura
    output_path = os.path.join(output_dir, f'evolution_H_N{n}.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✅ Gráfica guardada en: {output_path}")
    
    # Mostrar (opcional)
    # plt.show()
    plt.close()
    
    # Crear gráficas individuales más detalladas
    print("\nGenerando gráficas individuales...")
    
    algorithms = [
        ('Hill Climbing', hc_result, '#2E86AB', 'o'),
        ('Simulated Annealing', sa_result, '#A23B72', 's'),
        ('Genetic Algorithm', ga_result, '#F18F01', '^'),
        ('Random Search', rs_result, '#C73E1D', '.')
    ]
    
    for alg_name, result, color, marker in algorithms:
        if result.get('history'):
            plt.figure(figsize=(10, 6))
            
            if alg_name == 'Random Search':
                # Submuestrear para legibilidad
                step = max(1, len(result['history'])//500)
                x = list(range(0, len(result['history']), step))
                y = result['history'][::step]
                plt.plot(x, y, linewidth=1.5, color=color, alpha=0.7)
            else:
                plt.plot(result['history'], linewidth=2, color=color, marker=marker, 
                        markersize=4, markevery=max(1, len(result['history'])//30))
            
            plt.title(f'{alg_name} - Evolución de H(t) (N={n})', fontsize=14, fontweight='bold')
            plt.xlabel('Iteración', fontsize=12)
            plt.ylabel('H (pares en conflicto)', fontsize=12)
            plt.axhline(y=0, color='green', linestyle='--', alpha=0.7, linewidth=2, label='H=0 (solución)')
            plt.grid(True, alpha=0.3)
            plt.legend(loc='best', fontsize=10)
            
            # Añadir información en el gráfico
            info_text = f"H final: {result['H']}\nIteraciones: {result['states']}\nTiempo: {result['time']:.4f}s"
            plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            plt.tight_layout()
            
            safe_name = alg_name.lower().replace(' ', '_')
            individual_path = os.path.join(output_dir, f'evolution_{safe_name}_N{n}.png')
            plt.savefig(individual_path, dpi=150, bbox_inches='tight')
            print(f"  ✓ {individual_path}")
            plt.close()
    
    print("\n✅ Todas las gráficas generadas exitosamente!")
    
    # Imprimir resumen de resultados
    print("\n" + "="*60)
    print(f"RESUMEN DE RESULTADOS (N={n}, seed={seed})")
    print("="*60)
    print(f"{'Algoritmo':<25} {'H final':<10} {'Estados':<12} {'Tiempo (s)':<12}")
    print("-"*60)
    for alg_name, result, _, _ in algorithms:
        print(f"{alg_name:<25} {result['H']:<10} {result['states']:<12} {result['time']:<12.4f}")
    print("="*60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generar gráficas de evolución de H para N-Reinas")
    parser.add_argument("--n", type=int, default=8, help="Tamaño del tablero (default: 8)")
    parser.add_argument("--max-evals", type=int, default=10000, help="Presupuesto de evaluaciones (default: 10000)")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria (default: 42)")
    
    args = parser.parse_args()
    
    plot_evolution(n=args.n, max_evals=args.max_evals, seed=args.seed)
