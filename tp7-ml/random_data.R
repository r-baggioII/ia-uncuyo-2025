install.packages("tidyverse")

# Cargar las librerías necesarias
library(tidyverse)
library(scales) # Para etiquetas de porcentaje en los gráficos

# ---
# Tarea 1: División del dataset
# ---

# Establecer una semilla de aleatoriedad para que la división sea reproducible
set.seed(123)

# 1. Bajar (cargar) el archivo
# Asegúrate de que el archivo "arbolado-mendoza-dataset.csv" esté 
# en tu directorio de trabajo (Working Directory).
tryCatch({
  df_completo <- read_csv("arbolado-mendoza-dataset.csv")
  
  # 1a. y 1b. Crear conjuntos de validación (20%) y entrenamiento (80%)
  
  # Obtenemos los índices para el conjunto de validación de forma aleatoria
  total_filas <- nrow(df_completo)
  tamaño_val <- floor(0.20 * total_filas)
  
  indices_val <- sample(seq_len(total_filas), size = tamaño_val)
  
  # Creamos los dataframes
  df_val <- df_completo[indices_val, ]
  df_train <- df_completo[-indices_val, ]
  
  # 1a. Guardar el archivo de validación
  write_csv(df_val, "arbolado-mendoza-dataset-validation.csv")
  
  # 1b. Guardar el archivo de entrenamiento
  write_csv(df_train, "arbolado-mendoza-dataset-train.csv")
  
  print("Archivos 'arbolado-mendoza-dataset-validation.csv' y 'arbolado-mendoza-dataset-train.csv' creados con éxito.")
  print(paste("Filas entrenamiento:", nrow(df_train)))
  print(paste("Filas validación:", nrow(df_val)))
  
  
  # ---
  # Tarea 2: Análisis del dataset de Entrenamiento (df_train)
  # ---
  
  # 2a) Distribución de la clase inclinacion_peligrosa
  print("Generando gráfico 2a: Distribución de 'inclinacion_peligrosa'")
  
  # Suponemos que 'inclinacion_peligrosa' es una variable lógica (TRUE/FALSE) o (0/1).
  # ggplot2 la tratará como categórica.
  
  g_2a <- ggplot(df_train, aes(x = factor(inclinacion_peligrosa))) +
    geom_bar(aes(fill = factor(inclinacion_peligrosa)), show.legend = FALSE) +
    geom_text(stat = 'count', aes(label = ..count..), vjust = -0.5) +
    labs(title = "Distribución de la clase 'inclinacion_peligrosa'",
         x = "Inclinación Peligrosa",
         y = "Conteo Total") +
    theme_minimal()
  
  # Para ver el gráfico en RStudio, simplemente escribe el nombre de la variable
  print(g_2a)
  # ggsave("grafico_2a_distribucion.png", g_2a) # Opcional: guardarlo
  
  # Respuesta 2a:
  # El gráfico de barras muestra el conteo absoluto de árboles 
  # considerados peligrosos vs. no peligrosos en el conjunto de entrenamiento.
  
  
  # 2b) ¿Se puede considerar alguna sección más peligrosa que otra?
  print("Generando gráfico 2b: Peligrosidad por Sección")
  
  # Usamos un gráfico de barras apiladas al 100% (position = "fill")
  # para ver la *proporción* de peligrosidad, independientemente 
  # del número total de árboles en cada sección.
  
  g_2b <- df_train %>%
    filter(!is.na(seccion)) %>% # Filtramos NAs si existen
    ggplot(aes(x = factor(seccion), fill = factor(inclinacion_peligrosa))) +
    geom_bar(position = "fill") +
    scale_y_continuous(labels = scales::percent) +
    labs(title = "Proporción de Peligrosidad por Sección",
         x = "Sección",
         y = "Proporción de Árboles",
         fill = "Inclinación Peligrosa") +
    theme_minimal()
  
  print(g_2b)
  # ggsave("grafico_2b_seccion.png", g_2b)
  
  # Respuesta 2b:
  # Sí, se puede. El gráfico muestra la proporción de árboles peligrosos
  # (barra de color rojo/TRUE) vs. no peligrosos (barra azul/FALSE) 
  # para cada sección. Si una barra de sección tiene una porción roja 
  # visiblemente más grande que otras, esa sección es proporcionalmente 
  # más peligrosa.
  
  
  # 2c) ¿Se puede considerar alguna especie más peligrosa que otra?
  print("Generando gráfico 2c: Peligrosidad por Especie (Top 15 más comunes)")
  
  # El problema es que puede haber muchas especies.
  # Filtremos primero por las 15 especies más comunes para un gráfico legible.
  
  top_especies <- df_train %>%
    count(especie, sort = TRUE) %>%
    top_n(15, n) %>%
    pull(especie)
  
  g_2c <- df_train %>%
    filter(especie %in% top_especies) %>%
    ggplot(aes(x = fct_reorder(especie, inclinacion_peligrosa, .fun = mean), 
               fill = factor(inclinacion_peligrosa))) +
    geom_bar(position = "fill") +
    coord_flip() + # Giramos los ejes para mejor legibilidad de las especies
    scale_y_continuous(labels = scales::percent) +
    labs(title = "Proporción de Peligrosidad (Top 15 Especies más Comunes)",
         x = "Especie",
         y = "Proporción de Árboles",
         fill = "Inclinación Peligrosa") +
    theme_minimal()
  
  print(g_2c)
  # ggsave("grafico_2c_especie.png", g_2c)
  
  # Respuesta 2c:
  # Sí. Al igual que con la sección, el gráfico de barras apiladas 
  # (ordenado por peligrosidad) muestra que, entre las especies más comunes,
  # algunas tienen una proporción de 'inclinacion_peligrosa = TRUE'
  # mucho mayor que otras.
  
  
  # ---
  # Tarea 3: Análisis de 'circ_tronco_cm'
  # ---
  
  # 3a) Histograma de frecuencia para circ_tronco_cm
  print("Generando gráfico 3a: Histograma de 'circ_tronco_cm'")
  
  # Probar con diferentes bins
  # Opción 1: 30 bins
  g_3a_bins30 <- ggplot(df_train, aes(x = circ_tronco_cm)) +
    geom_histogram(bins = 30, fill = "steelblue", color = "white") +
    labs(title = "Histograma de Circunferencia de Tronco (30 bins)",
         x = "Circunferencia (cm)", y = "Frecuencia") +
    theme_minimal()
  
  print(g_3a_bins30)
  
  # Opción 2: 100 bins (para más detalle)
  g_3a_bins100 <- ggplot(df_train, aes(x = circ_tronco_cm)) +
    geom_histogram(bins = 100, fill = "darkgreen", color = "white") +
    labs(title = "Histograma de Circunferencia de Tronco (100 bins)",
         x = "Circunferencia (cm)", y = "Frecuencia") +
    theme_minimal()
  
  print(g_3a_bins100)
  
  
  # 3b) Repetir (3a) separando por inclinacion_peligrosa
  print("Generando gráfico 3b: Histograma de 'circ_tronco_cm' por Peligrosidad")
  
  # Usamos facet_wrap para separar los gráficos
  g_3b <- ggplot(df_train, aes(x = circ_tronco_cm, fill = factor(inclinacion_peligrosa))) +
    geom_histogram(bins = 60, color = "white", show.legend = FALSE) +
    facet_wrap(~ inclinacion_peligrosa, ncol = 1, scales = "free_y") +
    labs(title = "Histograma de Circunferencia por Peligrosidad",
         x = "Circunferencia (cm)", y = "Frecuencia") +
    theme_minimal()
  
  print(g_3b)
  
  # (Opcional) Un gráfico de densidad es útil para comparar distribuciones
  g_3b_densidad <- ggplot(df_train, aes(x = circ_tronco_cm, fill = factor(inclinacion_peligrosa))) +
    geom_density(alpha = 0.6) +
    labs(title = "Densidad de Circunferencia por Peligrosidad",
         x = "Circunferencia (cm)", y = "Densidad",
         fill = "Inclinación Peligrosa") +
    theme_minimal()
  
  print(g_3b_densidad)
  
  
  # 3c) Crear nueva variable categórica 'circ_tronco_cm_cat'
  
  # Para seleccionar los puntos de corte, usamos la información de (3a).
  # Lo más estándar es usar los cuartiles (que definen 4 grupos de igual tamaño).
  
  # Obtenemos los cuartiles de la variable
  cortes <- quantile(df_train$circ_tronco_cm, 
                     probs = c(0, 0.25, 0.5, 0.75, 1), 
                     na.rm = TRUE)
  
  print("Puntos de corte (cuartiles) para 'circ_tronco_cm':")
  print(cortes)
  
  # Definimos las etiquetas
  etiquetas <- c("bajo", "medio", "alto", "muy alto")
  
  # Creamos la nueva variable usando 'cut'
  df_train_nuevo <- df_train %>%
    mutate(
      circ_tronco_cm_cat = cut(
        circ_tronco_cm,
        breaks = cortes,
        labels = etiquetas,
        include.lowest = TRUE # Incluye el valor mínimo en la primera categoría
      )
    )
  
  # Verificamos la creación de la nueva variable
  print("Verificación de la nueva variable 'circ_tronco_cm_cat':")
  print(table(df_train_nuevo$circ_tronco_cm_cat))
  
  # 3d. Guardar el nuevo dataframe
  write_csv(df_train_nuevo, "arbolado-mendoza-dataset-circ_tronco_cm-train.csv")
  
  print("DataFrame con la nueva variable categórica guardado con éxito.")
  
}, error = function(e) {
  print(paste("Error al procesar el archivo:", e$message))
  print("Verifica que el archivo 'arbolado-mendoza-dataset.csv' se encuentre en tu directorio de trabajo.")
  print("Puedes verificar tu directorio actual con el comando getwd()")
})