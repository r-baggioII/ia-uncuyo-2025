# Trabajo Práctico 7A: Introducción a ML

## 1. Flexibilidad de los Métodos de Aprendizaje de Máquinas

### a) $n$ extremadamente grande, $p$ pequeño

Respuesta: Flexible

Justificación: Al contar con una gran cantidad de ejemplos, esto va a evitar el potencial overfitting de los modelos flexibles. Estos son simples de implementar ya que p limita el espacio de búsqueda.

### b) $p$ extremadamente grande, $n$ pequeño

Respuesta: No flexible

Justificación: Un metodo flexible va a memorizar los datos, en cambio, con un metodo inflexible vamos a poder aproximar f con pocos ejemplos, y explorando todo p, cosa que para un flexible explotaría en dimensionalidad.

### c) La relación entre predictores y variable dependiente es altamente no lineal

Respuesta: Flexible

Justificación: Los modelos flexibles por definición sirven cuando estamos buscando una funcion f poco usual.

### d) La varianza de los términos de error, $\sigma^2 = \text{Var}(\epsilon)$, es extremadamente alta

Respuesta: No flexible

Justificación: Un metodo flexible intentaría adaptarse a cada uno de estos datos, introduciendo ruido en la función f.

---

## 2. Clasificación vs. Regresión e Inferencia vs. Predicción

### a) Salario de Directores Ejecutivos

* Tipo de Problema: Inferencia y regresión
* $n$: 500
* $p$: 3

### b) Éxito o Fracaso de Nuevo Producto

* Tipo de Problema: Clasificación y Predicción
* $n$:20
* $p$:13

### c) Predicción del Tipo de Cambio USD/Euro

* Tipo de Problema:Regresión y Predicción
* $n$: 52
* $p$: 3

---

## 3. Ventajas y Desventajas de la Flexibilidad


Un enfoque flexible se adapta a un mayor número de funciones f, sin embargo, este corre el riesgo de cometer overfitting, sobre todo, cuando n es chico.
Otra ventaja de los modelos menos flexibles, es que nos aportan muchos datos para inferencia comparados a uno flexible, en una regresión lineal, vemos la relacion directa entre features y resultados.

---

## 4. Enfoque Paramétrico vs. No Paramétrico

Un enfoque paramétrico reduce el problema a uno más simple, encontrar los parámetros adecuados para estimar f, lo que simplifica el proceso.
Un enfoque no paramtrico, al no asumir una forma de f, se adapta a un mayor número de funciones, sin embargo, este requiere de una mayor cantidad de datos al no reducir el problema.

## 5. K Vecinos Más Cercanos (KNN) para Clasificación

Punto de prueba: $X_1 = 0, X_2 = 0, X_3 = 0$.

### a) Distancia Euclidiana

| Obs. | $X_1$ | $X_2$ | $X_3$ | Distancia Euclidiana ($D_i$) |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 0 | 3 | 0 | **3** |
| 2 | 2 | 0 | 0 | **2** |
| 3 | 0 | 1 | 3 | **$\sqrt{10} \approx 3.1623$** |
| 4 | 0 | 1 | 2 | **$\sqrt{5} \approx 2.2361$** |
| 5 | -1 | 0 | 1 | **$\sqrt{2} \approx 1.4142$** |
| 6 | 1 | 1 | 1 | **$\sqrt{3} \approx 1.7321$** |

### b) Predicción con $K = 1$

* Predicción:Verde
* Justificación: El vecino más cercano es la obs 5

### c) Predicción con $K = 3$

* Vecinos más cercanos:
* Clases:
* Predicción: Rojo
* Justificación:2,5 y 6 son los más cercanos, siendo 2 de estos, rojo 

### d) Valor de $K$ si el límite de decisión de Bayes es altamente no lineal

* Valor esperado de $K$: Pequeño
* Razón: Al k ser pequeño, nos adaptamos mejor a cualquier funcion, ya que independientemente de su forma, nos vamos a quedar con pocos vecinos. Aumentar el K hace que sea menos flexible