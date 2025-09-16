# TP4 – Búsquedas Locales en N-Reinas 

## 1. Objetivo

Implementar y comparar algoritmos de búsqueda local para el problema de N-Reinas, evaluando su desempeño empírico bajo un marco experimental reproducible. Se miden y grafican:

- **H final** (número de pares de reinas en conflicto; H=0 ⇒ solución).
- **Tiempo (s)** hasta la detención.
- **Evolución de H()** a lo largo de las iteraciones para una ejecución representativa por algoritmo.

## 2. Heurística utilizada 

Usamos la heurística de conflictos clásica:

**H(tablero) = cantidad de pares de reinas que se atacan (misma fila o misma diagonal).**

No se contabiliza columna porque la representación garantiza una reina por columna.

Con el tablero representado como vector `board` donde `board[c]` es la fila de la reina en la columna `c`, se define:

```
H(board) = #{(i,j) | i < j, [board[i] = board[j] o |board[i] - board[j]| = |i - j|]}
```

### Uso en cada algoritmo:

- **HC y SA:** minimizan directamente H.
- **GA:** define el fitness como -H(board) (maximiza fitness ⇔ minimiza H).
- **random:** evalúa candidatos con H y conserva el mejor observado.

**Objetivo global:** alcanzar H = 0 (solución válida).

## 3. Algoritmos implementados

### 3.1 Hill Climbing (HC, steepest-ascent)

- **Vecinos:** mover una reina en su columna a otra fila.
- **Estrategia:** elegir el mejor vecino con mejora estricta; sin sideways ni reinicios.
- **Corte:** no hay mejora o H=0.
- **Pros:** muy rápido cuando encuentra descenso.
- **Contras:** se atasca en mínimos locales/mesetas.

### 3.2 Simulated Annealing (SA)

- **Vecino:** cambio aleatorio (mover una reina de fila).
- **Aceptación:** mejoras y, con prob. exp(-Δ/T), también peores.
- **Enfriamiento:** T₀ = max(1, 0.5·N), α = 0.995, T_min = 1e-3.
- **Corte:** H=0, max_evals o T < T_min.
- **Pros:** escapa de mínimos locales; consistente.
- **Contras:** requiere sintonizar T₀/α.

### 3.3 Algoritmo Genético (GA)

- **Individuo:** vector de N filas.
- **Fitness:** -H(ind) (mayor es mejor).
- **Selección:** torneo (k=3), cruce: uniforme, mutación: por gen (p_m=0.1), elitismo: 5%.
- **Población por defecto:** max(50, 10·N); presupuesto: max_evals ≈ evaluaciones de fitness.
- **Pros:** muy robusto; suele llegar a H=0.
- **Contras:** más costoso (evalúa poblaciones completas).

### 3.4 Búsqueda Aleatoria (random)

- Muestra tableros al azar y conserva el mejor; corta si H=0.
- **Rol:** baseline.

## 4. Metodología experimental

### 4.1 Configuración base

- **Tamaños:** N ∈ {4, 8, 10}.
- **Réplicas:** 30 semillas por combinación.
- **Presupuesto por corrida:** max_evals = 10000 (mismo para todos).
- **Algoritmos:** random, HC, SA, GA.

### 4.2 Métricas registradas

- **H final** (objetivo).
- **Tiempo (s)** hasta la detención.
- **Historial H()** por iteración (una ejecución por algoritmo, misma seed).
- **Estados** (no comparado entre algoritmos; ver nota).

**Nota "estados":** la definición difiere por método (p.ej., HC cuenta movimientos aceptados; SA, pasos; GA, evaluaciones de fitness; random, muestras). Por ello no se usa para comparar en este informe.

## 5. Resultados y análisis (N=8 como caso ilustrativo)

### 5.1 Distribución de H final (todas las corridas)

- **GA y SA:** medianas muy bajas y muchas corridas en H=0 ⇒ alta tasa de éxito y consistencia.
- **HC:** mediana ~1; logra soluciones a veces, pero con atascos frecuentes.
- **random:** pobre; el éxito es raro y disperso.

**Conclusión parcial:** GA ≈ SA ≫ HC ≳ random en calidad de soluciones.

### 5.2 Tiempo (solo corridas exitosas)

- **SA:** rápido y estable (baja variabilidad).
- **HC:** muy veloz cuando funciona; esta vista condicional no refleja sus fallas.
- **GA:** tiempos mayores y con outliers por coste poblacional.
- **random:** muy variable (azar).

**Conclusión parcial:** Condicional a éxito, SA ofrece el mejor equilibrio rapidez-estabilidad; HC es veloz pero poco confiable; GA es robusto pero más costoso.

### 5.3 H() a lo largo de las iteraciones (una ejecución por algoritmo)

- **HC:** descensos bruscos hasta una meseta; si no mejora, se detiene (atasco).
- **SA:** descensos con pequeñas subidas aceptadas (exploración) hasta H=0.
- **GA:** mejoras escalonadas por generación (progreso poblacional).
- **random:** trayectoria errática; rara vez llega a 0.

## 6. Discusión

### Robustez vs. costo:

- **GA:** muy robusto (alta probabilidad de solución) a costa de más evaluaciones/tiempo.
- **SA:** excelente relación éxito/tiempo con baja variabilidad ⇒ opción práctica para N pequeños/medianos.
- **HC:** necesitaría reinicios y/o sideways moves para competir; tal como está, es poco fiable.
- **random:** baseline.

**Sobre "estados":** por su no homogeneidad entre métodos, se omite del análisis comparativo principal. Para justicia metodológica futura, medir #evaluaciones de H() en todos los algoritmos.

## 7. Conclusiones

Con N ∈ {4, 8, 10}, 30 semillas y max_evals=10000:

- **GA y SA** lideran en H final y tasa de éxito.
- **SA** es más rápido y consistente cuando resuelve.
- **HC** es muy veloz solo cuando no se traba.
- **random** queda como referencia inferior.

### Mejor algoritmo (global, en este setup): **Simulated Annealing (SA)**

Ofrece el mejor balance entre probabilidad de resolver, tiempo y estabilidad.

Si la prioridad exclusiva fuera maximizar la tasa de éxito sin restricciones de costo, **GA** sería la alternativa.