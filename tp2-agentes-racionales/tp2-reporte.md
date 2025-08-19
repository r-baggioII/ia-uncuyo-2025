# Reporte de Experimentos: Evaluación de Agentes de Limpieza

## 1. Introducción

Este reporte presenta los resultados de experimentos realizados para evaluar el desempeño de diferentes tipos de agentes de limpieza en entornos con distintas características. El objetivo principal es comparar la eficiencia de dos estrategias de comportamiento: un agente simple reflexivo y un agente completamente aleatorio.

## 2. Descripción del Entorno

### 2.1 Características del Entorno

El entorno de simulación consiste en una grilla cuadrada de dimensiones variables donde:

- **Celdas**: Cada celda puede estar limpia o sucia
- **Agente**: Se ubica en una posición específica y puede realizar acciones
- **Estado inicial**: El agente comienza en una posición aleatoria y algunas celdas contienen suciedad según el porcentaje especificado

### 2.2 Acciones Disponibles

El agente puede realizar las siguientes acciones:
- **Limpiar**: Limpia la celda actual si está sucia
- **Moverse**: Se desplaza a una celda adyacente (arriba, abajo, izquierda, derecha)
- **No hacer nada**: Permanece en la posición actual sin realizar acción

### 2.3 Medidas de Rendimiento

Para evaluar el desempeño de los agentes se utilizaron dos métricas principales:
1. **Cantidad de celdas limpiadas**: Número total de celdas que el agente logró limpiar
2. **Unidades de tiempo consumidas**: Número total de acciones realizadas por el agente

## 3. Tipos de Agentes Evaluados

### 3.1 Agente Simple (Reflexivo)

**Estrategia de comportamiento:**
- Si la celda actual está sucia → **Limpia** la celda
- Si la celda actual está limpia → Se **mueve aleatoriamente** a una celda adyacente

Este agente implementa una lógica básica de reacción ante el estado del entorno, priorizando la limpieza cuando detecta suciedad.

### 3.2 Agente Aleatorio (Random)

**Estrategia de comportamiento:**
- En cada paso de tiempo → Selecciona una **acción completamente aleatoria** de entre todas las acciones disponibles

Este agente no considera el estado del entorno y sirve como línea base para comparar el rendimiento del agente reflexivo.

## 4. Diseño Experimental

### 4.1 Parámetros del Experimento

**Tamaños de entorno evaluados:**
- 2 × 2 (4 celdas)
- 4 × 4 (16 celdas)
- 8 × 8 (64 celdas)
- 16 × 16 (256 celdas)
- 32 × 32 (1,024 celdas)
- 64 × 64 (4,096 celdas)
- 128 × 128 (16,384 celdas)

**Porcentajes de suciedad:**
- 0.1 (10% de celdas sucias)
- 0.2 (20% de celdas sucias)
- 0.4 (40% de celdas sucias)
- 0.8 (80% de celdas sucias)

**Repeticiones:**
- 10 ejecuciones por cada combinación de parámetros
- Total de combinaciones: 7 tamaños × 4 porcentajes = 28 configuraciones
- Total de ejecuciones por agente: 28 × 10 = 280 experimentos

### 4.2 Control de Variables

Para garantizar la reproducibilidad y comparabilidad de los experimentos:
- **Seed fijo**: Se utilizó `--seed 12345` para todas las ejecuciones
- **Mismas condiciones iniciales**: Cada par de experimentos (simple vs aleatorio) se ejecutó bajo las mismas condiciones de entorno
- **Tiempo de ejecución**: Se permitió que cada agente ejecute hasta completar su tarea o alcanzar una cierta cantidad de pasos (1000 pasos para estos experimentos)

### 4.3 Procedimiento Experimental

1. **Configuración del entorno**: Se genera una grilla del tamaño especificado con el porcentaje de suciedad correspondiente
2. **Inicialización del agente**: Se coloca el agente en una posición inicial aleatoria
3. **Ejecución**: El agente ejecuta acciones según su estrategia hasta completar la tarea
4. **Registro de datos**: Se almacenan la información de la ejecución en un archivo json 
5. **Repetición**: Se repite el proceso 10 veces para cada configuración

## 5. Recolección y Análisis de Datos

### 5.1 Estructura de Datos

Los resultados se almacenan en formato JSON y CSV con la siguiente estructura:
- **size**: Tamaño del entorno (N×N)
- **dirt_rate**: Porcentaje de suciedad (0.1-0.8)
- **repetition**: Número de repetición (1-10)
- **cleaned_cells**: Cantidad de celdas limpiadas
- **actions_taken**: Número de acciones realizadas


## 6. Implementación Técnica

### 6.1 Herramientas Utilizadas

- **Lenguaje**: Python 3
- **Ejecución**: Scripts automatizados con `subprocess`
- **Almacenamiento**: Archivos JSON y CSV
- **Análisis**: Estadísticas descriptivas con `statistics`

## 8. Resultados de los Experimentos y conclusiones

**Conclusiones principales**

La diferencia en la capacidad de los agentes para limpiar eficazmente a medida que el entorno crece es el punto más importante.

Dominio del Agente Simple: En absolutamente todas las combinaciones de tamaño y suciedad, el Agente Simple limpia un porcentaje igual o (en la mayoría de los casos) significativamente mayor que el Agente Random.

Rango Efectivo:

El Agente Simple es 100% efectivo hasta entornos de 8x8, y mantiene un rendimiento bueno (superior al 70%) en 16x16.

El Agente Random solo es 100% efectivo hasta 4x4. Su rendimiento se desploma a partir de 8x8, volviéndose muy pobre en 16x16 (apenas un 22-31%).

Degradación del Rendimiento: Aunque ambos agentes fallan en entornos muy grandes (32x32 en adelante), el rendimiento del Agente Simple se degrada de manera mucho más controlada. En el entorno de 32x32, por ejemplo, el Agente Simple limpia casi el triple (24%) que el Agente Random (~8-9%).

Basado en el análisis de los gráficos, el Agente Simple es consistentemente superior al Agente Random en todos los aspectos medibles. Aunque ambos agentes fallan en entornos grandes, el Agente Simple logra sus objetivos de limpieza de manera mucho más eficiente (con menos pasos).