# Formulación CSP del Sudoku

## 1. Variables
- Una variable por cada celda del tablero. Notación: $X_{r,c}$, donde $r,c \in \{1,\dots,N\}$.
- Para el Sudoku clásico: $N=9$.
- Total: $N^2 = 81$ variables.

## 2. Dominios
- Si la celda $(r,c)$ ya tiene una pista con valor fijo $v$:
  $$D_{r,c} = \{v\}$$
- Si está vacía:
  $$D_{r,c} = \{1,2,\dots,N\}$$

## 3. Restricciones
El Sudoku exige que **cada número aparezca exactamente una vez en cada fila, columna y subcuadro**.

- **Filas:** Para cada fila $r$:
  $$\text{AllDifferent}(X_{r,1}, X_{r,2}, \dots, X_{r,N})$$

- **Columnas:** Para cada columna $c$:
  $$\text{AllDifferent}(X_{1,c}, X_{2,c}, \dots, X_{N,c})$$

- **Subcuadros:** El tablero se divide en cajas de $k \times k$ (con $k^2=N$). Para cada bloque $(B_r,B_c)$:
  $$\text{AllDifferent}\Big( \{ X_{r,c}\ \mid\ r\in[kB_r+1,\dots,k(B_r+1)],\ c\in[kB_c+1,\dots,k(B_c+1)] \}\Big)$$

👉 En el Sudoku $9\times9$ ($k=3$), hay:
- 9 restricciones para filas,
- 9 para columnas,
- 9 para cajas.

En total: **27 restricciones AllDifferent**.

## 4. Grafo de restricciones
- Nodo = variable $X_{r,c}$.
- Dos nodos están conectados si comparten fila, columna o caja.
- Cada fila, columna y caja forma un **clique** de tamaño $N$.
- Esto hace que el grafo de restricciones sea muy denso.

## 5. Propagación / Consistencia
- Al fijar un valor en una celda, se elimina ese valor de los dominios de todas las celdas en la misma fila, columna y subcuadro (forward checking).
- Los propagadores de **AllDifferent** son más potentes que simplemente usar restricciones binarias de desigualdad.

## 6. Objetivo
- Encontrar una asignación completa:
  $$\{X_{r,c} = v \mid r,c \in \{1,\dots,N\}\}$$
  que respete todas las restricciones.
- No hay función objetivo de optimización; es **pura satisfacción**.