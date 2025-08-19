# Preguntas AIMA IA

## 2.10 Entorno con penalización por movimiento

**a. Agente reactivo simple**

No, aún si es penalizado por cada movimiento no mejorará su desempeño. Esto se debe a la naturaleza del agente reflexivo simple, que carece de memoria. Simplemente realiza acciones en base a su entorno local.

**b. Agente reactivo con estado**

Sí, puede ser racional. Si el agente posee memoria, entonces conoce exactamente qué celdas ha limpiado. Por lo que se moverá únicamente hacia aquellas celdas que considere desconocidas y que estén potencialmente sucias.

El agente funcionaría de la siguiente manera:

* Estado interno: posición, creencias limpio/sucio de cada celda (o “desconocido”).
* Reglas:

  * Si la celda actual está sucia, entonces el agente debe limpiar.
  * Si hay celdas sucias en la creencia ⇒ moverse por camino más corto a la más cercana.
  * Si no hay sucias pero hay desconocidas ⇒ explorar la más cercana.
  * Si todo limpio y nada desconocido ⇒ no hacer nada.

**c. Cambios si el agente tiene percepto global**

Para el reflexivo simple sin estado puede ser perfectamente racional, ya que posee un entorno totalmente observable y puede saber exactamente qué celdas le quedan por limpiar.

En el caso del reflexivo con estado y conocimiento total de su entorno también puede ser racional. Con percepto global, el agente reactivo simple puede ser racional porque “ve” todo el estado en cada paso (no necesita memoria). El agente con estado también puede ser racional, aunque la memoria se vuelve redundante, ya que el percepto le da toda la información que antes almacenaba.

## 2.11 Entorno desconocido con obstáculos y suciedad inicial aleatoria

**a. Agente reactivo simple**

No, un agente reactivo simple no puede ser perfectamente racional en este entorno. Al no tener memoria, desconoce qué celdas ya ha limpiado. Además, al desconocer la ubicación de los obstáculos y los límites, no puede planificar movimientos eficientes, lo que reduce su desempeño.

**b. Agente reactivo simple aleatorizado**

Sí, puede. Un agente aleatorizado elige movimientos al azar entre las opciones disponibles cuando la celda está limpia, lo que le permite explorar más eficientemente que un patrón fijo y, en algunos entornos, mejorar su desempeño.

**c. Entorno donde el agente aleatorizado tiene mal desempeño**

Sí, si el entorno es suficientemente grande, entonces el desempeño del agente empeorará. Sin embargo, el dirt-rate no afecta en gran medida al desempeño del mismo.

**d. Agente reactivo con estado**

Sí, el agente reactivo con estado puede superar el desempeño del agente reactivo simple común. Esto es porque al tener memoria, puede optimizar la limpieza, evitando pasar por celdas que ya ha limpiado y minimizar la cantidad de movimientos.
