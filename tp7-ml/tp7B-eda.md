# TP7B - EDA

Este documento resume el EDA solicitado (preguntas 2a-2c) y contiene las figuras generadas.

## 2a) ¿En qué secciones hay más árboles con inclinación peligrosa?

Ver figura: `peligrosidad_por_seccion.png` (ya incluida en el repositorio). Esta gráfica muestra el conteo de árboles con `inclinacion_peligrosa == 1` por `nombre_seccion`.

![peligrosidad_por_seccion](peligrosidad_por_seccion.png)

Observación: las secciones con mayores conteos pueden indicar zonas con necesidad de inspección.

## 2b) ¿Qué especies son las más afectadas por la inclinación peligrosa?

Ver figura: `pligrosidad_especie.png` (barras por especie mostrando proporción / conteo de inclinación peligrosa).

![peligrosidad_por_especie](pligrosidad_especie.png)

Observación: algunas especies muestran mayor proporción de inclinaciones peligrosas; conviene filtrar por abundancia para no sobre-interpretar especies escasas.

## 2c) Histograma de circunferencia segmentado por `inclinacion_peligrosa`

Se incluyen los histogramas y variantes:

- `circunferencia_30.png` — histograma con bins pequeñas
- `circunferencia_100_bins.png` — histograma con 100 bins
- `circ_peligrosidad.png` — densidad por clase

![circunferencia_30](circunferencia_30.png)

![circunferencia_100_bins](circunferencia_100_bins.png)

![circ_peligrosidad](circ_peligrosidad.png)

La variable `circ_tronco_cm` también fue categorizada en 4 niveles (`bajo`, `medio`, `alto`, `muy alto`) y se guardó en el archivo de entrenamiento: `data/arbolado-mendoza-dataset-circ_tronco_cm-train.csv`.


**Notas sobre reproducibilidad**

- Los CSV principales se encuentran en `data/`.
- Para reproducir las figuras, ejecutar el script R en `code/eda-clasif-cv/eda_clasif_cv.R` y adaptar los snippets de plotting según librerías de preferencia.
