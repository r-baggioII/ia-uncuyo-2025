# Trabajo Práctico 7A: Introducción a ML

## 1. Flexibilidad de los Métodos de Aprendizaje de Máquinas

### a) $n$ extremadamente grande, $p$ pequeño

Respuesta: método flexible 


Justificación:
En este escenario ($n$ grande, $p$ pequeño), se espera que un **método flexible se comporte mejor**. La razón principal es que la gran cantidad de observaciones ($n$) mitiga el principal riesgo de los modelos flexibles: la alta varianza o sobreajuste. Un modelo flexible tiene un sesgo bajo, lo que le permite capturar patrones complejos o no lineales en $f$. Si bien esto normalmente podría llevarlo a "memorizar" el ruido en muestras pequeñas, un $n$ grande le permite distinguir el ruido de la señal verdadera. Además, un $p$ pequeño evita la maldición de la dimensionalidad, asegurando que los datos cubran densamente el espacio de predictores, lo que hace que la estimación de $f$ por parte del modelo flexible sea más estable y precisa.

### b) $p$ extremadamente grande, $n$ pequeño

Respuesta: no flexibe 

Justificación: 
En este escenario, es mejor utilizar un método no flexible. El pequeño $n$ eleva el riesgo de sobreajuste (overfitting), mientras que el gran $p$ causa la "maldición de la dimensionalidad", dispersando los pocos datos en un espacio de características enorme. Un modelo flexible (de baja sesgo) tendría una varianza altísima al intentar ajustarse al ruido en este espacio disperso. Por el contrario, un método inflexible (de alto sesgo) impone una estructura simple que controla la varianza, lo cual es esencial para prevenir el sobreajuste en esta situación.

### c) La relación entre predictores y variable dependiente es altamente no lineal

Respuesta: flexibe

Justificación: Se necesita un método flexible, sino, es probable que no se pueda capturar la "forma" de la función f. 


### d) La varianza de los términos de error, $\sigma^2 = \text{Var}(\epsilon)$, es extremadamente alta

Respuesta: no flexible

Justificación:
Cuando $\sigma^2$ (la varianza del error) es extremadamente alta, los datos están muy "ruidosos". Esto significa que las observaciones $Y$ están muy dispersas y lejos de la verdadera función $f(X)$.

---

## 2. Clasificación vs. Regresión e Inferencia vs. Predicción

### a) Salario de Directores Ejecutivos

* Inferencia: qué factores afectan al salario
* Regresión: qué salario tienen los directores ejecutivos 
* n = 500 empresas
* p = ganancias, número de empleados, industria (3) 



### b) Éxito o Fracaso de Nuevo Producto

* Clasificación: exitoso o no exitoso
* Predicción: si el producto es exitoso o no
* $n$:20
* $p$:13


### c) Predicción del Tipo de Cambio USD/Euro

* Regresión: Se quiere conocer el porcentaje de cambio 
* Predicción: Se quiere predecir el porcentaje de cambio 
* n= 52
* p= 3


---

## 3. Ventajas y Desventajas de la Flexibilidad

### Ventajas de un enfoque flexible (vs. inflexible)

* Ventajas: Tienen un bajo sesgo, pueden modelar relación muy complejas. Si la función f es complicada pueden aproximarla con precisión. 

### Desventajas de un enfoque flexible (vs. inflexible)

* Desventajas: Si el conjunto de datos n es muy pequeño se corre el riesgo de un "sobreajuste": el modelo memoriza todos los datos. 

### Ventajas de un enfoque no flexible
* Ideal cuando se tiene un n pequeño, y un p pequeño 
* Los datos de entrenamiento no afectan tanto el modelo final


### Desventajas de un enfoque no flexible

* Tienen un sesgo muy alto: hacen suposiciones fuertes sobre la forma de f


### Cuando se prefiere un enfoque flexible ( o inflexible)

Flexible
* Se prefieren cuando la predicción es lo que importa. 
* Cuando f es no es lineal 
* Cuando n es grande y p pequeño 

Inflexible 
* El objetivo es la inferencia 
* n es pequeño y p grande 

## 4. Enfoques Paramétricos vs. No Paramétricos

### Enfoque Paramétrico
- Reduce el problema de estimar \( f \) a estimar un conjunto de parámetros.  
- Asume una forma específica para \( f \) (por ejemplo, \( f(X) = \beta_0 + \beta_1X_1 \)).  
- Usa los datos de entrenamiento para ajustar los parámetros.

**Ventajas:**
- Simple y fácil de interpretar.  
- Baja varianza: menos propenso al sobreajuste.  
- Eficiente: requiere menos datos.  

**Desventajas:**
- Alto sesgo: si la forma asumida es incorrecta, el modelo no se ajusta bien.

### Enfoque No Paramétrico
- No asume una forma para \( f \); los datos determinan su estructura.  
- Busca una función que se ajuste lo mejor posible a los datos.  

**Ventajas:**
- Bajo sesgo: puede adaptarse a funciones complejas.  
- Flexible y potencialmente más preciso.  

**Desventajas:**
- Alta varianza: propenso al sobreajuste si hay pocos datos.  
- Requiere un conjunto de datos grande.  
- Menor interpretabilidad.


---

## 5. K Vecinos Más Cercanos (KNN) para Clasificación

Punto de prueba: $X_1 = 0, X_2 = 0, X_3 = 0$.

### a) Distancia Euclidiana

| Obs. | X1 | X2 | X3 | Y     | Cálculo                             | Distancia |
| ---- | -- | -- | -- | ----- | ----------------------------------- | --------- |
| 1    | 0  | 3  | 0  | Rojo  | √((0−0)² + (3−0)² + (0−0)²) = √(9)  | **3.00**  |
| 2    | 2  | 0  | 0  | Rojo  | √((2−0)² + (0−0)² + (0−0)²) = √(4)  | **2.00**  |
| 3    | 0  | 1  | 3  | Rojo  | √((0−0)² + (1−0)² + (3−0)²) = √(10) | **3.16**  |
| 4    | 0  | 1  | 2  | Verde | √((0−0)² + (1−0)² + (2−0)²) = √(5)  | **2.24**  |
| 5    | -1 | 0  | 1  | Verde | √((−1−0)² + (0−0)² + (1−0)²) = √(2) | **1.41**  |
| 6    | 1  | 1  | 1  | Rojo  | √((1−0)² + (1−0)² + (1−0)²) = √(3)  | **1.73**  |



### b) Predicción con $K = 1$

* Predicción: verde
* Justificación: Tomamos el vecino más cercano es el 5, con una distancia de 1.41


### c) Predicción con $K = 3$

* Predicción: rojo
* Justificación: Tomamos los 3 vecinos más cercanos, 5,6,2. Por mayoría ganan 6 y 2, cuyo color corresopndiente es el rojo

### d) Valor de $K$ si el límite de decisión de Bayes es altamente no lineal

* Valor esperado de $K$: k pequeño
* Razón: Un K pequeño produce un clasificador de alta flexibilidad (bajo sesgo), que es necesario para aproximar con precisión una frontera de decisión de Bayes que es, por definición, altamente compleja y no lineal.