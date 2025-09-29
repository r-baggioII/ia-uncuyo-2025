# Informe - Tp5 - CSP 

## 1. Formulación CSP del Sudoku

### a. Variables
- Una variable por cada celda del tablero. Notación: $X_{r,c}$, donde $r,c \in \{1,\dots,N\}$.
- Para el Sudoku clásico: $N=9$.
- Total: $N^2 = 81$ variables.

### b. Dominios
- Si la celda $(r,c)$ ya tiene una pista con valor fijo $v$:
  $$D_{r,c} = \{v\}$$
- Si está vacía:
  $$D_{r,c} = \{1,2,\dots,N\}$$

### c. Restricciones
El Sudoku exige que **cada número aparezca exactamente una vez en cada fila, columna y subcuadro**.

- **Filas:** Para cada fila $r$:
  $$\text{AllDifferent}(X_{r,1}, X_{r,2}, \dots, X_{r,N})$$

- **Columnas:** Para cada columna $c$:
  $$\text{AllDifferent}(X_{1,c}, X_{2,c}, \dots, X_{N,c})$$

- **Subcuadros:** El tablero se divide en cajas de $k \times k$ (con $k^2=N$). Para cada bloque $(B_r,B_c)$:
  $$\text{AllDifferent}\Big( \{ X_{r,c}\ \mid\ r\in[kB_r+1,\dots,k(B_r+1)],\ c\in[kB_c+1,\dots,k(B_c+1)] \}\Big)$$

En el Sudoku $9\times9$ ($k=3$), hay:
- 9 restricciones para filas,
- 9 para columnas,
- 9 para cajas.

En total: **27 restricciones AllDifferent**.

### d. Grafo de restricciones
- Nodo = variable $X_{r,c}$.
- Dos nodos están conectados si comparten fila, columna o caja.
- Cada fila, columna y caja forma un **clique** de tamaño $N$.
- Esto hace que el grafo de restricciones sea muy denso.

### e. Propagación / Consistencia
- Al fijar un valor en una celda, se elimina ese valor de los dominios de todas las celdas en la misma fila, columna y subcuadro (forward checking).
- Los propagadores de **AllDifferent** son más potentes que simplemente usar restricciones binarias de desigualdad.

### f. Objetivo
- Encontrar una asignación completa:
  $$\{X_{r,c} = v \mid r,c \in \{1,\dots,N\}\}$$
  que respete todas las restricciones.
- No hay función objetivo de optimización; es **pura satisfacción**.



# 2: Demostración de Inconsistencias (problema de coloreo de mapa)

**Colores disponibles:** $\{red, green, blue\}$

**Variables:** $WA, NT, SA, Q, NSW, V, T$

## Vecindades (restricciones $X \neq Y$):
- $WA$: $NT, SA$
- $NT$: $WA, SA, Q$
- $SA$: $WA, NT, Q, NSW, V$
- $Q$: $NT, SA, NSW$
- $NSW$: $SA, Q, V$
- $V$: $SA, NSW$
- $T$: (sin vecinos)

**Asignación parcial dada:** $WA=red$, $V=blue$

## Inicialización de dominios

$$\begin{aligned}
D(WA) &= \{red\} \\
D(V) &= \{blue\} \\
D(NT), D(SA), D(Q), D(NSW), D(T) &= \{red, green, blue\}
\end{aligned}$$

La cola de AC-3 comienza con **todos** los arcos $(X,Y)$ para cada restricción $X \neq Y$.

## Propagación (revisiones clave)

### 1) Efecto de $WA=red$
- Revisar $(NT, WA)$: como $WA$ solo permite $red$, eliminamos de $D(NT)$ el valor **red** $\Rightarrow D(NT) = \{green, blue\}$.
- Revisar $(SA, WA)$: quitamos **red** de $D(SA)$ $\Rightarrow D(SA) = \{green, blue\}$.

### 2) Efecto de $V=blue$
- Revisar $(SA, V)$: quitamos **blue** de $D(SA)$ $\Rightarrow \boxed{D(SA) = \{green\}}$ (¡dominio unitario!).
- Revisar $(NSW, V)$: quitamos **blue** de $D(NSW)$ $\Rightarrow D(NSW) = \{red, green\}$.

Al volverse unitario $SA$, AC-3 vuelve a **encolar** arcos $(Z, SA)$ para **todos los vecinos** $Z \in \{WA, NT, Q, NSW, V\}$.

### 3) Propagar $SA=green$
- $(NT, SA)$: eliminar **green** de $D(NT)$ $\Rightarrow \boxed{D(NT) = \{blue\}}$.
- $(Q, SA)$: eliminar **green** de $D(Q)$ $\Rightarrow D(Q) = \{red, blue\}$.
- $(NSW, SA)$: eliminar **green** de $D(NSW)$ $\Rightarrow D(NSW) = \{red\}$.
- $(WA, SA)$ y $(V, SA)$ no cambian (ya unitarios y distintos de green).

Al volverse unitario $NT$ y $NSW$, re-encolamos $(Z, NT)$ y $(Z, NSW)$ para sus vecinos.

### 4) Propagar $NT=blue$
- $(Q, NT)$: eliminar **blue** de $D(Q)$ $\Rightarrow \boxed{D(Q) = \{red\}}$.
- $(WA, NT)$ y $(SA, NT)$ no cambian (ya distintos).

Al volverse unitario $Q$, AC-3 encola $(Z, Q)$ para sus vecinos $\{NT, SA, NSW\}$.

### 5) Propagar $Q=red$
- $(NSW, Q)$: eliminar **red** de $D(NSW)$. Pero $D(NSW) = \{red\}$ $\Rightarrow$ **se vacía**: $\boxed{D(NSW) = \varnothing}$.

En cuanto **algún dominio queda vacío**, AC-3 detecta **inconsistencia**.

## Conclusión

La asignación parcial $WA=red, V=blue$ conduce, vía propagación AC-3, a:
- $SA=green$,
- $NT=blue$,
- $Q=red$,
- y por las restricciones $NSW \neq SA$ (green), $NSW \neq Q$ (red), $NSW \neq V$ (blue), $NSW$ **no tiene ningún color disponible**.

**AC-3** por sí solo detecta esta **inconsistencia** (dominio vacío) **sin** necesidad de backtracking.



# Comparación de Algoritmos para N-Reinas

## 1. Introducción
Se evaluaron distintos enfoques para resolver el problema de las N-Reinas:  
- **Backtracking (con y sin forward checking)**  
- **Hill Climbing (HC)**  
- **Simulated Annealing (SA)**  
- **Algoritmos Genéticos (GA)**  
- **Búsqueda aleatoria (Random)**  

Los algoritmos se compararon considerando **calidad de la solución (H)**, **tiempo de ejecución** y **escalabilidad**.

---

## 2. Resultados

### 2.1 Calidad de la solución (H)
- **Backtracking / Forward Checking**: siempre encuentran soluciones **óptimas (H=0)**.  
- **Hill Climbing (HC)**: alta variabilidad, suele atascarse en óptimos locales → muchas soluciones con H>0.  
- **Simulated Annealing (SA)**: mejora a HC escapando de óptimos locales, pero no siempre llega a H=0.  
- **Algoritmos Genéticos (GA)**: encuentran buenas soluciones ocasionalmente (H=0), pero dependen de parámetros y muestran variabilidad.  
- **Random**: muy baja calidad; rara vez encuentra soluciones sin conflictos.  

**Ganador en exactitud**: Backtracking / Forward Checking.

---

### 2.2 Tiempo de ejecución
- **Backtracking**: crece rápidamente con N; forward checking reduce el tiempo y la variabilidad.  
- **HC y SA**: muy rápidos, tiempos casi constantes incluso al aumentar N.  
- **GA**: tiempos más altos y variables por el manejo de poblaciones y generaciones.  
- **Random**: rápido, pero con pésimos resultados.  

**Ganador en velocidad**: HC y SA.

---

### 2.3 Escalabilidad
- **Backtracking**: adecuado solo para N pequeños/medianos; escala de forma exponencial.  
- **Forward Checking**: mejora la escalabilidad, pero sigue siendo exponencial.  
- **Metaheurísticas (HC, SA, GA)**: escalan mejor a N grandes, aunque sacrifican exactitud.  
- **Random**: trivialmente escalable, pero sin utilidad práctica.  

---

## 3. Conclusiones
- **Backtracking (con forward checking)** es la mejor opción si se busca **solución exacta garantizada**, adecuado para instancias pequeñas o medianas.  
- **Metaheurísticas (HC, SA, GA)** son preferibles en instancias grandes donde la exactitud absoluta no es crítica, ya que ofrecen soluciones aproximadas en tiempos mucho menores.  
- **Random** solo sirve como línea base de comparación.  

En resumen:  
- **Exactitud → Backtracking/Forward Checking**  
- **Eficiencia en N grandes → HC, SA, GA**  
- **Random → descartado en práctica**


## 4. Gráficos (Backtracking)
![nodos_boxplot](graficos/nodos_boxplot.png)
![tiempos_boxplot](graficos/tiempos_boxplot.png)


