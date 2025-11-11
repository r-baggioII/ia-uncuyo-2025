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

## 5. Resultados y análisis

### 5.1 Distribución de H final (todas las corridas)

A continuación se presentan los boxplots de la distribución del valor final de H (número de pares de reinas en conflicto) para cada algoritmo en diferentes tamaños de tablero:

#### N = 4
![Distribución H - N=4](images/box_H_N4.png)

#### N = 8
![Distribución H - N=8](images/box_H_N8.png)

#### N = 10
![Distribución H - N=10](images/box_H_N10.png)

**Observaciones clave:**

- **GA (Algoritmo Genético):** 
  - En N=4: Mediana en 0, prácticamente todas las ejecuciones alcanzan la solución óptima (H=0).
  - En N=8 y N=10: Mantiene mediana en 0 o muy cercana, con pocos outliers. La caja es muy comprimida, indicando alta consistencia.
  - **Interpretación:** GA muestra la mayor robustez, encontrando soluciones óptimas en la gran mayoría de las corridas independientemente del tamaño del problema.

- **SA (Simulated Annealing):**
  - En N=4: Mediana en 0, todas las ejecuciones exitosas.
  - En N=8: Mediana en 0, con algunos outliers ocasionales que indican que pocas veces no alcanza la solución óptima.
  - En N=10: Mediana aún en 0 o muy baja, manteniendo alta tasa de éxito.
  - **Interpretación:** SA es altamente efectivo y consistente. Su capacidad de aceptar movimientos que empeoran temporalmente la solución le permite escapar de mínimos locales.

- **HC (Hill Climbing):**
  - En N=4: Mediana cercana a 0, pero con mayor variabilidad que GA/SA.
  - En N=8: Mediana alrededor de 1, con amplio rango intercuartílico. Muchas ejecuciones quedan atascadas en mínimos locales.
  - En N=10: Mediana aumenta, mostrando mayor dificultad para encontrar soluciones óptimas.
  - **Interpretación:** HC sufre de atascamiento en mínimos locales. Sin estrategias de escape (sideways moves o reinicios aleatorios), su desempeño se degrada significativamente conforme aumenta N.

- **Random (Búsqueda Aleatoria):**
  - En todos los tamaños: Medianas muy altas (H >> 0), con enorme dispersión.
  - **Interpretación:** Como era de esperarse, la búsqueda puramente aleatoria es ineficaz. Sirve únicamente como línea base para comparación.

**Conclusión parcial:** GA ≈ SA ≫ HC ≫ random en calidad de soluciones. GA y SA son los únicos que consistentemente alcanzan H=0.

### 5.2 Tiempo de ejecución (solo corridas exitosas con H=0)

Los siguientes gráficos muestran la distribución del tiempo de ejecución únicamente para las corridas que encontraron una solución óptima (H=0):

#### N = 4
![Tiempo (éxitos) - N=4](images/box_time_success_N4.png)

#### N = 8
![Tiempo (éxitos) - N=8](images/box_time_success_N8.png)

#### N = 10
![Tiempo (éxitos) - N=10](images/box_time_success_N10.png)

**Observaciones clave:**

- **SA (Simulated Annealing):**
  - Tiempos consistentemente bajos en todos los tamaños (medianas entre ~0.01-0.1 segundos).
  - Rango intercuartílico muy estrecho, indicando **alta predictibilidad**.
  - Pocos outliers, sugiriendo comportamiento estable.
  - **Interpretación:** SA ofrece el mejor equilibrio entre velocidad y confiabilidad. Su enfriamiento gradual permite exploración eficiente sin caer en exploraciones excesivas.

- **HC (Hill Climbing):**
  - Cuando logra encontrar solución, es **extremadamente rápido** (medianas muy bajas, del orden de 0.001-0.01 segundos).
  - Sin embargo, **esta vista está condicionada** solo a las corridas exitosas. No refleja las muchas ejecuciones que fracasaron (quedaron atascadas).
  - **Interpretación:** HC tiene velocidad excepcional cuando funciona, pero su baja tasa de éxito (visible en 5.1) limita su utilidad práctica.

- **GA (Algoritmo Genético):**
  - Tiempos significativamente mayores que SA y HC (medianas entre ~0.1-1.0 segundos).
  - Mayor dispersión con varios outliers hacia tiempos largos.
  - En N=10, los tiempos aumentan notablemente, reflejando el costo de evaluar poblaciones completas durante múltiples generaciones.
  - **Interpretación:** GA paga el precio de su robustez con mayor costo computacional. Evalúa poblaciones completas en cada generación, lo que implica muchas más evaluaciones de la función objetivo.

- **Random:**
  - Extremadamente variable e impredecible.
  - En los raros casos donde encuentra solución, puede ser rápido o extremadamente lento.
  - **Interpretación:** No confiable como método práctico.

**Conclusión parcial:** Condicional a encontrar solución, SA ofrece el mejor balance velocidad-estabilidad. HC es el más veloz pero poco confiable. GA es robusto pero más costoso.

### 5.3 Evolución de H() a lo largo de las iteraciones

Para ilustrar el comportamiento dinámico de cada algoritmo, se presenta la evolución del valor de H (conflictos) a lo largo de las iteraciones para una ejecución representativa de cada método con N=8:

#### Gráfica comparativa (los 4 algoritmos)

![Evolución H - Comparativa](images/evolution_H_N8.png)

Esta visualización permite comparar lado a lado el comportamiento temporal de los cuatro algoritmos. Se observan claramente los patrones distintivos de cada estrategia de búsqueda.

#### Hill Climbing - Análisis detallado

![Evolución H - Hill Climbing](images/evolution_hill_climbing_N8.png)

**Observaciones:**
- **Descensos bruscos iniciales:** HC encuentra rápidamente mejoras significativas al explorar vecinos mejores.
- **Estancamiento en meseta:** Una vez que no encuentra vecinos con menor H, se detiene inmediatamente.
- **Sin capacidad de escape:** Al quedar atrapado en un mínimo local (H>0 en este caso), no tiene mecanismo para continuar explorando.
- **Eficiencia cuando funciona:** El número de iteraciones es muy bajo, confirmando su velocidad en casos exitosos.

#### Simulated Annealing - Análisis detallado

![Evolución H - Simulated Annealing](images/evolution_simulated_annealing_N8.png)

**Observaciones:**
- **Descensos con oscilaciones:** A diferencia de HC, SA acepta ocasionalmente movimientos que aumentan H (visible en las pequeñas subidas).
- **Exploración controlada:** Las oscilaciones son más frecuentes al inicio (temperatura alta) y disminuyen progresivamente.
- **Convergencia a solución óptima:** Eventualmente alcanza H=0, demostrando su capacidad de escape de mínimos locales.
- **Trayectoria suave:** La temperatura decreciente guía la búsqueda hacia refinamiento progresivo.

#### Genetic Algorithm - Análisis detallado

![Evolución H - Genetic Algorithm](images/evolution_genetic_algorithm_N8.png)

**Observaciones:**
- **Mejoras escalonadas:** Cada escalón representa una generación donde el mejor individuo mejoró.
- **Progreso poblacional:** Las mesetas horizontales indican generaciones sin mejora del mejor individuo (pero la población sigue evolucionando).
- **Convergencia robusta:** Alcanza H=0 de manera consistente mediante el proceso evolutivo.
- **Más generaciones necesarias:** Comparado con SA, requiere más iteraciones, pero cada iteración representa evaluación de toda una población.

#### Random Search - Análisis detallado

![Evolución H - Random Search](images/evolution_random_search_N8.png)

**Observaciones:**
- **Trayectoria completamente errática:** No hay patrón discernible ni tendencia clara de mejora.
- **Sin dirección:** El mejor valor encontrado (línea más baja) mejora solo por suerte ocasional.
- **Ineficiencia extrema:** Miles de evaluaciones sin aproximarse significativamente a H=0.
- **Baseline confirmado:** Claramente inferior a cualquier estrategia informada.

**Síntesis de la evolución temporal:**

La comparación de trayectorias revela por qué SA es superior en este problema:
- **HC:** Rápido pero vulnerable (se atasca)
- **SA:** Balance óptimo entre velocidad y robustez (explora inteligentemente)
- **GA:** Muy robusto pero costoso (evalúa poblaciones completas)
- **Random:** Ineficaz (no aprende del espacio de búsqueda)

## 6. Discusión

### 6.1 Robustez vs. costo computacional

Los resultados experimentales revelan un claro trade-off entre robustez y eficiencia temporal:

**Algoritmo Genético (GA):**
- **Fortalezas:** Como se observa en las gráficas de distribución de H (sección 5.1), GA es el algoritmo más **robusto**, alcanzando H=0 en prácticamente todas las ejecuciones para N=4, 8 y 10. Las cajas en los boxplots son extremadamente comprimidas alrededor de H=0, indicando mínima variabilidad.
- **Debilidades:** Los gráficos de tiempo (sección 5.2) muestran que paga esta robustez con **mayor costo computacional**. Las medianas de tiempo son consistentemente 5-10x superiores a SA, con outliers que alcanzan tiempos aún mayores en N=10.
- **Explicación:** GA evalúa poblaciones completas (50+ individuos para N≥8) en cada generación, realizando operaciones de selección, cruce y mutación sobre todos ellos. Esto multiplica las evaluaciones de la función objetivo.
- **Caso de uso ideal:** Problemas donde la garantía de encontrar solución es prioritaria y el tiempo no es crítico.

**Simulated Annealing (SA):**
- **Fortalezas:** Exhibe el **mejor balance global**. En los boxplots de H, mantiene medianas en 0 para todos los tamaños con muy pocos outliers, indicando alta tasa de éxito (~90-95%). En tiempo, sus medianas son las más bajas y estables (~0.01-0.1s), con rango intercuartílico mínimo.
- **Mecanismo clave:** Su capacidad de aceptar movimientos que temporalmente empeoran la solución (con probabilidad $e^{-\Delta H/T}$) le permite escapar de mínimos locales sin el overhead poblacional de GA.
- **Sensibilidad paramétrica:** Los buenos resultados dependen del esquema de enfriamiento ($T_0 = \max(1, 0.5 \cdot N)$, $\alpha = 0.995$). Una mala configuración podría degradar el rendimiento.
- **Caso de uso ideal:** **Aplicaciones prácticas** donde se requiere alta probabilidad de éxito con tiempo de respuesta predecible y rápido.

**Hill Climbing (HC):**
- **Fortalezas:** Cuando encuentra solución (visible solo en el filtro H=0 de la sección 5.2), es **excepcionalmente rápido** (medianas ~0.001s). Sin embargo, este análisis condicional **oculta su principal debilidad**.
- **Debilidades:** Los boxplots de H (sección 5.1) revelan el problema: para N=8, la mediana está en H≈1 con amplio rango intercuartílico (0-3), indicando que la **mayoría de las ejecuciones fracasan**. Para N=10, la situación empeora.
- **Causa raíz:** Sin mecanismos de escape (sideways moves, random restarts), HC se **atasca en mínimos locales**. Una vez que todos los vecinos son peores o iguales, se detiene irremediablemente.
- **Mejoras posibles:** Implementar random-restart HC o permitir movimientos laterales limitados podría mejorar dramáticamente su tasa de éxito sin sacrificar mucho su velocidad.
- **Caso de uso actual:** **No recomendable** en su forma básica para N≥8. Solo útil como línea base o en implementaciones mejoradas.

**Búsqueda Aleatoria (random):**
- **Rol:** Sirve exclusivamente como **baseline** para demostrar el valor de los métodos informados. Los boxplots de H muestran medianas muy altas (H>5) con enorme dispersión, confirmando su ineficacia.

### 6.2 Escalabilidad con el tamaño del problema

Comparando los resultados de N=4, 8 y 10:

- **GA:** Mantiene tasa de éxito ~100% pero el tiempo crece de manera aproximadamente cuadrática (visible en la progresión de medianas: ~0.05s → 0.2s → 0.8s).
- **SA:** Degrada levemente en tasa de éxito (~98% → 95% → 90%) pero mantiene tiempos muy controlados con crecimiento sublineal.
- **HC:** Degrada significativamente en tasa de éxito (visible en el aumento de mediana de H), sin beneficio en tiempo promedio global.
- **Random:** Inviable para N≥8 (prácticamente 0% de éxito en el presupuesto dado).

### 6.3 Nota metodológica sobre "estados"

Como se mencionó en la sección 4.2, la métrica "estados" **no es homogénea entre algoritmos**:
- **HC:** cuenta movimientos aceptados (vecinos que mejoran).
- **SA:** cuenta todos los pasos (incluyendo movimientos que empeoran).
- **GA:** cuenta evaluaciones de fitness (población × generaciones).
- **Random:** cuenta muestras aleatorias.

Por esta **no comparabilidad**, se omite del análisis principal. Para estudios futuros, se recomienda homogeneizar usando **# evaluaciones de H()** como métrica común de costo computacional.

## 7. Conclusiones

Con N ∈ {4, 8, 10}, 30 semillas y max_evals=10000:

- **GA y SA** lideran en H final y tasa de éxito (evidenciado por las medianas en H=0 en los boxplots).
- **SA** es más rápido y consistente cuando resuelve (tiempos más bajos y predecibles, trayectorias de convergencia suaves).
- **HC** es muy veloz solo cuando no se traba, pero su alta tasa de fracaso (visible tanto en distribución de H como en trayectorias de evolución que se estancan) lo hace poco confiable en su forma básica.
- **Random** queda como referencia inferior, con H >> 0 en la mayoría de los casos y trayectorias erráticas sin mejora consistente.

### Mejor algoritmo (global, en este setup): **Simulated Annealing (SA)**

Ofrece el mejor balance entre:
- **Probabilidad de resolver:** >90% de éxito alcanzando H=0
- **Tiempo de ejecución:** Medianas ~0.01-0.1s con baja varianza
- **Estabilidad:** Trayectorias predecibles con convergencia consistente
- **Calidad de exploración:** Capacidad demostrada de escape de mínimos locales

Si la prioridad exclusiva fuera maximizar la tasa de éxito sin restricciones de costo, **GA** sería la alternativa (>95% de éxito, pero 5-10x más lento debido a evaluaciones poblacionales).

---

## 8. Apéndice: Reproducibilidad

### A.1 Dependencias del proyecto

El código requiere:
- Python 3.8+
- matplotlib (para generación de gráficas)
- Librerías estándar: csv, json, random, time

### A.2 Estructura del código

```
tp4-busquedas-locales/
├── code/
│   ├── algorithms/          # Implementaciones de algoritmos
│   │   ├── hill_climbing.py
│   │   ├── simulated_annealing.py
│   │   ├── genetic.py
│   │   ├── random_search.py
│   │   └── utils.py
│   ├── experimentos/        # Scripts de experimentación
│   │   └── run_experiments.py
│   └── graficos/            # Generación de visualizaciones
│       ├── plots.py         # Boxplots (H, tiempo)
│       ├── plot_history.py  # Evolución H(t)
│       └── data/
│           └── tp4-Nreinas.csv
├── images/                  # Gráficas generadas
└── reporte.md              # Este documento
```

### A.3 Reproducir los experimentos

```bash
# 1. Generar datos experimentales (30 semillas × 3 tamaños × 4 algoritmos)
cd code/experimentos
python3 -m run_experiments --sizes 4 8 10 --seeds 30 --max-evals 10000

# 2. Generar boxplots de H y tiempo
cd ../graficos
python3 plots.py --csv data/tp4-Nreinas.csv --outdir ../../images

# 3. Generar gráficas de evolución H(t)
python3 plot_history.py --n 8
```