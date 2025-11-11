# Informe de Experimentos — Agente de Búsqueda en Grid

**Fecha:** 2025-09-01

## Resumen ejecutivo

- Se evaluaron **16 combinaciones**: 2 escenarios (_UNIFORM_ y _HORIZ_CHEAP_) × 8 algoritmos (**Random, BFS, DFS, DLS-50, DLS-75, DLS-100, UCS, A***).
- Cada combinación se ejecutó **30 veces**. Para el análisis se consideraron **solo las corridas con solución** (`solution_found == True`).
- Métricas analizadas: **estados explorados** (`states_n`), **acciones** (`actions_count`), **costo nativo del escenario** (`native_cost`) y **tiempo** (`time`).  
- El agente tiene **vida máxima = 1000 acciones**; esto influye en los algoritmos que tienden a caminos largos (p.ej., DFS), que saturan cerca de ese tope.

**Conclusiones rápidas**

1. **A*** y **UCS** son los más **eficientes y estables** (menos estados explorados y tiempos bajos) en ambos escenarios; su ventaja **aumenta** en _HORIZ_CHEAP_ por ser **sensibles a costos**.
2. **DFS** muestra **alta variabilidad** y con frecuencia **satura la vida (≈1000 acciones)**; explora muchos estados y es el de **mayor costo/tiempo** en mediana.
3. **BFS** y **Random** tienen desempeño intermedio; **BFS** mejora en _UNIFORM_ (costo homogéneo) pero **empeora su costo** en _HORIZ_CHEAP_ (no es costo–informado).
4. **DLS** respeta sus límites de profundidad en **acciones** (≈50/75/100), pero puede requerir **muchísimos estados** para hallar soluciones (sobre todo **DLS(100)**); su tiempo crece en consonancia.
5. La relación **tiempo ↔ estados explorados** es clara: más expansión ⇒ más tiempo.

---

## Metodología

- **Datos**: 16 CSV (uno por combinación) con 30 corridas cada uno.
- **Filtrado**: se excluyeron corridas sin solución para evitar mezclar exploración fallida con caminos reales.
- **Estadística**: para cada métrica se calculó distribución y se graficó **box plot** por **escenario** (dos gráficos por métrica).
- **Interpretación**: mediana (línea central), rango intercuartílico (caja), bigotes (≈1.5×IQR) y outliers.

### Heurística utilizada en A*

El algoritmo A* utiliza una **función heurística** que estima el costo restante desde un estado hasta el objetivo. La heurística implementada es **admisible** y **consistente** (monótona), lo que garantiza que A* encuentre la solución óptima.

**Definición de la heurística:**

La heurística se adapta al escenario de costos:

1. **Escenario UNIFORM** (costo uniforme = 1 por acción):
   ```
   h(estado, objetivo) = distancia_Manhattan(estado, objetivo)
   h(estado, objetivo) = |r1 - r2| + |c1 - c2|
   ```
   Donde `(r1, c1)` son las coordenadas del estado actual y `(r2, c2)` las del objetivo.
   
   Esta es la **distancia Manhattan** (o distancia de taxi), que calcula el número mínimo de pasos horizontales y verticales necesarios para alcanzar el objetivo, asumiendo que no hay obstáculos.

2. **Escenario HORIZ_CHEAP** (L/R = 1, U/D = 10):
   ```
   h(estado, objetivo) = |r1 - r2| × 10 + |c1 - c2| × 1
   ```
   
   Esta heurística **pondera la distancia** según los costos de cada tipo de movimiento:
   - Movimientos verticales (U/D): cada paso vertical en línea recta costaría 10
   - Movimientos horizontales (L/R): cada paso horizontal en línea recta costaría 1

**Propiedades de admisibilidad:**

- La heurística **nunca sobreestima** el costo real porque asume el camino en línea recta sin obstáculos, que es el más corto posible.
- En el escenario UNIFORM: la distancia Manhattan es el mínimo de pasos necesarios.
- En el escenario HORIZ_CHEAP: la suma ponderada representa el costo mínimo si se pudiera ir en línea recta.

**Consistencia (monotonía):**

Para cada par de estados vecinos `n` y `n'` conectados por la acción `a`:
```
h(n) ≤ costo(n, a, n') + h(n')
```

Esta propiedad se cumple porque cada paso hacia el objetivo reduce la distancia heurística en exactamente el costo del movimiento (o menos, si el movimiento no es directo al objetivo).

**Impacto en el rendimiento:**

La heurística informada permite que A* explore significativamente menos estados que algoritmos no informados (BFS, UCS), priorizando los caminos más prometedores hacia el objetivo. Como se observa en los resultados, A* mantiene el menor número de estados explorados y tiempo de ejecución, especialmente en el escenario HORIZ_CHEAP donde la heurística guía eficazmente hacia rutas horizontales preferentes.

---

## Resultados por métrica

### 1) Acciones tomadas (`actions_count`)

**HORIZ_CHEAP**  
![Acciones — HORIZ_CHEAP](images/boxplot_actions_count_HORIZ_CHEAP.png)

**UNIFORM**  
![Acciones — UNIFORM](images/boxplot_actions_count_UNIFORM.png)

**Lecturas clave**

- **DFS**: distribución con **medianas muy altas** y dispersión extrema; muchos casos rondan **≈1000 acciones** (tope de vida), lo que anticipa altos costos y tiempos.
- **DLS**: los box plots se **alinean con el límite** (≈50, 75, 100), confirmando que el número de acciones del plan hallado casi siempre está acotado por la profundidad. Sin embargo, esto **no implica** menos **estados** (ver más abajo).
- **A*** / **UCS**: requieren notablemente **menos acciones** que DFS/BFS/Random. **A*** suele estar entre los mejores en mediana.
- **BFS** / **Random**: zona media; **BFS** algo más estable que **Random**.

> Bajo _UNIFORM_, los órdenes relativos son muy parecidos, porque el costo equivale a longitud del camino. Bajo _HORIZ_CHEAP_, esta métrica por sí sola **no captura el efecto del costo direccional** (ver `native_cost`).

---

### 2) Costo nativo (`native_cost`)

**HORIZ_CHEAP**  
![Costo — HORIZ_CHEAP](images/boxplot_native_cost_HORIZ_CHEAP.png)

**UNIFORM**  
![Costo — UNIFORM](images/boxplot_native_cost_UNIFORM.png)

**Lecturas clave**

- **UNIFORM**: el costo es básicamente la longitud del camino; por eso las jerarquías **replican** lo visto en `actions_count` (A*/UCS ≪ BFS/Random ≪ DFS; DLS cerca de sus límites).
- **HORIZ_CHEAP**: el costo **penaliza verticales** (U/D=10).  
  - **A*** y **UCS** **mantienen costos bajos**: aprovechan la información de costo/grafo y **prefieren horizontales** cuando conviene.  
  - **BFS** y **DFS** **incrementan significativamente su costo** respecto a _UNIFORM_, porque **no consideran pesos** al elegir el siguiente nodo.  
  - **DLS**: medianas **sensiblemente mayores** que en _UNIFORM_, con distinta dispersión según el límite. **DLS(100)** destaca por **costos y varianza altos**.

> En este escenario, la **ventaja real de los algoritmos costo–informados** (UCS/A*) se vuelve **más marcada**.

---

### 3) Estados explorados (`states_n`)

**HORIZ_CHEAP**  
![Estados — HORIZ_CHEAP](images/boxplot_states_n_HORIZ_CHEAP.png)

**UNIFORM**  
![Estados — UNIFORM](images/boxplot_states_n_UNIFORM.png)

**Lecturas clave**

- **DFS** y **DLS(100)** pueden alcanzar **decenas de miles** de estados; aparecen **outliers muy altos** (p.ej., >100k), reflejando **búsquedas profundas** y poco guiadas.
- **A*** mantiene **medianas muy bajas** y **poca varianza**, señal de **exploración dirigida** por heurística. **UCS** también es bajo, aunque normalmente **explora más que A*** (al no usar heurística).
- **BFS** y **Random** quedan en una **zona media**, con mayor varianza que A*/UCS.
- **DLS(50)/DLS(75)**: aunque limitan la **profundidad del plan**, pueden implicar muchas **expansiones** para alcanzar una solución factible dentro del límite.

---

### 4) Tiempo (`time`, segundos)

**HORIZ_CHEAP**  
![Tiempo — HORIZ_CHEAP](images/boxplot_time_HORIZ_CHEAP.png)

**UNIFORM**  
![Tiempo — UNIFORM](images/boxplot_time_UNIFORM.png)

**Lecturas clave**

- El **tiempo** se correlaciona fuertemente con **estados explorados**: **DFS** y **DLS(100)** presentan las **colas más largas**.  
- **A*** es sistemáticamente de los **más rápidos**, seguido por **UCS**.  
- **BFS** y **Random** suelen quedar en el **medio**, coherente con su volumen de expansión.

---

## Discusión y síntesis comparativa

1. **Eficiencia global**  
   - **A*** se destaca como el **más consistente** (baja varianza) y **eficiente** en **estados** y **tiempo**, con **costos** competitivos en ambos escenarios.  
   - **UCS** es cercano a A*, especialmente en escenarios con **costos informativos**; explora algo más pero **optimiza costo** de forma segura.
2. **Algoritmos no informados**  
   - **BFS** es competitivo en **UNIFORM** (donde costo ~ longitud), pero **pierde ventaja** en **HORIZ_CHEAP** por ignorar pesos.  
   - **DFS** es **inestable** y arriesga **saturar vida** (≈1000 acciones), elevando **costo** y **tiempo**.
3. **Búsqueda con límite de profundidad (DLS)**  
   - Controla **longitud del plan** (≈50/75/100 acciones), útil si hay **restricciones duras** de plan/vida.  
   - Aun así, puede requerir **gran expansión** (especialmente DLS(100)). Si la **heurística/cola de prioridad** están disponibles, **A*** o **UCS** resultan preferibles para eficiencia total.
4. **Impacto del costo direccional (HORIZ_CHEAP)**  
   - Penaliza verticales ⇒ incrementa fuertemente los costos de **BFS/DFS/DLS**.  
   - **A*** y **UCS** aprovechan los pesos para **reducir el costo final**, reforzando su superioridad práctica.

---

