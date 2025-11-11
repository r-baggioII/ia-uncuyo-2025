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

---

# 3: Análisis de Complejidad de AC-3 en un CSP con Estructura de Árbol

## Contexto del problema

Un **CSP con estructura de árbol** es un problema de satisfacción de restricciones cuyo grafo de restricciones forma un árbol (grafo conexo sin ciclos). Esta estructura especial permite resolver el CSP de manera muy eficiente.

**Propiedades clave:**
- Grafo conexo sin ciclos
- $n$ variables implican exactamente $n-1$ arcos (aristas)
- Cada par de variables tiene a lo sumo una restricción directa entre ellas

## Complejidad temporal de AC-3 en árboles

### Teorema
Si el grafo de restricciones de un CSP es un **árbol**, entonces el algoritmo **AC-3** tiene complejidad temporal de **$O(n \cdot d^2)$**, donde:
- $n$ = número de variables
- $d$ = tamaño máximo de los dominios

### Demostración

**Paso 1: Número de arcos en un árbol**

En un árbol con $n$ nodos (variables), hay exactamente $n-1$ aristas. Como cada arista genera 2 arcos dirigidos (uno en cada dirección), tenemos:

$$\text{Total de arcos} = 2(n-1) = O(n)$$

**Paso 2: Análisis del algoritmo AC-3**

AC-3 mantiene una cola de arcos a revisar. Para cada arco $(X_i, X_j)$:

1. **Revisar el arco:** Verificar si cada valor $v \in D(X_i)$ tiene al menos un valor compatible en $D(X_j)$.
   - En el peor caso, revisar todos los pares $(v_i, v_j)$ con $v_i \in D(X_i)$ y $v_j \in D(X_j)$.
   - **Costo de una revisión:** $O(d^2)$ (comparar $d$ valores contra $d$ valores).

2. **Re-encolar arcos:** Si se reduce $D(X_i)$, se encolan arcos $(X_k, X_i)$ para todos los vecinos $X_k$ de $X_i$.

**Paso 3: Clave para árboles - Cada arco se procesa a lo sumo una vez**

**Lema:** En un CSP con estructura de árbol, cada arco $(X_i, X_j)$ se revisa **a lo sumo una vez** durante la ejecución de AC-3 (cuando se aplica directional arc consistency de forma topológica).

**Justificación:**
- En un árbol, no hay ciclos, por lo que no hay caminos alternativos que propaguen restricciones de vuelta.
- Si aplicamos AC-3 siguiendo un orden topológico (de hojas hacia raíz), cada variable se procesa exactamente una vez.
- Una vez que un arco $(X_i, X_j)$ se hace arco-consistente y no hay cambios en $D(X_j)$ posteriores, no necesita revisarse nuevamente.

**Paso 4: Cálculo de la complejidad total**

$$\begin{aligned}
\text{Complejidad total} &= (\text{número de arcos}) \times (\text{costo por revisión}) \\
&= O(n) \times O(d^2) \\
&= \boxed{O(n \cdot d^2)}
\end{aligned}$$

## Comparación con grafos generales

Para CSPs con grafos de restricciones **generales** (con ciclos), AC-3 puede tener complejidad de hasta **$O(e \cdot d^3)$**, donde $e$ es el número de aristas, porque:
- Cada arco puede ser revisado múltiples veces debido a ciclos en el grafo.
- En el peor caso, un arco puede ser re-encolado $O(d)$ veces (una por cada reducción del dominio del vecino).
- Con $e$ aristas y potencialmente $O(e \cdot d)$ revisiones de arcos, cada una costando $O(d^2)$, obtenemos $O(e \cdot d^3)$.

En grafos densos, $e$ puede ser $O(n^2)$, llevando a **$O(n^2 \cdot d^3)$** en el peor caso.

## Ventaja de la estructura de árbol

La estructura de árbol reduce dramáticamente la complejidad de AC-3:

| Estructura | Complejidad de AC-3 | Observaciones |
|------------|---------------------|---------------|
| **Árbol** | $O(n \cdot d^2)$ | Lineal en $n$ |
| **General** | $O(e \cdot d^3)$ | Puede ser $O(n^2 \cdot d^3)$ |

**Implicación práctica:** Para CSPs con estructura de árbol (o que pueden convertirse en árboles mediante eliminación de variables/condicionamiento), AC-3 es **polinomial** y muy eficiente, incluso garantizando encontrar todas las soluciones o detectar inconsistencias globales sin backtracking.

## Algoritmo eficiente para CSPs en árbol

**Procedimiento completo:**

1. **Elegir una variable raíz** arbitraria.
2. **Ordenar variables topológicamente** desde las hojas hacia la raíz (post-order traversal).
3. **Aplicar AC-3 direccionalmente:** procesar arcos de padres a hijos en orden reverso topológico.
4. **Complejidad total:** $O(n \cdot d^2)$ para hacer el grafo arco-consistente.
5. **Asignación de valores:** Si no hay dominios vacíos, asignar valores de raíz a hojas garantiza una solución sin backtracking.

**Complejidad total del solver:** $O(n \cdot d^2)$ - **polinomial y eficiente**.

---

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


